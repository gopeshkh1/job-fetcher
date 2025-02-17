import time
import csv
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import random

JOB_PORTALS_FILENAME = "workday_companies_job_portal.csv"
WORKDAY_COMPANIES_FILENAME = "companies.csv"

def save_to_csv(csv_filename, data, headers):
    """Save data to a CSV file. Prevents duplicate headers."""
    file_exists = False
    try:
        with open(csv_filename, "r", encoding="utf-8") as file:
            file_exists = True
    except FileNotFoundError:
        pass  # File does not exist, will be created

    with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(headers)  # Write headers only for new files

        for row in data:
            writer.writerow(row)


def read_companies(csv_filename):
    """Read existing companies from CSV to avoid duplicate searches."""
    existing_companies = set()
    try:
        with open(csv_filename, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                existing_companies.add(row[0])
    except FileNotFoundError:
        print(f"⚠️ {csv_filename} not found. A new one will be created.")
    return existing_companies


def search_career_page(company):
    """Search for a company's career page using DuckDuckGo with retries."""
    query = f"{company} careers site OR jobs OR recruitment"
    retries = 5
    delay = 5  # Initial delay

    for attempt in range(retries):
        try:
            results = DDGS().text(query, max_results=10)
            for result in results:
                url = result["href"]
                if "career" in url.lower() or "jobs" in url.lower():
                    return url
            return "Not Found"
        except Exception as e:
            print(f"⚠️ Error searching for {company}: {e}")
            if attempt < retries - 1:
                print(f"🔄 Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"❌ Max retries reached for {company}. Skipping.")
                return "Error"

        time.sleep(random.randint(3, 7))  # Random delay to prevent rate limiting


def get_career_pages():
    """Fetch career pages for companies and save them to CSV."""
    companies = fetch_companies()
    existing_companies = read_companies(JOB_PORTALS_FILENAME)
    career_pages = []

    for company in companies:
        if company in existing_companies:
            print(f"✅ Skipping {company} (already in CSV)")
            continue

        print(f"🔍 Searching career page for: {company}")
        career_page = search_career_page(company)
        career_pages.append([company, career_page])

    save_to_csv(JOB_PORTALS_FILENAME, career_pages, ["Company", "Job Links"])
    print(f"✅ Saved {len(career_pages)} new career pages to {JOB_PORTALS_FILENAME}")

    return career_pages


def fetch_companies():
    """Fetch Workday service partner companies and save them to CSV."""
    url = "https://api.mktg.workday.com/v2/search/partner/en-us"
    params = {"filters": "type", "type": "Services Partner"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        companies = [
            c["_source"].get("name", "Unknown")
            for c in data.get("hits", {}).get("hits", [])
        ]

        # Avoid duplicate company entries
        existing_companies = read_companies(WORKDAY_COMPANIES_FILENAME)
        new_companies = [[company] for company in companies if company not in existing_companies]

        if new_companies:
            save_to_csv(WORKDAY_COMPANIES_FILENAME, new_companies, ["Company"])
            print(f"✅ Added {len(new_companies)} new companies to {WORKDAY_COMPANIES_FILENAME}")

        return companies

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return []

if __name__ == "__main__":
    fetch_companies()
