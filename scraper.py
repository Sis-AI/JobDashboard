import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime, timedelta
import csv
import os
from urllib.parse import urljoin, quote_plus
import logging

# Configure logging to show timestamp, log level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraper:
    """Data Scientist Job Scraper for Israel"""
    def __init__(self, csv_file='data_scientist_jobs.csv'):
        # Initialize scraper with a CSV output file path
        self.csv_file = csv_file
        self.jobs = []  # List to store collected job entries
        # HTTP headers to mimic a browser and avoid blocks
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        # If the CSV file does not exist, create it with headers
        if not os.path.exists(self.csv_file):
            self._init_csv()

    def _init_csv(self):
        """Initialize a CSV file with column headers"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'job_title', 'company_name', 'location',
                'date_posted', 'url', 'source', 'scraped_at'
            ])

    def scrape_linkedin_jobs(self, keywords="Data Scientist", location="Israel", limit=25):
        """Scrape jobs from LinkedIn job search"""
        logger.info("Scraping LinkedIn jobs...")
        base = "https://www.linkedin.com/jobs/search"
        # Build search URL with encoded parameters
        url = (
            f"{base}?keywords={quote_plus(keywords)}"
            f"&location={quote_plus(location)}&f_TPR=r86400"
        )
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            time.sleep(random.uniform(2, 4))  # Delay to avoid triggering anti-bot
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            # LinkedIn job postings are inside divs with these classes
            cards = soup.find_all('div', class_=['job-search-card', 'base-card'])
            for card in cards[:limit]:
                # Extract basic job info
                title = card.select_one('h3')
                company = card.select_one('h4')
                loc = card.select_one('.job-search-card__location')
                date_span = card.find('time')  # Contains datetime attribute for posting date
                link = card.find('a', href=True)
                if not title or not company:
                    continue  # Skip invalid entries
                # Parse date posted or default to now
                raw_date = date_span['datetime'][:10] if date_span and date_span.has_attr('datetime') else ''
                try:
                    posted = datetime.strptime(raw_date, '%Y-%m-%d')
                except Exception:
                    posted = datetime.now()
                # Construct job dictionary
                job = {
                    'job_title': title.get_text(strip=True),
                    'company_name': company.get_text(strip=True),
                    'location': loc.get_text(strip=True) if loc else location,
                    'date_posted': posted.strftime('%Y-%m-%d'),
                    'url': urljoin('https://www.linkedin.com', link['href']) if link else url,
                    'source': 'LinkedIn',
                    'scraped_at': datetime.now().isoformat()
                }
                self.jobs.append(job)
                logger.info(f"LinkedIn: {job['job_title']}")
        except Exception as e:
            logger.error(f"LinkedIn error: {e}")

    def scrape_jobmaster(self, keywords="Data Scientist", limit=20):
        """Scrape jobs from JobMaster.co.il"""
        logger.info("Scraping JobMaster.co.il...")
        url = ("https://www.jobmaster.co.il/jobs/?"
               f"q={quote_plus(keywords)}&l=")
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            time.sleep(random.uniform(2, 4))
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            anchors = soup.find_all('a', href=True)  # All anchors for filtering jobs
            count = 0
            for a in anchors:
                href = a['href']
                if not href.startswith('/jobs/'):  # Skip non-job links
                    continue
                title = a.get_text(strip=True)
                # Try to find company name in related elements
                comp_elem = a.find_previous().select_one("div a span")
                company = comp_elem.get_text(strip=True) if comp_elem else 'unknown'
                if not title:
                    continue
                full_url = urljoin('https://www.jobmaster.co.il', href)
                # Find posting date text near the link
                dt_text = ''
                dt = a.find_next(string=re.compile(r'פורסם'))
                if dt:
                    dt_text = dt.strip()
                now = datetime.now()
                date_posted = now.strftime('%Y-%m-%d')
                # Convert relative Hebrew date (e.g., 'לפני 3 ימים') into actual date
                if 'לפני' in dt_text:
                    num = int(re.search(r"\d+", dt_text).group())
                    if 'שעה' in dt_text:
                        posted = now - timedelta(hours=num)
                    elif 'יום' in dt_text:
                        posted = now - timedelta(days=num)
                    else:
                        posted = now
                    date_posted = posted.strftime('%Y-%m-%d')
                # Find location info from following <ul>
                location = 'Israel'
                ul = a.find_next('ul')
                if ul:
                    items = [li.get_text(strip=True) for li in ul.find_all('li')]
                    if items:
                        location = items[0]
                # Construct job dictionary
                job = {
                    'job_title': title,
                    'company_name': company,
                    'location': location,
                    'date_posted': date_posted,
                    'url': full_url,
                    'source': 'JobMaster',
                    'scraped_at': now.isoformat()
                }
                self.jobs.append(job)
                logger.info(f"JobMaster: {title}")
                count += 1
                if count >= limit:  # Stop when reaching limit
                    break
        except Exception as e:
            logger.error(f"JobMaster error: {e}")

    def remove_duplicates(self):
        """Remove duplicate job postings based on title, company, and URL"""
        seen = set()
        unique = []
        for job in self.jobs:
            key = (job['job_title'].lower(), job['company_name'].lower(), job['url'])
            if key not in seen:
                seen.add(key)
                unique.append(job)
        self.jobs = unique
        logger.info(f"Deduplicated: {len(self.jobs)} jobs")

    def save_to_csv(self):
        """Save scraped jobs to CSV while avoiding duplicates with existing file"""
        if not self.jobs:
            logger.info("No jobs to save.")
            return
        existing = set()
        if os.path.exists(self.csv_file):
            try:
                df_exist = pd.read_csv(self.csv_file)
                for _, r in df_exist.iterrows():
                    existing.add((r['job_title'].lower(), r['company_name'].lower(), r['url']))
            except Exception:
                pass  # Ignore CSV read errors
        # Filter out already existing jobs
        new = [j for j in self.jobs if (j['job_title'].lower(), j['company_name'].lower(), j['url']) not in existing]
        if new:
            df = pd.DataFrame(new)
            df.to_csv(self.csv_file, mode='a', header=not os.path.exists(self.csv_file), index=False)
            logger.info(f"Saved {len(new)} jobs")
        else:
            logger.info("No new jobs to save.")

    def run_collection(self, limit=25):
        """Run the whole scraping process for all sources"""
        self.jobs = []
        self.scrape_linkedin_jobs(limit=limit)
        self.scrape_jobmaster(limit=limit)
        self.remove_duplicates()
        self.save_to_csv()
        return len(self.jobs)

if __name__ == "__main__":
    scraper = JobScraper()
    count = scraper.run_collection(limit=200)
    print(f"Found {count} jobs. Data saved to {scraper.csv_file}.")
