"""
Scheduled Task Manager for Finance News AgentOS
Handles daily report generation and cache management
"""

from datetime import datetime, timedelta
import logging
from pathlib import Path
import threading
import time
from typing import Any

from .cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Background task scheduler for periodic operations"""

    def __init__(self, finance_agent=None):
        self.finance_agent = finance_agent
        self.running = False
        self.tasks = {}
        self.scheduler_thread = None

    def add_task(self, name: str, func, interval_hours: int, run_immediately: bool = False):
        """Add a scheduled task"""
        task = {
            "name": name,
            "func": func,
            "interval_hours": interval_hours,
            "last_run": None,
            "next_run": datetime.now()
            if run_immediately
            else datetime.now() + timedelta(hours=interval_hours),
            "run_count": 0,
            "error_count": 0,
        }
        self.tasks[name] = task
        logger.info(f"Scheduled task '{name}' to run every {interval_hours} hours")

    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Task scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Task scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                now = datetime.now()
                for task_name, task in self.tasks.items():
                    if now >= task["next_run"]:
                        self._run_task(task)

                # Sleep for 1 minute before checking again
                time.sleep(60)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

    def _run_task(self, task: dict[str, Any]):
        """Execute a scheduled task"""
        task_name = task["name"]
        try:
            logger.info(f"Running scheduled task: {task_name}")
            task["func"]()
            task["last_run"] = datetime.now()
            task["run_count"] += 1
            task["next_run"] = datetime.now() + timedelta(hours=task["interval_hours"])
            logger.info(f"Task '{task_name}' completed successfully")
        except Exception as e:
            task["error_count"] += 1
            task["next_run"] = datetime.now() + timedelta(hours=1)  # Retry in 1 hour
            logger.error(f"Task '{task_name}' failed: {e}")

    def get_task_status(self) -> dict[str, Any]:
        """Get status of all scheduled tasks"""
        status = {"scheduler_running": self.running, "tasks": {}}

        for task_name, task in self.tasks.items():
            status["tasks"][task_name] = {
                "last_run": task["last_run"].isoformat() if task["last_run"] else None,
                "next_run": task["next_run"].isoformat(),
                "run_count": task["run_count"],
                "error_count": task["error_count"],
                "interval_hours": task["interval_hours"],
            }

        return status


class DailyReportGenerator:
    """Generates and caches daily financial reports"""

    def __init__(self, finance_agent, reports_dir: str = "reports"):
        self.finance_agent = finance_agent
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)

    def generate_daily_market_overview(self):
        """Generate daily market overview report"""
        try:
            logger.info("Generating daily market overview...")

            # Run the agent to get market overview
            result = self.finance_agent.run(
                "Provide a comprehensive market overview including major indices, sector performance, and key economic indicators"
            )

            # Cache the result
            cache_manager = get_cache_manager()
            if cache_manager:
                cache_key = cache_manager._generate_key(
                    "daily_market_overview", {"date": datetime.now().strftime("%Y-%m-%d")}
                )
                cache_manager.set(
                    cache_key,
                    {
                        "overview": str(result.content),
                        "timestamp": datetime.now().isoformat(),
                        "type": "daily_overview",
                    },
                    ttl=86400,
                )  # 24 hours

            # Save to file
            filename = f"daily_market_overview_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = self.reports_dir / filename

            with open(filepath, "w") as f:
                f.write(f"# Daily Market Overview - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
                f.write(str(result.content))

            logger.info(f"Daily market overview saved to {filepath}")
            return str(result.content)

        except Exception as e:
            logger.error(f"Failed to generate daily market overview: {e}")
            raise

    def generate_top_stocks_analysis(self):
        """Generate analysis of top performing stocks"""
        try:
            logger.info("Generating top stocks analysis...")

            # Popular stocks to analyze
            stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "JNJ", "V"]

            analyses = {}
            for symbol in stocks[:5]:  # Limit to top 5 to avoid rate limits
                try:
                    result = self.finance_agent.run(
                        f"Provide a brief analysis of {symbol} including recent performance, key metrics, and outlook"
                    )
                    analyses[symbol] = str(result.content)
                    time.sleep(2)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Failed to analyze {symbol}: {e}")
                    analyses[symbol] = f"Analysis unavailable: {e}"

            # Cache the combined result
            cache_manager = get_cache_manager()
            if cache_manager:
                cache_key = cache_manager._generate_key(
                    "daily_stocks_analysis", {"date": datetime.now().strftime("%Y-%m-%d")}
                )
                cache_manager.set(
                    cache_key,
                    {
                        "analyses": analyses,
                        "timestamp": datetime.now().isoformat(),
                        "type": "daily_stocks",
                    },
                    ttl=86400,
                )

            # Save to file
            filename = f"daily_stocks_analysis_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = self.reports_dir / filename

            with open(filepath, "w") as f:
                f.write(f"# Daily Top Stocks Analysis - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
                for symbol, analysis in analyses.items():
                    f.write(f"## {symbol}\n\n{analysis}\n\n---\n\n")

            logger.info(f"Daily stocks analysis saved to {filepath}")
            return analyses

        except Exception as e:
            logger.error(f"Failed to generate stocks analysis: {e}")
            raise

    def generate_economic_indicators_report(self):
        """Generate economic indicators report"""
        try:
            logger.info("Generating economic indicators report...")

            result = self.finance_agent.run(
                "Provide analysis of key economic indicators including inflation data, employment figures, "
                "GDP growth, interest rates, and their implications for the markets"
            )

            # Cache the result
            cache_manager = get_cache_manager()
            if cache_manager:
                cache_key = cache_manager._generate_key(
                    "daily_economic_indicators", {"date": datetime.now().strftime("%Y-%m-%d")}
                )
                cache_manager.set(
                    cache_key,
                    {
                        "indicators": str(result.content),
                        "timestamp": datetime.now().isoformat(),
                        "type": "economic_indicators",
                    },
                    ttl=86400,
                )

            # Save to file
            filename = f"daily_economic_indicators_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = self.reports_dir / filename

            with open(filepath, "w") as f:
                f.write(f"# Daily Economic Indicators - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
                f.write(str(result.content))

            logger.info(f"Economic indicators report saved to {filepath}")
            return str(result.content)

        except Exception as e:
            logger.error(f"Failed to generate economic indicators report: {e}")
            raise

    def cleanup_old_reports(self, days_to_keep: int = 30):
        """Clean up old report files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0

            for filepath in self.reports_dir.glob("daily_*.md"):
                if filepath.stat().st_mtime < cutoff_date.timestamp():
                    filepath.unlink()
                    deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old report files")

        except Exception as e:
            logger.error(f"Failed to cleanup old reports: {e}")


def setup_scheduler(finance_agent) -> TaskScheduler:
    """Set up and configure the task scheduler"""
    scheduler = TaskScheduler(finance_agent)
    report_generator = DailyReportGenerator(finance_agent)

    # Add daily tasks (run at different times to spread load)
    scheduler.add_task(
        "daily_market_overview", report_generator.generate_daily_market_overview, interval_hours=24
    )

    scheduler.add_task(
        "daily_stocks_analysis", report_generator.generate_top_stocks_analysis, interval_hours=24
    )

    scheduler.add_task(
        "daily_economic_indicators",
        report_generator.generate_economic_indicators_report,
        interval_hours=24,
    )

    # Weekly cleanup task
    scheduler.add_task(
        "cleanup_old_reports",
        lambda: report_generator.cleanup_old_reports(days_to_keep=30),
        interval_hours=168,  # 7 days
    )

    # Cache cleanup task (every 6 hours)
    def cleanup_cache():
        cache_manager = get_cache_manager()
        if cache_manager:
            cache_manager.clear_expired()

    scheduler.add_task("cache_cleanup", cleanup_cache, interval_hours=6)

    return scheduler


# Global scheduler instance
global_scheduler: TaskScheduler | None = None


def init_scheduler(finance_agent) -> TaskScheduler:
    """Initialize global scheduler"""
    global global_scheduler
    global_scheduler = setup_scheduler(finance_agent)
    return global_scheduler


def get_scheduler() -> TaskScheduler | None:
    """Get global scheduler instance"""
    return global_scheduler
