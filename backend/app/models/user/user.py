from typing import Dict, List, Optional, Any
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.models.base import BaseModel, AuditLogMixin, db
from app.core.security import get_password_hash, verify_password

# Association table for user_roles
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)


class Permission:
    """System permissions"""
    # Campaign permissions
    CAMPAIGN_VIEW = 'campaigns.view'
    CAMPAIGN_CREATE = 'campaigns.create'
    CAMPAIGN_EDIT = 'campaigns.edit'
    CAMPAIGN_DELETE = 'campaigns.delete'
    CAMPAIGN_APPROVE = 'campaigns.approve'

    # Creative permissions
    CREATIVE_VIEW = 'creatives.view'
    CREATIVE_CREATE = 'creatives.create'
    CREATIVE_EDIT = 'creatives.edit'
    CREATIVE_DELETE = 'creatives.delete'
    CREATIVE_APPROVE = 'creatives.approve'

    # Advertiser permissions
    ADVERTISER_VIEW = 'advertisers.view'
    ADVERTISER_CREATE = 'advertisers.create'
    ADVERTISER_EDIT = 'advertisers.edit'
    ADVERTISER_DELETE = 'advertisers.delete'

    # Report permissions
    REPORT_VIEW = 'reports.view'
    REPORT_CREATE = 'reports.create'
    REPORT_DOWNLOAD = 'reports.download'

    # User management permissions
    USER_VIEW = 'users.view'
    USER_CREATE = 'users.create'
    USER_EDIT = 'users.edit'
    USER_DELETE = 'users.delete'

    # Role management permissions
    ROLE_VIEW = 'roles.view'
    ROLE_CREATE = 'roles.create'
    ROLE_EDIT = 'roles.edit'
    ROLE_DELETE = 'roles.delete'

    # Billing permissions
    BILLING_VIEW = 'billing.view'
    BILLING_CREATE = 'billing.create'
    BILLING_EDIT = 'billing.edit'

    # Analytics permissions
    ANALYTICS_VIEW = 'analytics.view'
    ANALYTICS_EXPORT = 'analytics.export'

    @classmethod
    def get_all_permissions(cls) -> List[str]:
        """Get all available permissions"""
        return [
            value for key, value in cls.__dict__.items()
            if not key.startswith('_') and isinstance(value, str)
        ]

    @classmethod
    def get_permission_groups(cls) -> Dict[str, List[str]]:
        """Get permissions grouped by category"""
        groups = {}
        for key, value in cls.__dict__.items():
            if not key.startswith('_') and isinstance(value, str):
                category = key.split('_')[0].lower()
                if category not in groups:
                    groups[category] = []
                groups[category].append(value)
        return groups


class User(BaseModel, AuditLogMixin):
    """User model for authentication and authorization"""
    __tablename__ = 'user'

    username = Column(String(64), unique=True, index=True, nullable=False, comment='用户名')
    email = Column(String(120), unique=True, index=True, nullable=False, comment='邮箱')
    full_name = Column(String(120), nullable=True, comment='姓名')
    hashed_password = Column(String(255), nullable=False, comment='密码哈希')
    is_active = Column(Boolean, default=True, comment='是否激活')
    is_superuser = Column(Boolean, default=False, comment='是否超级管理员')
    last_login = Column(String(30), nullable=True, comment='最后登录时间')
    advertiser_id = Column(Integer, ForeignKey('advertiser.id', name='fk_user_advertiser_id'), nullable=True, comment='关联的广告主ID')
    phone = Column(String(20), nullable=True, comment='手机号')

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    advertiser = relationship(
        "Advertiser",
        back_populates="users",
        foreign_keys=[advertiser_id]
    )
    managed_advertisers = relationship('Advertiser', back_populates='account_manager', foreign_keys='Advertiser.account_manager_id')

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Set password hash from plain text password"""
        self.hashed_password = get_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if plain text password matches hash"""
        return verify_password(password, self.hashed_password)

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        if self.is_superuser:
            return True

        for role in self.roles:
            if role.has_permission(permission):
                return True

        return False

    def get_permissions(self) -> List[str]:
        """Get all permissions assigned to this user through roles"""
        if self.is_superuser:
            return ["*"]  # Superuser has all permissions

        permissions = set()
        for role in self.roles:
            for perm in role.get_permissions():
                permissions.add(perm)

        return list(permissions)

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        """Get user by username"""
        return cls.query.filter_by(username=username, is_deleted=False).first()

    @classmethod
    def get_by_email(cls, email: str) -> Optional["User"]:
        """Get user by email"""
        return cls.query.filter_by(email=email, is_deleted=False).first()


class Role(BaseModel, AuditLogMixin):
    """Role model for RBAC"""
    __tablename__ = 'role'

    name = Column(String(80), unique=True, nullable=False, comment='角色名称')
    description = Column(String(255), comment='角色描述')
    permissions = Column(JSON, default=lambda: {}, comment='权限列表')

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def has_permission(self, permission: str) -> bool:
        """Check if role has a specific permission"""
        if not self.permissions:
            return False

        # Handle wildcard permissions
        if "*" in self.permissions.get("permissions", []):
            return True

        return permission in self.permissions.get("permissions", [])

    def get_permissions(self) -> List[str]:
        """Get all permissions for this role"""
        if not self.permissions:
            return []

        return self.permissions.get("permissions", [])

    def set_permissions(self, permissions: List[str]) -> None:
        """Set permissions for this role"""
        if not self.permissions:
            self.permissions = {}

        self.permissions["permissions"] = permissions

    def add_permission(self, permission: str) -> None:
        """Add a permission to this role"""
        if not self.permissions:
            self.permissions = {"permissions": []}

        if permission not in self.permissions.get("permissions", []):
            self.permissions["permissions"].append(permission)

    def remove_permission(self, permission: str) -> None:
        """Remove a permission from this role"""
        if not self.permissions or "permissions" not in self.permissions:
            return

        if permission in self.permissions["permissions"]:
            self.permissions["permissions"].remove(permission)
