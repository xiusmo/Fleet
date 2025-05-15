from typing import Dict, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy as sa

from shared.models.sign_config import SignConfig
from shared.models.user_activity_detection import UserActivityDetection

if TYPE_CHECKING:
    from shared.models.worker import Worker

class User(SQLModel, table=True):
    """用户模型"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    tel: str = Field(unique=True, index=True)
    
    cx_d: str = Field(default=None, nullable=True)
    cx_uf: str = Field(default=None, nullable=True)
    cx_vc3: str = Field(default=None, nullable=True)
    cx_uid: str = Field(default=None, nullable=True)
    
    im_username: str = Field(default=None, nullable=True)   
    im_password: str = Field(default=None, nullable=True)
    monitor_status: bool = Field(default=False)
    
    person_name: str = Field(default=None, nullable=True)
    school_name: str = Field(default=None, nullable=True)
    fid: str = Field(default=None, nullable=True)
    
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    worker_name: str = Field(default=None, nullable=True, foreign_key="workers.name")
    
    # 关系
    sign_configs: List["SignConfig"] = Relationship(back_populates="user")
    detected_activities: List["UserActivityDetection"] = Relationship(back_populates="user")
    worker: Optional["Worker"] = Relationship(back_populates="users")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.TIMESTAMP(timezone=True))
    )

    @property
    def cookies(self) -> Dict[str, str]:
        """生成用户的cookie字符串
        
        Returns:
            str: 格式化的cookie字符串
        """
        cookies = {}
        
        if self.cx_d:
            cookies["_d"] = self.cx_d
            
        if self.cx_uf:
            cookies["uf"] = self.cx_uf
            
        if self.cx_vc3:
            cookies["vc3"] = self.cx_vc3
            
        if self.cx_uid:
            cookies["_uid"] = self.cx_uid
            cookies["UID"] = self.cx_uid
        
        if self.fid:
            cookies["fid"] = self.fid
        
        return cookies