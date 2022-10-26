import uuid
import sqlalchemy as sa
from sqlalchemy.orm import declarative_mixin, relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from datetime import datetime


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

    def as_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in sa.inspect(self).mapper.column_attrs
        }
