import time
import csv
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

REQUIRED_KEYWORDS = {"Bangalore", "Bengaluru"}
ROLE = "workday finance consultant"
WORKDAY_COMPANIES_FILENAME = "companies.csv"

def filter_job_urls(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(), options=chrome_options)
        driver.get(url)
        time.sleep(5)

        page_source = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page_source, "html.parser")
        page_text = soup.get_text(separator=" ", strip=True).lower()

        if any(keyword.lower() in page_text for keyword in REQUIRED_KEYWORDS):
            print(f"✅ Job listing found: {url}")
            return True
        else:
            print(f"❌ Skipping {url} (no matching keywords)")
            return False

    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return None

def filter_job(results, location):
    """
    Filter job search results for those that mention the specified location (e.g., Bangalore).
    """
    filtered = []
    for result in results:
        # Check if the location is mentioned in the job body or title
        if location.lower() in result['body'].lower() or location.lower() in result['title'].lower():
            filtered.append(result)
    return filtered

def search_company_jobs(company, role, location):
    query = f"{company} {role} {location}"
    print(f"🔍 Searching: {query}")

    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=10)
        return [result['href'] for result in results if filter_job_urls(result['href'])]
    except Exception as e:
        print(f"⚠️ Error: {e}")

# Run job search & save results to CSV
def search_job():
    # Read the CSV with company names and URLs (first and second columns)
    companies = pd.read_csv(WORKDAY_COMPANIES_FILENAME, skiprows=1, header=None)[0]
    csv_filename = "job_search_results.csv"

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Company", "URL", "Job Links"])  # CSV Header

        for company in companies:
            print(f"🔍 Searching for jobs at: {company}")
            job_links = search_company_jobs(company, ROLE, "bangalore")

            if job_links:
                for link in job_links:
                    writer.writerow([company, link])
            else:
                writer.writerow([company, "No jobs found"])

            time.sleep(10)

    print(f"\n✅ Data saved to {csv_filename}")

if __name__ == "__main__":
    search_job()
    # search_company_jobs("pwc",  "workday finance consultant", "bangalore")
