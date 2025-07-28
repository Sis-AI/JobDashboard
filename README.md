# Job Scraper & Dashboard

## Overview

This repository contains:

* **Job Scraper**: Python script for scraping Data Scientist job postings from LinkedIn and JobMaster, saving them into a CSV file.
* **Scheduler**: Optional script to automatically run the scraper every 24 hours.
* **Interactive Dashboard**: A Streamlit dashboard for visualizing and filtering job data.

---

## How It Works

### Scraper

The scraper:

1. Sends HTTP requests to LinkedIn and JobMaster job listing pages.
2. Parses HTML using **BeautifulSoup** to extract job title, company name, location, date posted, and URL.
3. Converts relative posting dates (e.g., “3 days ago”) to actual dates.
4. Saves all collected jobs into `data_scientist_jobs.csv`, avoiding duplicates.

### Dashboard

The dashboard (built with **Streamlit**) allows you to:

* Load job data from the CSV.
* Filter jobs by company, location, and posting date range.
* View trends with:

  * **Line Chart**: Number of open positions over time by posting date.
  * **Bar Chart**: Job counts by location.
* Explore all job listings in an interactive table with clickable links.
* Auto-refreshes data caching every hour (or on page reload).

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Sis-AI/JobDashboard.git
cd JobDashboard
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # On Linux/macOS
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Run the Scraper Manually

```bash
python job_scraper.py
```

This will create or update `data_scientist_jobs.csv` with the latest job listings.

### Run the Dashboard

```bash
streamlit run app.py
```

Then open the link provided by Streamlit in your browser (e.g., [http://localhost:8501](http://localhost:8501)).

### Run the Scheduler (Optional)

The scheduler runs the scraper automatically every 24 hours:

```bash
python daily_scheduler.py
```

Keep this running in the background (or use tools like `screen`, `tmux`, `nohup`, or set up a cron job/systemd service).

---

## CSV Output Structure

The CSV (`data_scientist_jobs.csv`) contains the following columns:

* `job_title`
* `company_name`
* `location`
* `date_posted`
* `url`
* `source`
* `scraped_at`

---

## Notes

* Make sure you have Python 3.8+ installed.
* LinkedIn scraping may have limitations or require adjusting the script if HTML structure changes.
* The dashboard automatically caches data for one hour for performance; refresh the page or wait for cache expiry to see new updates.
