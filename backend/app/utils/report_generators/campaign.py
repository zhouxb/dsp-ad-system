import pandas as pd
from typing import Dict, Any, List
from app.models.report.report import DailyStatistic
from app.models.campaign.campaign import Campaign
from .base import BaseReportGenerator


class CampaignReportGenerator(BaseReportGenerator):
    """Report generator for campaign performance reports"""

    def get_data(self) -> pd.DataFrame:
        """Get campaign performance data"""
        # Get campaign IDs from parameters
        campaign_ids = self.parameters.get('campaign_ids', [])

        # Query daily statistics
        query = DailyStatistic.query.filter(
            DailyStatistic.date >= self.start_date,
            DailyStatistic.date <= self.end_date
        )

        if campaign_ids:
            query = query.filter(DailyStatistic.campaign_id.in_(campaign_ids))

        stats = query.all()

        # Convert to DataFrame
        data = []
        for stat in stats:
            data.append({
                'date': stat.date,
                'campaign_id': stat.campaign_id,
                'campaign_name': stat.campaign.name if stat.campaign else None,
                'impressions': stat.impressions,
                'clicks': stat.clicks,
                'conversions': stat.conversions,
                'spend': stat.spend,
                'ctr': stat.ctr,
                'cpc': stat.cpc,
                'cpm': stat.cpm,
                'cvr': stat.cvr,
                'cpa': stat.cpa
            })

        return pd.DataFrame(data)

    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to the campaign data"""
        filters = self.parameters.get('filters', {})

        for field, value in filters.items():
            if field in df.columns:
                if isinstance(value, list):
                    df = df[df[field].isin(value)]
                else:
                    df = df[df[field] == value]

        return df

    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate campaign metrics"""
        # Basic metrics are already calculated in DailyStatistic
        # Add any additional calculations here

        # Calculate custom metrics if specified
        if 'custom_metrics' in self.parameters:
            for metric_name in self.parameters['custom_metrics']:
                custom_metrics = self._get_custom_metrics(self.report.advertiser_id)
                for metric in custom_metrics:
                    if metric.name == metric_name:
                        df[metric_name] = self._calculate_custom_metric(df, metric)

        return df
