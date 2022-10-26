"""initial

Revision ID: a51c0998baff
Revises: 
Create Date: 2022-10-27 01:52:27.067384

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime
# revision identifiers, used by Alembic.
revision = 'a51c0998baff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("create schema content")

    op.create_table(
        'movies',
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column("created_at", sa.DateTime(timezone=False), default=sa.sql.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=False), default=sa.sql.func.now(), onupdate=datetime.utcnow),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='content'
    )
    op.create_table(
        'original_media',
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column("created_at", sa.DateTime(timezone=False), default=sa.sql.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=False), default=sa.sql.func.now(), onupdate=datetime.utcnow),
        sa.Column('bucket', sa.String(length=128), nullable=False),
        sa.Column('filepath', sa.String(length=128), nullable=False),
        sa.Column('duration', sa.Numeric(precision=14, scale=7), nullable=False),
        sa.Column('size', sa.String(length=64), nullable=True),
        sa.Column('format', sa.String(length=64), nullable=True),
        sa.Column('acodec', sa.String(length=64), nullable=True),
        sa.Column('vcodec', sa.String(length=64), nullable=True),
        sa.Column('movies_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['movies_id'], ['content.movies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('filepath'),
    schema='content'
    )
    op.create_table(
        'convert_media',
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column("created_at", sa.DateTime(timezone=False), default=sa.sql.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=False), default=sa.sql.func.now(), onupdate=datetime.utcnow),
        sa.Column('bucket', sa.String(length=128), nullable=False),
        sa.Column('filepath', sa.String(length=128), nullable=False),
        sa.Column('duration', sa.Numeric(precision=14, scale=7), nullable=False),
        sa.Column('size', sa.String(length=64), nullable=True),
        sa.Column('format', sa.String(length=64), nullable=True),
        sa.Column('acodec', sa.String(length=64), nullable=True),
        sa.Column('vcodec', sa.String(length=64), nullable=True),
        sa.Column('hash_convert', sa.String(length=128), nullable=False),
        sa.Column('movies_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('original_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['movies_id'], ['content.movies.id'], ),
        sa.ForeignKeyConstraint(['original_id'], ['content.original_media.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('filepath'),
        schema='content'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('convert_media', schema='content')
    op.drop_table('original_media', schema='content')
    op.drop_table('movies', schema='content')
    # ### end Alembic commands ###
