import requests
import pandas as pd
import time
import os
from datetime import datetime
import pytz

# ===============================
# CONFIG
# ===============================

API_URL = "https://tedweb.api.ted.europa.eu/private-search/api/v1/notices/search"
FILE_NAME = "EU_TED_Tenders.xlsx"

KEYWORDS = ["Unmanned aerial vehicle" , "missiles", "counter drones" , "anti drones" , "loitering munitions" , "suicidal drones" , "drones" , "MicroUAV" , "small arms" , "ammunitions"]

PAGES_TO_SCAN = 8
LIMIT_PER_PAGE = 100

IST = pytz.timezone("Asia/Kolkata")

# ===============================
# TIME CONVERSION
# ===============================
def convert_to_ist(date_string):
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.astimezone(IST).replace(tzinfo=None)
    except:
        return None

# ===============================
# HEADERS
# ===============================
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://ted.europa.eu",
    "referer": "https://ted.europa.eu/",
    "user-agent": "Mozilla/5.0"
}

# ===============================
# FETCH
# ===============================
def fetch_data(keyword, page):
    payload = {
        "query": f"(FT ~ ({keyword})) SORT BY publication-number DESC",
        "page": page,
        "limit": LIMIT_PER_PAGE,
        "fields": [
            "publication-number","notice-title","buyer-name",
            "buyer-country","publication-date",
            "deadline-receipt-request","procedure-type",
            "contract-nature","place-of-performance"
        ],
        "scope": "ALL",
        "language": "EN"
    }

    try:
        r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
        if r.status_code != 200:
            return []
        return parse_data(r.json().get("notices", []), keyword)
    except:
        return []

# ===============================
# PARSE
# ===============================
def parse_data(notices, keyword):
    records = []
    keyword_lower = keyword.lower()

    for notice in notices:
        try:
            title = notice.get("notice-title")
            if isinstance(title, dict):
                title = title.get("eng")

            if not title or keyword_lower not in str(title).lower():
                continue

            pub_no = str(notice.get("publication-number")).strip()
            # --- CONSTRUCT TENDER LINK ---
            tender_link = f"https://ted.europa.eu/en/notice/-/detail/{pub_no}"

            buyer = notice.get("buyer-name")
            if isinstance(buyer, dict):
                buyer = list(buyer.values())[0][0]

            country = notice.get("buyer-country")
            if isinstance(country, list) and country:
                if isinstance(country[0], dict):
                    country = country[0].get("label")

            pub_date = convert_to_ist(notice.get("publication-date"))

            deadline = None
            dr = notice.get("deadline-receipt-request")
            if isinstance(dr, list) and dr:
                deadline = convert_to_ist(dr[0])

            procedure = notice.get("procedure-type")
            if isinstance(procedure, list) and procedure:
                p = procedure[0]
                procedure = p.get("label") if isinstance(p, dict) else str(p)
            elif isinstance(procedure, dict):
                procedure = procedure.get("label")

            contract = notice.get("contract-nature")
            if isinstance(contract, list) and contract:
                c = contract[0]
                contract = c.get("label") if isinstance(c, dict) else str(c)
            elif isinstance(contract, dict):
                contract = contract.get("label")

            place = notice.get("place-of-performance")
            if isinstance(place, list):
                places = [p.get("label") for p in place if isinstance(p, dict) and p.get("label")]
                place = ", ".join(sorted(set(places)))

            now = datetime.now(IST)

            records.append({
                "Title": title,
                "Ref No": pub_no,
                "Tender Link": tender_link,
                "Deadline": deadline,
                "Location": country,
                "Funding": "",
                "Industry": contract,
                "Posted Date": pub_date,
                "Keyword": keyword,
                "Buyer Name": buyer,
                "Procedure Type": procedure,
                "Place of Performance": place,
                "Scraped Date": now.strftime("%Y-%m-%d"),
                "Scraped Time (IST)": now.strftime("%H:%M:%S")
            })
        except:
            pass
    return records

# ===============================
# MAIN
# ===============================
def run_scraper(user_keywords, update_source="Manual", progress_callback=None):
    all_keywords = list(dict.fromkeys(KEYWORDS + user_keywords))
    all_data = []

    total_steps = len(all_keywords) * PAGES_TO_SCAN
    current_step = 0

    for keyword in all_keywords:
        for page in range(1, PAGES_TO_SCAN + 1):
            data = fetch_data(keyword, page)
            if not data:
                break
            
            for item in data:
                item["Update Source"] = update_source

            all_data.extend(data)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, keyword, page)
            time.sleep(0.3)

    new_df = pd.DataFrame(all_data)
    if new_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    new_df["Ref No"] = new_df["Ref No"].astype(str).str.strip()
    new_df["Deadline"] = pd.to_datetime(new_df["Deadline"], errors="coerce").astype(str)

    if os.path.exists(FILE_NAME):
        old_df = pd.read_excel(FILE_NAME)
        if not old_df.empty:
            old_df["Ref No"] = old_df["Ref No"].astype(str).str.strip()
            old_df["Deadline"] = pd.to_datetime(old_df["Deadline"], errors="coerce").astype(str)
            combined = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates(subset=["Ref No", "Deadline"], keep='last')
        else:
            combined = new_df
    else:
        combined = new_df

    combined.to_excel(FILE_NAME, index=False)
    return combined, new_df

# --- SCHEDULER LOGIC ---
if __name__ == "__main__":
    print("--- TED Backend: Starting Auto Update ---")
    run_scraper([], update_source="Auto")
    print("--- Update Finished ---")
