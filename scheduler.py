"""
Automated Scheduler for BreatheSmart Data Ingestion
Runs data_ingestor.py at scheduled intervals

Usage:
    python scheduler.py           # Run in foreground with default schedule
    python scheduler.py --daily   # Run daily at 2:00 AM
    python scheduler.py --hourly  # Run every hour (for testing)
"""
import schedule
import time
import logging
import sys
from datetime import datetime
from pathlib import Path
import argparse

# Import our config and ingestor
from config import LOGS_PATH, LOG_FORMAT, LOG_LEVEL
from data_ingestor import fetch_abu_dhabi_air

# Setup logging
log_file = LOGS_PATH / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def job():
    """
    The scheduled job - runs the data ingestor
    """
    logger.info("⏰ Scheduled ingestion job triggered")
    try:
        fetch_abu_dhabi_air(incremental=True)
        logger.info("✅ Scheduled job completed successfully")
    except Exception as e:
        logger.error(f"❌ Scheduled job failed: {e}", exc_info=True)


def run_scheduler(mode='daily'):
    """
    Start the scheduler
    
    Args:
        mode: 'daily', 'hourly', or 'test' (every 5 minutes)
    """
    logger.info("=" * 80)
    logger.info("🕐 BreatheSmart Scheduler Started")
    logger.info(f"Mode: {mode}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    if mode == 'daily':
        # Run every day at 2:00 AM
        schedule.every().day.at("02:00").do(job)
        logger.info("📅 Scheduled: Daily at 2:00 AM")
    elif mode == 'hourly':
        # Run every hour (useful for testing)
        schedule.every().hour.do(job)
        logger.info("📅 Scheduled: Every hour")
    elif mode == 'test':
        # Run every 5 minutes (for testing)
        schedule.every(5).minutes.do(job)
        logger.info("📅 Scheduled: Every 5 minutes (TEST MODE)")
    else:
        logger.error(f"Unknown mode: {mode}")
        return
    
    # Run once immediately
    logger.info("🚀 Running initial ingestion job...")
    job()
    
    # Enter scheduler loop
    logger.info("\n⏳ Waiting for next scheduled run... (Press Ctrl+C to stop)")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("\n🛑 Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BreatheSmart Data Ingestion Scheduler')
    parser.add_argument(
        '--mode',
        choices=['daily', 'hourly', 'test'],
        default='daily',
        help='Scheduling mode: daily (2 AM), hourly, or test (5 min)'
    )
    
    args = parser.parse_args()
    run_scheduler(mode=args.mode)
