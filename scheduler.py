import time
import logging
from scraper import JobScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_scraper_once():
    scraper = JobScraper()
    count = scraper.run_collection(limit=200)
    logger.info(f"Scraped {count} jobs and saved to CSV.")

if __name__ == "__main__":
    while True:
        run_scraper_once()
        # Sleep for 24 hours (86400 seconds)
        logger.info("Sleeping for 24 hours before next run...")
        time.sleep(86400)
