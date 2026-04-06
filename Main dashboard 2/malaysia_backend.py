import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz
import time
import threading

URL = "https://www.bidsinfo.net/elasticsearch/elastic_cron/search_result.php"
FILE_NAME = "bidsinfo_tenders.xlsx"

KEYWORDS = [
    "Unmanned aerial vehicle", "missiles", "counter drones",
    "anti drones", "loitering munitions", "suicidal drones",
    "drones", "MicroUAV", "small arms", "ammunitions"
]

PAGES_TO_SCAN = 4
india_tz = pytz.timezone("Asia/Kolkata")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.bidsinfo.com",
    "Referer": "https://www.bidsinfo.com/advance-search"
}

# ---------------- FETCH ----------------
def fetch_data(keyword, page):
    payload = {
        "a_refno": "",
        "a_keyword": keyword,
        "a_region": "",
        "a_subregion": "",
        "a_location": "MY",
        "a_funding": "",
        "a_industry": "",
        "a_postdate": "",
        "a_deadline": "",
        "viewperpage": "100",
        "page": page
    }

    try:
        response = requests.post(URL, headers=HEADERS, data=payload, timeout=10)
        data = response.json()
        html = data.get("result", "")
        return parse_html(html, keyword)
    except:
        return []

# ---------------- PARSE ----------------
def parse_html(html, keyword):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("article", class_="card")
    tenders = []

    for card in cards:
        try:
            title = card.find("h2").text.strip()
            title_lower = title.lower()
            keyword_words = keyword.lower().split()

            if not all(word in title_lower for word in keyword_words):
                continue

            ref_deadline = card.find("p", class_="card-subtitle").text
            ref_no = ref_deadline.split("|")[0].replace("BI Ref.:", "").strip()
            deadline = ref_deadline.split("Deadline:")[-1].strip()

            # --- CONSTRUCT TENDER LINK ---
            slug = title.lower().replace(" ", "-").replace(",", "").replace("/", "-")
            tender_link = f"https://www.bidsinfo.com/ref/{ref_no}/{slug}"

            location, funding, industry, posted = "", "", "", ""
            for small in card.find_all("small"):
                text = small.text.strip()
                if "Location:" in text: location = text.split("Location:")[-1].strip()
                if "Funding:" in text: funding = text.split("Funding:")[-1].split("|")[0].strip()
                if "Industry:" in text: industry = text.split("Industry:")[-1].strip()
                if "Posted:" in text: posted = text.split("Posted:")[-1].strip()

            now = datetime.now(india_tz)

            tenders.append({
                "Title": title,
                "Ref No": ref_no,
                "Tender Link": tender_link,
                "Deadline": deadline,
                "Location": location,
                "Funding": funding,
                "Industry": industry,
                "Posted Date": posted,
                "Keyword": keyword,
                "Scraped Date": now.strftime("%Y-%m-%d"),
                "Scraped Time (IST)": now.strftime("%H:%M:%S")
            })
        except:
            pass
    return tenders

# ---------------- FINAL FUNCTION ----------------
def run_scraper(user_keywords, update_source="Manual", progress_callback=None):
    # Ensure every keyword in the list is searched
    all_keywords = list(dict.fromkeys(KEYWORDS + user_keywords))
    all_data = []
    total_steps = len(all_keywords) * PAGES_TO_SCAN
    current_step = 0

    for keyword in all_keywords:
        for page in range(1, PAGES_TO_SCAN + 1):
            data = fetch_data(keyword, page)
            if not data: 
                current_step += 1
                continue
            
            # Tag the source (Auto or Manual)
            for item in data:
                item["Update Source"] = update_source

            all_data.extend(data)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, keyword, page)
            time.sleep(0.3)

    columns = [
        "Title", "Ref No", "Tender Link", "Deadline", "Location", "Funding",
        "Industry", "Posted Date", "Keyword", "Update Source",
        "Scraped Date", "Scraped Time (IST)"
    ]

    new_df = pd.DataFrame(all_data, columns=columns)

    if not new_df.empty:
        new_df["Ref No"] = new_df["Ref No"].astype(str).str.strip()
        new_df["Deadline"] = pd.to_datetime(new_df["Deadline"], errors="coerce")
        new_df = new_df.dropna(subset=["Ref No", "Deadline"])
        new_df = new_df.drop_duplicates(subset=["Ref No", "Deadline"])

    if os.path.exists(FILE_NAME):
        old_df = pd.read_excel(FILE_NAME)
        if not old_df.empty:
            old_df.columns = old_df.columns.str.strip()
            if "Ref No" in old_df.columns and "Deadline" in old_df.columns:
                old_df["Ref No"] = old_df["Ref No"].astype(str).str.strip()
                old_df["Deadline"] = pd.to_datetime(old_df["Deadline"], errors="coerce")
                old_df = old_df.dropna(subset=["Ref No", "Deadline"])
                old_df = old_df.drop_duplicates(subset=["Ref No", "Deadline"])
            else:
                old_df = pd.DataFrame(columns=columns)
        else:
            old_df = pd.DataFrame(columns=columns)
    else:
        old_df = pd.DataFrame(columns=columns)

    if not new_df.empty and not old_df.empty:
        new_unique = new_df[~new_df.set_index(["Ref No", "Deadline"]).index.isin(old_df.set_index(["Ref No", "Deadline"]).index)]
    else:
        new_unique = new_df

    combined = pd.concat([old_df, new_unique], ignore_index=True)
    combined.to_excel(FILE_NAME, index=False)
    return combined, new_unique

# --- SCHEDULER LOGIC ---
if __name__ == "__main__":
    print("--- Malaysia Backend: Starting Auto Update ---")
    run_scraper([], update_source="Auto")
    print("--- Update Finished ---")
