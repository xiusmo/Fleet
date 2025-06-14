"""init

Revision ID: 45960ae8201c
Revises: 
Create Date: 2025-04-18 13:33:03.510188

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel, Field
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '45960ae8201c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('announcements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('summary', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('content', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('status', sa.Enum('draft', 'published', 'scheduled', 'archived', 'advertisement', name='announcementstatus'), nullable=False),
    sa.Column('is_pinned', sa.Boolean(), nullable=False),
    sa.Column('publish_date', sa.DateTime(), nullable=True),
    sa.Column('cover_image', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_announcements_title'), 'announcements', ['title'], unique=False)
    op.create_index(op.f('ix_announcements_uuid'), 'announcements', ['uuid'], unique=True)
    op.create_table('logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('level', sa.Enum('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', name='loglevel'), nullable=False),
    sa.Column('category', sa.Enum('SYSTEM', 'TASK', 'WORKER', 'USER', 'API', 'SECURITY', 'PUSH', 'SCHEDULER', 'OTHER', name='logcategory'), nullable=False),
    sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('worker_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_logs_task_id'), 'logs', ['task_id'], unique=False)
    op.create_index(op.f('ix_logs_user_id'), 'logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_logs_worker_id'), 'logs', ['worker_id'], unique=False)
    op.create_table('sign_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.String(length=50), nullable=True),
    sa.Column('course_id', sa.String(length=50), nullable=True),
    sa.Column('course_name', sa.String(length=50), nullable=True),
    sa.Column('class_id', sa.String(length=50), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('other_id', sa.Integer(), nullable=True),
    sa.Column('sign_type', sa.String(length=20), nullable=True),
    sa.Column('teacher_name', sa.String(length=50), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('sign_out_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('time_long', sa.Integer(), nullable=True),
    sa.Column('sign_out_time_long', sa.Integer(), nullable=True),
    sa.Column('manual', sa.Boolean(), nullable=True),
    sa.Column('total_users', sa.Integer(), nullable=True),
    sa.Column('signed_users', sa.Integer(), nullable=True),
    sa.Column('sign_percent', sa.Float(), nullable=True),
    sa.Column('need_photo', sa.Boolean(), nullable=True),
    sa.Column('need_location', sa.Boolean(), nullable=True),
    sa.Column('location_range', sa.Float(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('need_code', sa.Boolean(), nullable=True),
    sa.Column('sign_code', sa.String(length=20), nullable=True),
    sa.Column('need_sign_out', sa.Boolean(), nullable=True),
    sa.Column('need_captcha', sa.Boolean(), nullable=True),
    sa.Column('captcha_type', sa.String(length=20), nullable=True),
    sa.Column('need_face', sa.Boolean(), nullable=True),
    sa.Column('attend_update_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sign_activities_activity_id'), 'sign_activities', ['activity_id'], unique=True)
    op.create_index(op.f('ix_sign_activities_class_id'), 'sign_activities', ['class_id'], unique=False)
    op.create_index(op.f('ix_sign_activities_course_id'), 'sign_activities', ['course_id'], unique=False)
    op.create_index(op.f('ix_sign_activities_id'), 'sign_activities', ['id'], unique=False)
    op.create_table('workers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('endpoint', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('status', sa.Enum('ONLINE', 'OFFLINE', 'BUSY', 'ERROR', name='workerstatus'), nullable=False),
    sa.Column('last_heartbeat', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('capabilities', sa.JSON(), nullable=True),
    sa.Column('subdomain', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subdomain')
    )
    op.create_index(op.f('ix_workers_name'), 'workers', ['name'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('tel', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('cx_d', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('cx_uf', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('cx_vc3', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('cx_uid', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('im_username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('im_password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('monitor_status', sa.Boolean(), nullable=False),
    sa.Column('person_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('school_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('fid', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('worker_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['worker_name'], ['workers.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_tel'), 'users', ['tel'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('sign_configs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=True),
    sa.Column('course_id', sa.String(length=50), nullable=True),
    sa.Column('class_id', sa.String(length=50), nullable=True),
    sa.Column('location_text', sa.String(length=255), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('use_random_position', sa.Boolean(), nullable=True),
    sa.Column('position_offset', sa.Float(), nullable=True),
    sa.Column('photo_path', sa.String(length=255), nullable=True),
    sa.Column('use_random_photo', sa.Boolean(), nullable=True),
    sa.Column('custom_headers', sa.JSON(), nullable=True),
    sa.Column('custom_data', sa.JSON(), nullable=True),
    sa.Column('trigger_type', sa.String(length=20), nullable=True),
    sa.Column('threshold_count', sa.Integer(), nullable=True),
    sa.Column('threshold_percent', sa.Float(), nullable=True),
    sa.Column('threshold_time', sa.Integer(), nullable=True),
    sa.Column('poll_interval', sa.Integer(), nullable=True),
    sa.Column('sign_delay', sa.Integer(), nullable=True),
    sa.Column('random_delay', sa.Integer(), nullable=True),
    sa.Column('monitor_interval', sa.Integer(), nullable=True),
    sa.Column('notify_on_detect', sa.Boolean(), nullable=True),
    sa.Column('notify_on_sign', sa.Boolean(), nullable=True),
    sa.Column('ios_bark_key', sa.String(length=255), nullable=True),
    sa.Column('android_ntfy_key', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_sign_configs_course_id'), 'sign_configs', ['course_id'], unique=False)
    op.create_index(op.f('ix_sign_configs_id'), 'sign_configs', ['id'], unique=False)
    op.create_table('user_activity_detections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.String(length=50), nullable=False),
    sa.Column('course_name', sa.String(length=100), nullable=True),
    sa.Column('teacher_name', sa.String(length=100), nullable=True),
    sa.Column('uuid_expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('message', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['sign_activities.activity_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_user_activity_detections_activity_id'), 'user_activity_detections', ['activity_id'], unique=False)
    op.create_index(op.f('ix_user_activity_detections_id'), 'user_activity_detections', ['id'], unique=False)
    op.create_index(op.f('ix_user_activity_detections_user_id'), 'user_activity_detections', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_activity_detections_user_id'), table_name='user_activity_detections')
    op.drop_index(op.f('ix_user_activity_detections_id'), table_name='user_activity_detections')
    op.drop_index(op.f('ix_user_activity_detections_activity_id'), table_name='user_activity_detections')
    op.drop_table('user_activity_detections')
    op.drop_index(op.f('ix_sign_configs_id'), table_name='sign_configs')
    op.drop_index(op.f('ix_sign_configs_course_id'), table_name='sign_configs')
    op.drop_table('sign_configs')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_tel'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_workers_name'), table_name='workers')
    op.drop_table('workers')
    op.drop_index(op.f('ix_sign_activities_id'), table_name='sign_activities')
    op.drop_index(op.f('ix_sign_activities_course_id'), table_name='sign_activities')
    op.drop_index(op.f('ix_sign_activities_class_id'), table_name='sign_activities')
    op.drop_index(op.f('ix_sign_activities_activity_id'), table_name='sign_activities')
    op.drop_table('sign_activities')
    op.drop_index(op.f('ix_logs_worker_id'), table_name='logs')
    op.drop_index(op.f('ix_logs_user_id'), table_name='logs')
    op.drop_index(op.f('ix_logs_task_id'), table_name='logs')
    op.drop_table('logs')
    op.drop_index(op.f('ix_announcements_uuid'), table_name='announcements')
    op.drop_index(op.f('ix_announcements_title'), table_name='announcements')
    op.drop_table('announcements')
    # ### end Alembic commands ###
