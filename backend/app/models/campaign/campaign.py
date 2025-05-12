from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text, Enum, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.models.base import BaseModel, AuditLogMixin, db
from app.models.creative import Creative


class Campaign(BaseModel, AuditLogMixin):
    """Campaign model representing an advertising campaign"""
    name = Column(String(100), nullable=False)
    advertiser_id = Column(Integer, ForeignKey('advertiser.id'), nullable=False)
    daily_budget = Column(Float, nullable=False)
    total_budget = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum('draft', 'pending', 'active', 'paused', 'completed', 'rejected'), default='draft', nullable=False)
    targeting = Column(JSON, nullable=True, comment="Targeting criteria")
    bid_strategy = Column(Enum('cpc', 'cpm', 'cpa', 'cpi'), default='cpc', nullable=False)
    bid_amount = Column(Float, nullable=False)
    frequency_cap = Column(Integer, nullable=True, comment="Maximum impressions per user")
    frequency_period = Column(String(20), nullable=True, comment="Period for frequency cap (e.g., day, week)")
    rejection_reason = Column(Text, nullable=True)
    
    # Settings
    settings = Column(JSON, default=lambda: {}, nullable=True)
    
    # Optimization settings
    optimization_goal = Column(String(50), nullable=True, comment="Optimization goal (e.g., clicks, conversions)")
    
    # Relationships
    advertiser = relationship("Advertiser", back_populates="campaigns")
    creatives = relationship("Creative", back_populates="campaign")
    
    def __repr__(self) -> str:
        return f"<Campaign {self.name}>"
    
    def get_daily_spent(self, date: datetime = None) -> float:
        """Get amount spent for a specific day"""
        if date is None:
            date = datetime.utcnow()
            
        # This would normally query from a stats table
        # Placeholder for now
        return 0.0
    
    def get_total_spent(self) -> float:
        """Get total amount spent for the campaign"""
        # This would normally query from a stats table
        # Placeholder for now
        return 0.0
    
    def is_within_budget(self) -> bool:
        """Check if campaign is within budget limits"""
        daily_spent = self.get_daily_spent()
        total_spent = self.get_total_spent()
        
        return daily_spent < self.daily_budget and total_spent < self.total_budget
    
    def is_active(self) -> bool:
        """Check if campaign is currently active"""
        now = datetime.utcnow()
        
        if self.status != 'active':
            return False
            
        if now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return self.is_within_budget()
    
    def set_targeting(self, targeting_config: Dict[str, Any]) -> None:
        """Set targeting configuration for campaign"""
        self.targeting = targeting_config
        
    def get_active_creatives(self) -> List["Creative"]:
        """Get list of active creatives for this campaign"""
        return [c for c in self.creatives if c.status == 'active']


class TargetingRule(BaseModel):
    """Model for storing targeting rules"""
    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=False)
    rule_type = Column(String(50), nullable=False, comment="Type of targeting rule (geo, device, etc)")
    rule_value = Column(JSON, nullable=False, comment="JSON value of the rule")
    operator = Column(String(20), default='include', comment="include or exclude")
    
    # Relationships
    campaign = relationship("Campaign")
    
    def __repr__(self) -> str:
        return f"<TargetingRule {self.rule_type}>"