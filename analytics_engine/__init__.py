"""
Analytics Engine for SURESH AI ORIGIN
Modular analytics system with GA/Stripe/referral data, KPI calculations, anomaly detection, and weekly PDF reports
"""

from .data_collector import DataCollector
from .kpi_calculator import KPICalculator
from .anomaly_detector import AnomalyDetector
from .pdf_generator import PDFGenerator
from .email_notifier import EmailNotifier
from .scheduler import AnalyticsScheduler

__version__ = "1.0.0"
__all__ = [
    "DataCollector",
    "KPICalculator",
    "AnomalyDetector",
    "PDFGenerator",
    "EmailNotifier",
    "AnalyticsScheduler"
]
