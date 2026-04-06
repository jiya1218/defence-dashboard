import requests
import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
import pytz

BASE_URL = "https://bolpatra.gov.np/egp/searchBidDashboardHomePage"
FILE_NAME = "nepal_tenders.xlsx"

KEYWORDS = ["Unmanned aerial vehicle" , "missiles", "counter drones" , "anti drones" , "loitering munitions" , "suicidal drones" , "drones" , "MicroUAV" , "small arms" , "ammunitions"]
PAGES_TO_SCAN = 4

IST = pytz.timezone("Asia/Kolkata")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# FETCH FUNCTION
# ===============================
def fetch_page(keyword, page):

    params = {
        "bidSearchTO.title": keyword,
        "currentPageIndex": page,
        "pageSize": 30
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    response = requests.get(BASE_URL, params=params, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")
    data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 8:
            record = {
                "Tender No": cols[1].text.strip(),
                "Project Title": cols[2].text.strip(),
                "Public Entity": cols[3].text.strip(),
                "Procurement Method": cols[4].text.strip(),
                "Status": cols[5].text.strip(),
                "Published Date": cols[6].text.strip(),
                "Deadline": cols[7].text.strip(),
                "Keyword": keyword
            }
            data.append(record)

    return data

# ===============================
# MAIN SCRAPER FUNCTION
# ===============================
def run_scraper(user_keywords, progress_callback=None):

    all_keywords = list(dict.fromkeys(KEYWORDS + user_keywords))
    all_records = []

    total_steps = len(all_keywords) * PAGES_TO_SCAN
    current_step = 0

    for keyword in all_keywords:
        keyword_lower = keyword.lower()

        for page in range(1, PAGES_TO_SCAN + 1):

            try:
                page_data = fetch_page(keyword, page)

                now = datetime.now(IST)
                scrape_date = now.strftime("%Y-%m-%d")
                scrape_time = now.strftime("%H:%M:%S")

                for row in page_data:

                    # 🔥 STRICT MATCH (ONLY ADDITION)
                    title = str(row.get("Project Title", "")).lower()
                    if keyword_lower not in title:
                        continue

                    row["Scraping Date"] = scrape_date
                    row["Scraping Time"] = scrape_time
                    row["Source"] = "Nepal"
                    all_records.append(row)

            except:
                continue

            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, keyword, page)

            time.sleep(0.5)

    new_df = pd.DataFrame(all_records)

    if new_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    new_df["Tender No"] = new_df["Tender No"].astype(str)
    new_df["Deadline"] = new_df["Deadline"].astype(str)
    new_df = new_df.drop_duplicates(subset=["Tender No", "Deadline"])

    if os.path.exists(FILE_NAME):
        old_df = pd.read_excel(FILE_NAME)
        old_df["Tender No"] = old_df["Tender No"].astype(str)
        old_df["Deadline"] = old_df["Deadline"].astype(str)
        old_df = old_df.drop_duplicates(subset=["Tender No", "Deadline"])
    else:
        old_df = pd.DataFrame()

    if not old_df.empty:
        old_keys = set(zip(old_df["Tender No"], old_df["Deadline"]))
        new_df["key"] = list(zip(new_df["Tender No"], new_df["Deadline"]))
        new_unique = new_df[~new_df["key"].isin(old_keys)].drop(columns=["key"])
    else:
        new_unique = new_df

    combined = pd.concat([old_df, new_unique], ignore_index=True)
    combined = combined.drop_duplicates(subset=["Tender No", "Deadline"])
    combined.to_excel(FILE_NAME, index=False)

    return combined, new_unique