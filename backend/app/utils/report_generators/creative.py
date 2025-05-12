import pandas as pd
from typing import Dict, Any, List
from app.models.report.report import DailyStatistic
from app.models.creative.creative import Creative
from .base import BaseReportGenerator


class CreativeReportGenerator(BaseReportGenerator):
    """Report generator for creative performance reports"""

    def get_data(self) -> pd.DataFrame:
        """Get creative performance data"""
        # Get creative IDs from parameters
        creative_ids = self.parameters.get('creative_ids', [])

        # Query daily statistics
        query = DailyStatistic.query.filter(
            DailyStatistic.date >= self.start_date,
            DailyStatistic.date <= self.end_date
        )

        if creative_ids:
            query = query.filter(DailyStatistic.creative_id.in_(creative_ids))

        stats = query.all()

        # Convert to DataFrame
        data = []
        for stat in stats:
            data.append({
                'date': stat.date,
                'creative_id': stat.creative_id,
                'creative_name': stat.creative.name if stat.creative else None,
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
                'cpa': stat.cpa,
                'video_starts': stat.video_starts,
                'video_completes': stat.video_completes,
                'video_first_quartile': stat.video_first_quartile,
                'video_midpoint': stat.video_midpoint,
                'video_third_quartile': stat.video_third_quartile
            })

        return pd.DataFrame(data)

    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to the creative data"""
        filters = self.parameters.get('filters', {})

        for field, value in filters.items():
            if field in df.columns:
                if isinstance(value, list):
                    df = df[df[field].isin(value)]
                else:
                    df = df[df[field] == value]

        return df

    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate creative metrics"""
        # Basic metrics are already calculated in DailyStatistic
        # Add video-specific metrics
        if 'video_starts' in df.columns and 'impressions' in df.columns:
            df['video_start_rate'] = df['video_starts'] / df['impressions']

        if 'video_completes' in df.columns and 'video_starts' in df.columns:
            df['video_completion_rate'] = df['video_completes'] / df['video_starts']

        # Calculate custom metrics if specified
        if 'custom_metrics' in self.parameters:
            for metric_name in self.parameters['custom_metrics']:
                custom_metrics = self._get_custom_metrics(self.report.advertiser_id)
                for metric in custom_metrics:
                    if metric.name == metric_name:
                        df[metric_name] = self._calculate_custom_metric(df, metric)

        return df
