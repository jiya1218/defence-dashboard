import requests
import json
import pandas as pd
import os
import time
from datetime import datetime
import pytz

# ===============================
# SETTINGS
# ===============================

MAIN_URL = "https://bidplus.gem.gov.in/all-bids"
API_URL = "https://bidplus.gem.gov.in/all-bids-data"

FILE_NAME = "gem_tenders.xlsx"

KEYWORDS = [
    "Unmanned aerial vehicle", "missiles", "counter drones", "anti drones",
    "loitering munitions", "suicidal drones", "drones", "MicroUAV",
    "small arms", "ammunitions"
]

PAGES_PER_KEYWORD = 10
india_tz = pytz.timezone("Asia/Kolkata")

# ===============================
# MAIN FUNCTION
# ===============================

def run_scraper(user_keywords, update_source="Manual", progress_callback=None):

    all_keywords = list(dict.fromkeys(KEYWORDS + user_keywords))

    session = requests.Session()
    session.get(MAIN_URL)

    csrf_token = session.cookies.get("csrf_gem_cookie")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://bidplus.gem.gov.in",
        "Referer": "https://bidplus.gem.gov.in/all-bids"
    }

    all_records = []

    total_steps = len(all_keywords) * PAGES_PER_KEYWORD
    current_step = 0

    # ===============================
    # SCRAPING
    # ===============================
    for keyword in all_keywords:
        keyword_lower = keyword.lower()

        for page in range(1, PAGES_PER_KEYWORD + 1):

            payload_json = {
                "param": {
                    "searchBid": keyword,
                    "searchType": "fullText"
                },
                "filter": {
                    "bidStatusType": "ongoing_bids",
                    "byType": "all",
                    "highBidValue": "",
                    "byEndDate": {"from": "", "to": ""},
                    "sort": "Bid-End-Date-Oldest"
                },
                "page": page
            }

            data = {
                "payload": json.dumps(payload_json),
                "csrf_bd_gem_nk": csrf_token
            }

            try:
                response = session.post(API_URL, headers=headers, data=data, timeout=10)

                if response.status_code != 200:
                    continue

                result = response.json()
                docs = result["response"]["response"]["docs"]

                for bid in docs:

                    # 🔥 STRICT MATCH CHECK
                    title = (
                        str(bid.get("b_category_name", [""])[0]) + " " +
                        str(bid.get("bd_category_name", [""])[0])
                    ).lower()

                    if keyword_lower not in title:
                        continue

                    now = datetime.now(india_tz)

                    record = {
                        "Keyword": keyword,
                        "Bid ID": str(bid.get("b_id", [""])[0]),
                        "Bid Number": bid.get("b_bid_number", [""])[0],
                        "Category Name": bid.get("b_category_name", [""])[0],
                        "Start Date": str(bid.get("final_start_date_sort", [""])[0]),
                        "End Date": str(bid.get("final_end_date_sort", [""])[0]),
                        "Full Category Details": bid.get("bd_category_name", [""])[0],
                        "Quantity": bid.get("b_total_quantity", [""])[0],
                        "Ministry": bid.get("ba_official_details_minName", [""])[0],
                        "Department": bid.get("ba_official_details_deptName", [""])[0],
                        "Bid Type": bid.get("b_bid_type", [""])[0],
                        "Update Source": update_source, # <--- Fix applied here
                        "Scraped Date": now.strftime("%Y-%m-%d"),
                        "Scraped Time (IST)": now.strftime("%H:%M:%S")
                    }

                    all_records.append(record)

            except:
                continue

            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, keyword, page)

            time.sleep(0.5)

    new_df = pd.DataFrame(all_records)

    if new_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    new_df["Bid Number"] = new_df["Bid Number"].astype(str)
    new_df["End Date"] = new_df["End Date"].astype(str)

    new_df = new_df.drop_duplicates(subset=["Bid Number", "End Date"])

    if os.path.exists(FILE_NAME):
        old_df = pd.read_excel(FILE_NAME)
        old_df["Bid Number"] = old_df["Bid Number"].astype(str)
        old_df["End Date"] = old_df["End Date"].astype(str)
        old_df = old_df.drop_duplicates(subset=["Bid Number", "End Date"])
    else:
        old_df = pd.DataFrame()

    if not old_df.empty:
        old_keys = set(zip(old_df["Bid Number"], old_df["End Date"]))
        new_df["key"] = list(zip(new_df["Bid Number"], new_df["End Date"]))
        new_unique = new_df[~new_df["key"].isin(old_keys)].drop(columns=["key"])
    else:
        new_unique = new_df

    combined = pd.concat([old_df, new_unique], ignore_index=True)
    combined = combined.drop_duplicates(subset=["Bid Number", "End Date"])
    combined.to_excel(FILE_NAME, index=False)

    return combined, new_unique

# Add this at the very end of gem_backend.py
if __name__ == "__main__":
    print("Windows Task Scheduler started the update...")
    # This runs the scraper with 'Auto' as the source
    run_scraper(user_keywords=[], update_source="Auto")
    print("Update Complete. Excel file updated.")
