# vietnam_backend.py

import requests
import urllib3
import ssl
import pandas as pd
import time
import os
from datetime import datetime
from requests.adapters import HTTPAdapter
from deep_translator import GoogleTranslator
import pytz

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount("https://", TLSAdapter())

URL = "https://muasamcong.mpi.gov.vn/o/egp-portal-contractor-selection-v2/services/smart/search"
TOKEN = "PASTE_YOUR_REAL_TOKEN"
FILE_NAME = "vietnam_tenders.xlsx"
MAX_PAGES = 2

KEYWORDS_EN = ["Unmanned aerial vehicle" , "missiles", "counter drones" , "anti drones" , "loitering munitions" , "suicidal drones" , "drones" , "MicroUAV" , "small arms" , "ammunitions"]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

translator_vi_to_en = GoogleTranslator(source='vi', target='en')
translator_en_to_vi = GoogleTranslator(source='en', target='vi')

IST = pytz.timezone("Asia/Kolkata")

def improve_translation_input(text):
    text = text.lower().strip()

    replacements = {
        "counter drone": "counter drone system",
        "counter drones": "counter drone system",
        "anti drone": "anti drone system",
        "anti drones": "anti drone system",
        "loitering munition": "loitering munition weapon",
        "loitering munitions": "loitering munition weapon",
        "suicide drone": "suicide drone weapon",
        "suicidal drones": "suicide drone weapon",
        "uav": "unmanned aerial vehicle",
        "microuav": "small unmanned aerial vehicle",
        "small arms": "light weapons",
        "ammunitions": "military ammunition"
    }

    return replacements.get(text, text)

def convert_to_ist(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
        dt_ist = pytz.utc.localize(dt).astimezone(IST)
        return dt_ist.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return date_str

def convert_to_usd(value):
    try:
        if value:
            return round(float(value) / 24000, 2)
    except:
        pass
    return None

def fetch_data(keyword_en, progress_callback=None, current_step=0, total_steps=1):

    try:
        improved_keyword = improve_translation_input(keyword_en)
        keyword_vi = translator_en_to_vi.translate(improved_keyword)
    except:
        keyword_vi = keyword_en

    all_rows = []

    for page in range(MAX_PAGES):

        payload = [{
            "pageSize": 10,
            "pageNumber": page,
            "query": [{
                "index": "es-contractor-selection",
                "keyWord": keyword_vi,
                "matchType": "all-1",
                "matchFields": ["notifyNo", "bidName"],
                "filters": [
                    {"fieldName": "type", "searchType": "in", "fieldValues": ["es-notify-contractor"]},
                    {"fieldName": "caseKHKQ", "searchType": "not_in", "fieldValues": ["1"]}
                ]
            }]
        }]

        try:
            response = session.post(URL, headers=HEADERS, params={"token": TOKEN}, json=payload, verify=False, timeout=30)
            data = response.json()
            records = data.get("page", {}).get("content", [])

            if not records:
                break

            now_ist = datetime.now(IST)
            scrape_date = now_ist.strftime("%Y-%m-%d")
            scrape_time = now_ist.strftime("%H:%M:%S")

            for item in records:
                title_vi = " ".join(item.get("bidName", []))
                entity_vi = item.get("investorName", "")

                try:
                    title_en = translator_vi_to_en.translate(title_vi)
                except:
                    title_en = title_vi

                # 🔥 STRICT MATCH ON ENGLISH TITLE (ONLY ADDITION)
                if keyword_en.lower() not in str(title_en).lower():
                    continue

                try:
                    entity_en = translator_vi_to_en.translate(entity_vi)
                except:
                    entity_en = entity_vi

                locations = item.get("locations", [])
                province_vi = locations[0].get("provName") if locations else ""

                try:
                    province_en = translator_vi_to_en.translate(province_vi) if province_vi else ""
                except:
                    province_en = province_vi

                raw_value = item.get("bidPrice", [None])[0]
                value_usd = convert_to_usd(raw_value)
                close_date = item.get("bidCloseDate")

                status_flag = "Active"
                if close_date:
                    try:
                        if datetime.strptime(close_date[:10], "%Y-%m-%d") < datetime.utcnow():
                            status_flag = "Closed"
                    except:
                        pass

                row = {
                    "Tender ID": item.get("notifyNo"),
                    "Title (EN)": title_en,
                    "Entity (EN)": entity_en,
                    "Province (EN)": province_en,
                    "Publish Date (IST)": convert_to_ist(item.get("publicDate")),
                    "Closing Date (IST)": convert_to_ist(close_date),
                    "Value (USD)": value_usd,
                    "Status": status_flag,
                    "Country": "Vietnam",
                    "Keyword EN": keyword_en,
                    "Keyword VI": keyword_vi,
                    "Scraping Date": scrape_date,
                    "Scraping Time": scrape_time
                }

                all_rows.append(row)

        except:
            pass

        if progress_callback:
            progress_callback(current_step + page + 1, total_steps, keyword_en, page + 1)

        time.sleep(2)

    return all_rows

def run_scraper(user_keywords=[], progress_callback=None):

    all_records = []
    all_keywords = list(dict.fromkeys(KEYWORDS_EN + user_keywords))

    total_steps = len(all_keywords) * MAX_PAGES
    current_step = 0

    for kw in all_keywords:
        data = fetch_data(kw, progress_callback, current_step, total_steps)
        all_records.extend(data)
        current_step += MAX_PAGES

    new_df = pd.DataFrame(all_records)

    if new_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    new_df["Tender ID"] = new_df["Tender ID"].astype(str)
    new_df["Closing Date (IST)"] = new_df["Closing Date (IST)"].astype(str)

    new_df = new_df.drop_duplicates(subset=["Tender ID", "Closing Date (IST)"])

    if os.path.exists(FILE_NAME):
        old_df = pd.read_excel(FILE_NAME)

        old_df["Tender ID"] = old_df["Tender ID"].astype(str)
        old_df["Closing Date (IST)"] = old_df["Closing Date (IST)"].astype(str)

        old_df = old_df.drop_duplicates(subset=["Tender ID", "Closing Date (IST)"])
    else:
        old_df = pd.DataFrame()

    if not old_df.empty:
        old_keys = set(zip(old_df["Tender ID"], old_df["Closing Date (IST)"]))
        new_df["key"] = list(zip(new_df["Tender ID"], new_df["Closing Date (IST)"]))
        new_unique = new_df[~new_df["key"].isin(old_keys)].drop(columns=["key"])
    else:
        new_unique = new_df

    combined = pd.concat([old_df, new_unique], ignore_index=True)
    combined = combined.drop_duplicates(subset=["Tender ID", "Closing Date (IST)"])
    combined.to_excel(FILE_NAME, index=False)

    return combined, new_unique