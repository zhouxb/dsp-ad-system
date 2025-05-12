import pandas as pd
from typing import Dict, Any, List
from app.models.report.report import DailyStatistic
from app.models.advertiser.advertiser import Advertiser
from .base import BaseReportGenerator


class AdvertiserReportGenerator(BaseReportGenerator):
    """Report generator for advertiser performance reports"""

    def get_data(self) -> pd.DataFrame:
        """Get advertiser performance data"""
        # Get advertiser IDs from parameters
        advertiser_ids = self.parameters.get('advertiser_ids', [])

        # Query daily statistics
        query = DailyStatistic.query.filter(
            DailyStatistic.date >= self.start_date,
            DailyStatistic.date <= self.end_date
        )

        if advertiser_ids:
            query = query.filter(DailyStatistic.advertiser_id.in_(advertiser_ids))

        stats = query.all()

        # Convert to DataFrame
        data = []
        for stat in stats:
            data.append({
                'date': stat.date,
                'advertiser_id': stat.advertiser_id,
                'advertiser_name': stat.advertiser.name if stat.advertiser else None,
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
        """Apply filters to the advertiser data"""
        filters = self.parameters.get('filters', {})

        for field, value in filters.items():
            if field in df.columns:
                if isinstance(value, list):
                    df = df[df[field].isin(value)]
                else:
                    df = df[df[field] == value]

        return df

    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advertiser metrics"""
        # Basic metrics are already calculated in DailyStatistic

        # Calculate custom metrics if specified
        if 'custom_metrics' in self.parameters:
            for metric_name in self.parameters['custom_metrics']:
                custom_metrics = self._get_custom_metrics(self.report.advertiser_id)
                for metric in custom_metrics:
                    if metric.name == metric_name:
                        df[metric_name] = self._calculate_custom_metric(df, metric)

        return df
