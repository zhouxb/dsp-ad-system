from .base import BaseReportGenerator
from .campaign import CampaignReportGenerator
from .creative import CreativeReportGenerator
from .advertiser import AdvertiserReportGenerator
from app.models.report.report import Report


def generate_campaign_report(report: Report) -> str:
    """Generate campaign performance report"""
    generator = CampaignReportGenerator(report)
    return generator.generate()


def generate_creative_report(report: Report) -> str:
    """Generate creative performance report"""
    generator = CreativeReportGenerator(report)
    return generator.generate()


def generate_advertiser_report(report: Report) -> str:
    """Generate advertiser performance report"""
    generator = AdvertiserReportGenerator(report)
    return generator.generate()


def generate_platform_report(report: Report) -> str:
    """Generate platform performance report"""
    # For now, we'll use the advertiser report generator
    # In the future, this could be replaced with a dedicated PlatformReportGenerator
    generator = AdvertiserReportGenerator(report)
    return generator.generate()


__all__ = [
    'BaseReportGenerator',
    'CampaignReportGenerator',
    'CreativeReportGenerator',
    'AdvertiserReportGenerator',
    'generate_campaign_report',
    'generate_creative_report',
    'generate_advertiser_report',
    'generate_platform_report'
] 