from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text, Enum, Float, DateTime, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, AuditLogMixin, db


class Creative(BaseModel, AuditLogMixin):
    """Model for creative assets"""
    
    # Basic information
    name = Column(String(100), nullable=False)
    advertiser_id = Column(Integer, ForeignKey('advertiser.id'), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=False, index=True)
    status = Column(Enum('draft', 'pending', 'active', 'paused', 'rejected', 'archived'), 
                   default='draft', nullable=False)
    
    # Creative type and format
    type = Column(Enum('image', 'video', 'html5', 'native'), nullable=False)
    format = Column(String(50), nullable=False, comment="Creative format (e.g., 300x250, 728x90)")
    file_type = Column(String(20), nullable=False, comment="File type (e.g., jpg, mp4, zip)")
    file_size = Column(Integer, nullable=False, comment="File size in bytes")
    file_path = Column(String(255), nullable=False, comment="Path to creative file")
    
    # Creative content
    title = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    call_to_action = Column(String(50), nullable=True)
    landing_url = Column(String(500), nullable=False)
    
    # Video specific fields
    duration = Column(Integer, nullable=True, comment="Duration in seconds for video creatives")
    video_thumbnail = Column(String(255), nullable=True, comment="Path to video thumbnail")
    
    # HTML5 specific fields
    html5_zip_path = Column(String(255), nullable=True, comment="Path to HTML5 zip file")
    html5_entry_point = Column(String(100), nullable=True, comment="Main HTML file in the zip")
    
    # Native specific fields
    native_assets = Column(JSON, nullable=True, comment="Native ad assets (title, description, icon, etc.)")
    
    # Tracking and targeting
    click_tracking_url = Column(String(500), nullable=True)
    impression_tracking_url = Column(String(500), nullable=True)
    view_tracking_url = Column(String(500), nullable=True)
    targeting = Column(JSON, nullable=True, comment="Creative-specific targeting rules")
    
    # Performance metrics
    impressions = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    conversions = Column(Integer, default=0, nullable=False)
    spend = Column(Float, default=0.0, nullable=False)
    
    # Relationships
    advertiser = relationship("Advertiser", back_populates="creatives", foreign_keys=[advertiser_id])
    campaign = relationship("Campaign", back_populates="creatives")
    
    def __repr__(self) -> str:
        return f"<Creative {self.name} ({self.type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert creative to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'advertiser_id': self.advertiser_id,
            'campaign_id': self.campaign_id,
            'status': self.status,
            'type': self.type,
            'format': self.format,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_path': self.file_path,
            'title': self.title,
            'description': self.description,
            'call_to_action': self.call_to_action,
            'landing_url': self.landing_url,
            'duration': self.duration,
            'video_thumbnail': self.video_thumbnail,
            'html5_zip_path': self.html5_zip_path,
            'html5_entry_point': self.html5_entry_point,
            'native_assets': self.native_assets,
            'click_tracking_url': self.click_tracking_url,
            'impression_tracking_url': self.impression_tracking_url,
            'view_tracking_url': self.view_tracking_url,
            'targeting': self.targeting,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'spend': self.spend,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_advertiser(cls, advertiser_id: int) -> List["Creative"]:
        """Get all creatives for an advertiser"""
        return cls.query.filter_by(advertiser_id=advertiser_id).all()
    
    @classmethod
    def get_by_campaign(cls, campaign_id: int) -> List["Creative"]:
        """Get all creatives for a campaign"""
        return cls.query.filter_by(campaign_id=campaign_id).all()
    
    @classmethod
    def get_active_creatives(cls) -> List["Creative"]:
        """Get all active creatives"""
        return cls.query.filter_by(status='active').all()
    
    def update_status(self, new_status: str) -> None:
        """Update creative status"""
        if new_status not in ['draft', 'pending', 'active', 'paused', 'rejected', 'archived']:
            raise ValueError(f"Invalid status: {new_status}")
        
        self.status = new_status
        self.save()
    
    def update_metrics(self, impressions: int = 0, clicks: int = 0, 
                      conversions: int = 0, spend: float = 0.0) -> None:
        """Update creative performance metrics"""
        self.impressions += impressions
        self.clicks += clicks
        self.conversions += conversions
        self.spend += spend
        self.save() 