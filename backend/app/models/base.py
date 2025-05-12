import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime, String, Boolean, text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import MutableDict

from app.extensions import db
# Initialize SQLAlchemy
# db = SQLAlchemy()
migrate = Migrate()


class BaseModel(db.Model):
    """Base model for all database models"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def save(self) -> "BaseModel":
        """Save the current instance to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def update(self, **kwargs) -> "BaseModel":
        """Update model with kwargs and save"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save()
    
    def delete(self) -> "BaseModel":
        """Soft delete the instance"""
        self.is_deleted = True
        return self.save()
    
    @classmethod
    def get_by_id(cls, id: int) -> Optional["BaseModel"]:
        """Get a model instance by ID"""
        return cls.query.filter_by(id=id, is_deleted=False).first()
    
    @classmethod
    def get_all(cls, **filters) -> List["BaseModel"]:
        """Get all active instances with filters"""
        # Always exclude deleted records
        filters['is_deleted'] = False
        return cls.query.filter_by(**filters).all()
        
    @classmethod
    def paginate(
        cls, 
        page: int = 1, 
        per_page: int = 20, 
        **filters
    ) -> Dict[str, Any]:
        """Paginate query results"""
        filters['is_deleted'] = False
        query = cls.query.filter_by(**filters)
        
        pagination = query.paginate(page=page, per_page=per_page)
        return {
            "items": [item.to_dict() for item in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages
        }


class AuditLogMixin:
    """Mixin to add audit fields for models requiring audit trail"""
    created_by_id = Column(Integer, nullable=True)
    updated_by_id = Column(Integer, nullable=True)
    audit_log = Column(MutableDict.as_mutable(JSON), default=lambda: {}, nullable=True)
    
    def log_change(self, user_id: int, action: str, details: Dict[str, Any]) -> None:
        """Log a change to the model with user info"""
        if not self.audit_log:
            self.audit_log = {}
            
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id,
            "action": action,
            "details": details
        }
        
        # Add entry to audit log
        self.audit_log[str(uuid.uuid4())] = log_entry
        
        # Update last modified user
        self.updated_by_id = user_id 