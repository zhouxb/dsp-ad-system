from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Text, Enum, Float, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.models.base import BaseModel, AuditLogMixin, db


class DailyStatistic(BaseModel):
    """Daily statistics for campaigns, creatives and advertisers"""
    date = Column(Date, nullable=False, index=True)
    advertiser_id = Column(Integer, ForeignKey('advertiser.id'), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=True, index=True)
    creative_id = Column(Integer, ForeignKey('creative.id'), nullable=True, index=True)

    # Basic metrics
    impressions = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    conversions = Column(Integer, default=0, nullable=False)
    spend = Column(Float, default=0.0, nullable=False)

    # Calculated metrics
    ctr = Column(Float, default=0.0, nullable=False, comment="Click-through rate")
    cpc = Column(Float, default=0.0, nullable=False, comment="Cost per click")
    cpm = Column(Float, default=0.0, nullable=False, comment="Cost per mille (1000 impressions)")
    cvr = Column(Float, default=0.0, nullable=False, comment="Conversion rate")
    cpa = Column(Float, default=0.0, nullable=False, comment="Cost per acquisition")

    # Extended metrics
    video_starts = Column(Integer, default=0, nullable=True)
    video_completes = Column(Integer, default=0, nullable=True)
    video_first_quartile = Column(Integer, default=0, nullable=True)
    video_midpoint = Column(Integer, default=0, nullable=True)
    video_third_quartile = Column(Integer, default=0, nullable=True)

    # Additional data
    additional_metrics = Column(JSON, nullable=True, comment="Additional metrics and dimensions")

    # Relationships
    advertiser = relationship("Advertiser")
    campaign = relationship("Campaign")
    creative = relationship("Creative")

    def __repr__(self) -> str:
        parts = [f"DailyStat {self.date}"]
        if self.advertiser_id:
            parts.append(f"adv:{self.advertiser_id}")
        if self.campaign_id:
            parts.append(f"camp:{self.campaign_id}")
        if self.creative_id:
            parts.append(f"cr:{self.creative_id}")
        return "<" + " ".join(parts) + ">"

    @classmethod
    def get_advertiser_stats(cls, advertiser_id: int, start_date: Date, end_date: Date) -> List["DailyStatistic"]:
        """Get daily stats for an advertiser within date range"""
        return cls.query.filter(
            cls.advertiser_id == advertiser_id,
            cls.campaign_id.is_(None),
            cls.creative_id.is_(None),
            cls.date >= start_date,
            cls.date <= end_date
        ).order_by(cls.date.asc()).all()

    @classmethod
    def get_campaign_stats(cls, campaign_id: int, start_date: Date, end_date: Date) -> List["DailyStatistic"]:
        """Get daily stats for a campaign within date range"""
        return cls.query.filter(
            cls.campaign_id == campaign_id,
            cls.creative_id.is_(None),
            cls.date >= start_date,
            cls.date <= end_date
        ).order_by(cls.date.asc()).all()

    @classmethod
    def get_creative_stats(cls, creative_id: int, start_date: Date, end_date: Date) -> List["DailyStatistic"]:
        """Get daily stats for a creative within date range"""
        return cls.query.filter(
            cls.creative_id == creative_id,
            cls.date >= start_date,
            cls.date <= end_date
        ).order_by(cls.date.asc()).all()


class HourlyStatistic(BaseModel):
    """Hourly statistics for real-time monitoring"""
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=False, index=True)
    advertiser_id = Column(Integer, ForeignKey('advertiser.id'), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=True, index=True)

    # Basic metrics
    impressions = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    conversions = Column(Integer, default=0, nullable=False)
    spend = Column(Float, default=0.0, nullable=False)

    # Calculated metrics
    ctr = Column(Float, default=0.0, nullable=False)
    cpc = Column(Float, default=0.0, nullable=False)

    def __repr__(self) -> str:
        return f"<HourlyStat {self.date} {self.hour}:00 camp:{self.campaign_id}>"


class Report(BaseModel, AuditLogMixin):
    """Model for report generation jobs"""
    name = Column(String(100), nullable=False)
    status = Column(Enum('pending', 'processing', 'completed', 'failed'), default='pending', nullable=False)
    report_type = Column(String(50), nullable=False, comment="Type of report")
    parameters = Column(JSON, nullable=False, comment="Report generation parameters")
    result_file_path = Column(String(255), nullable=True, comment="Path to generated report file")
    error_message = Column(Text, nullable=True)

    # Date range
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Task and processing info
    task_id = Column(String(100), nullable=True, comment="Celery task ID")
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Report {self.name} ({self.status})>"

    def start_processing(self, task_id: str) -> None:
        """Mark report job as processing"""
        self.status = 'processing'
        self.task_id = task_id
        self.processing_started_at = datetime.utcnow()
        self.save()

    def complete(self, file_path: str) -> None:
        """Mark report job as completed"""
        self.status = 'completed'
        self.result_file_path = file_path
        self.processing_completed_at = datetime.utcnow()
        self.save()

    def fail(self, error_message: str) -> None:
        """Mark report job as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.processing_completed_at = datetime.utcnow()
        self.save()


class CustomMetric(BaseModel):
    """Model for custom metrics defined by users"""
    name = Column(String(100), nullable=False)
    advertiser_id = Column(Integer, ForeignKey('advertiser.id'), nullable=False)
    formula = Column(String(500), nullable=False, comment="Formula for calculating metric")
    description = Column(Text, nullable=True)

    # Relationships
    advertiser = relationship("Advertiser")

    def __repr__(self) -> str:
        return f"<CustomMetric {self.name}>"
