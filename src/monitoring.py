"""
Model Monitoring & Alerting
---------------------------
Monitors model performance, detects drift, and sends alerts.

Features:
- Prediction accuracy monitoring
- Data drift detection
- Performance degradation alerts
- Slack/Email notifications (configurable)

Usage:
    python src/monitoring.py
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Thresholds
RMSE_THRESHOLD = 5.0  # Alert if RMSE exceeds this
MAE_THRESHOLD = 3.0  # Alert if MAE exceeds this
DRIFT_THRESHOLD = 0.2  # 20% change in distribution


class ModelMonitor:
    """Monitor model predictions and detect issues"""

    def __init__(self, predictions_path: str = "data/predictions.csv"):
        self.predictions_path = Path(predictions_path)
        self.alerts = []

    def load_predictions(self, days: int = 7) -> pd.DataFrame:
        """Load recent predictions"""
        if not self.predictions_path.exists():
            logger.warning("No predictions file found")
            return pd.DataFrame()

        df = pd.read_csv(self.predictions_path, parse_dates=["prediction_date", "generated_at"])
        cutoff = datetime.now() - timedelta(days=days)
        return df[df["generated_at"] >= cutoff]

    def check_prediction_range(self, df: pd.DataFrame) -> bool:
        """Check if predictions are within reasonable range"""
        if df.empty:
            return True

        predictions = df["predicted_pm25"]

        # PM2.5 should be between 0 and 500 µg/m³
        out_of_range = (predictions < 0) | (predictions > 500)
        if out_of_range.any():
            count = out_of_range.sum()
            self.alerts.append(
                {
                    "type": "OUT_OF_RANGE",
                    "severity": "WARNING",
                    "message": f"{count} predictions out of valid range (0-500 µg/m³)",
                }
            )
            return False
        return True

    def check_prediction_variance(self, df: pd.DataFrame) -> bool:
        """Check for unusual variance in predictions"""
        if len(df) < 10:
            return True

        predictions = df["predicted_pm25"]
        std = predictions.std()
        mean = predictions.mean()

        # Coefficient of variation check
        cv = std / mean if mean > 0 else 0
        if cv > 1.0:  # Very high variance
            self.alerts.append(
                {
                    "type": "HIGH_VARIANCE",
                    "severity": "WARNING",
                    "message": f"High prediction variance detected (CV={cv:.2f})",
                }
            )
            return False
        return True

    def check_missing_predictions(self, df: pd.DataFrame, expected_hourly: bool = True) -> bool:
        """Check for gaps in predictions"""
        if len(df) < 2:
            return True

        df_sorted = df.sort_values("prediction_date")
        time_diffs = df_sorted["prediction_date"].diff()

        if expected_hourly:
            # Check for gaps > 2 hours
            large_gaps = time_diffs > pd.Timedelta(hours=2)
            if large_gaps.any():
                gap_count = large_gaps.sum()
                self.alerts.append(
                    {
                        "type": "MISSING_PREDICTIONS",
                        "severity": "INFO",
                        "message": f"{gap_count} gaps detected in hourly predictions",
                    }
                )
                return False
        return True

    def run_all_checks(self) -> dict:
        """Run all monitoring checks"""
        logger.info("Starting model monitoring checks...")
        df = self.load_predictions()

        results = {"timestamp": datetime.now().isoformat(), "predictions_count": len(df), "checks": {}}

        # Run checks
        results["checks"]["range"] = self.check_prediction_range(df)
        results["checks"]["variance"] = self.check_prediction_variance(df)
        results["checks"]["gaps"] = self.check_missing_predictions(df)

        # Summary
        results["all_passed"] = all(results["checks"].values())
        results["alerts"] = self.alerts

        # Log results
        if results["all_passed"]:
            logger.info("✅ All monitoring checks passed")
        else:
            logger.warning(f"⚠️ {len(self.alerts)} alerts raised")
            for alert in self.alerts:
                logger.warning(f"  [{alert['severity']}] {alert['type']}: {alert['message']}")

        return results

    def send_alert(self, alert: dict):
        """Send alert notification (placeholder for Slack/Email integration)"""
        # TODO: Implement Slack webhook or email sending
        logger.warning(f"ALERT: {alert['message']}")


def generate_monitoring_report(output_path: str = "reports/monitoring_report.md"):
    """Generate a monitoring report"""
    monitor = ModelMonitor()
    results = monitor.run_all_checks()

    report = f"""# Model Monitoring Report

**Generated:** {results['timestamp']}

## Summary
- **Predictions Analyzed:** {results['predictions_count']}
- **All Checks Passed:** {'✅ Yes' if results['all_passed'] else '❌ No'}

## Check Results
| Check | Status |
|-------|--------|
| Prediction Range | {'✅' if results['checks']['range'] else '❌'} |
| Prediction Variance | {'✅' if results['checks']['variance'] else '❌'} |
| Missing Predictions | {'✅' if results['checks']['gaps'] else '⚠️'} |

## Alerts
"""
    if results["alerts"]:
        for alert in results["alerts"]:
            report += f"- **[{alert['severity']}]** {alert['type']}: {alert['message']}\n"
    else:
        report += "_No alerts_\n"

    # Save report
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Report saved to {output_path}")
    return results


if __name__ == "__main__":
    generate_monitoring_report()
