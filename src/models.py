import enum
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import declarative_mixin, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from datetime import datetime
from schemas import ConvertSchema
from prefect import get_run_logger
from schemas import MediaInfoSchema


class ObjectDoesNotExistError(Exception):
    """Raise it if object does not exist in database."""


class ObjectAlreadyExistError(Exception):
    """Raise it if object already exist in database."""

@declarative_mixin
class TimestampMixin:

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = sa.Column(
        sa.DateTime(timezone=False), default=lambda: datetime.utcnow()
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=False),
        default=lambda: datetime.utcnow(),
        onupdate=datetime.utcnow,
    )


@declarative_mixin
class BaseMediaMixin:

    bucket = sa.Column(sa.String(length=128), nullable=False, unique=False)
    filepath = sa.Column(sa.String(length=128), nullable=False, unique=True)
    duration = sa.Column(
        sa.Numeric(14, 7), sa.CheckConstraint("duration>0"), nullable=False
    )
    size = sa.Column(sa.String(length=64), nullable=True, unique=False)
    format = sa.Column(sa.String(length=64), nullable=True, unique=False)
    acodec = sa.Column(sa.String(length=64), nullable=True, unique=False)
    vcodec = sa.Column(sa.String(length=64), nullable=True, unique=False)


class MoviesModel(Base, TimestampMixin):

    __tablename__ = "movies"

    name = sa.Column(sa.String(length=128), nullable=False, unique=False)


class MediaOriginalModel(Base, TimestampMixin, BaseMediaMixin):

    __tablename__ = "original_media"

    movies_id = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey('content.movies.id')
    )
    movies = relationship("MoviesModel", foreign_keys=[movies_id])

    @classmethod
    async def _get_obj(cls, db_session, stmt: sa.sql.Select):
        result = await db_session.execute(stmt)
        obj = result.scalar()
        if not obj:
            raise ObjectDoesNotExistError
        return obj

    @classmethod
    async def get_original_not_have_convert_schema(
            cls,
            db_session: AsyncSession,
            convert_schema: ConvertSchema
    ):
        logger = get_run_logger()
        hash_convert = convert_schema.get_hash()
        subquery = sa.select(MediaConvertModel.original_id).filter(
            MediaConvertModel.hash_convert == hash_convert)
        query = sa.select(
            MediaOriginalModel).where(MediaOriginalModel.id.notin_(subquery))
        try:
            result = await db_session.execute(query)
            return result.scalars().all()
        except Exception as error:
            logger.error(f'DB Error {error}')

    def as_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in sa.inspect(self).mapper.column_attrs
        }


class MediaConvertModel(Base, TimestampMixin, BaseMediaMixin):

    __tablename__ = "convert_media"


    hash_convert = sa.Column(
        sa.String(length=128), nullable=False, unique=False
    )

    movies_id = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey('content.movies.id')
    )
    movies = relationship("MoviesModel", foreign_keys=[movies_id])

    original_id = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey('content.original_media.id')
    )
    media_original = relationship(
        "MediaOriginalModel", foreign_keys=[original_id]
    )

    @classmethod
    async def _get_obj(cls, db_session, stmt: sa.sql.Select):
        result = await db_session.execute(stmt)
        obj = result.scalar()
        if not obj:
            raise ObjectDoesNotExistError
        return obj

    @classmethod
    async def add_info(
            cls,
            db_session: AsyncSession,
            filepath: str,
            bucket: str,
            hash_convert: str,
            movies_id: str,
            original_id: str,
            media_info: MediaInfoSchema,
    ):
        media_convert = MediaConvertModel(
            filepath=filepath,
            bucket=bucket,
            movies_id=movies_id,
            original_id=original_id,
            hash_convert=hash_convert,
            **media_info.dict()
        )
        db_session.add(media_convert)
        try:
            await db_session.commit()
        except sa.exc.IntegrityError:
            raise ObjectAlreadyExistError
        await db_session.refresh(media_convert)

    def as_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in sa.inspect(self).mapper.column_attrs
        }
