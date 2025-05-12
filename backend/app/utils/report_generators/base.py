from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import pandas as pd
from app.models.report.report import Report
from app.models.report.report import DailyStatistic
from app.models.report.report import HourlyStatistic
from app.models.report.report import CustomMetric


class BaseReportGenerator(ABC):
    """Base class for all report generators"""

    def __init__(self, report: Report):
        self.report = report
        self.parameters = report.parameters
        self.start_date = report.start_date
        self.end_date = report.end_date

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        """Get the data for the report"""
        pass

    @abstractmethod
    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to the data"""
        pass

    @abstractmethod
    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate metrics for the report"""
        pass

    def generate(self) -> str:
        """Generate the report and return the file path"""
        try:
            # Get the data
            df = self.get_data()

            # Apply filters
            df = self.apply_filters(df)

            # Calculate metrics
            df = self.calculate_metrics(df)

            # Group by if specified
            if 'group_by' in self.parameters:
                df = df.groupby(self.parameters['group_by']).sum().reset_index()

            # Sort if specified
            if 'sort_by' in self.parameters:
                df = df.sort_values(
                    by=self.parameters['sort_by'],
                    ascending=self.parameters.get('sort_ascending', True)
                )

            # Limit if specified
            if 'limit' in self.parameters:
                df = df.head(self.parameters['limit'])

            # Generate file path
            file_path = self._generate_file_path()

            # Save the report
            self._save_report(df, file_path)

            return file_path

        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")

    def _generate_file_path(self) -> str:
        """Generate a unique file path for the report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"reports/{self.report.report_type}_{timestamp}.csv"

    def _save_report(self, df: pd.DataFrame, file_path: str) -> None:
        """Save the report to a file"""
        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save based on file extension
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        elif file_path.endswith('.json'):
            df.to_json(file_path, orient='records')
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

    def _get_custom_metrics(self, advertiser_id: int) -> List[CustomMetric]:
        """Get custom metrics for an advertiser"""
        return CustomMetric.query.filter_by(advertiser_id=advertiser_id).all()

    def _calculate_custom_metric(self, df: pd.DataFrame, metric: CustomMetric) -> pd.Series:
        """Calculate a custom metric"""
        # This is a placeholder - actual implementation would need to parse and evaluate the formula
        return pd.Series(0, index=df.index)
