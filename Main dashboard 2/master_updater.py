import time
from datetime import datetime

# Import the scraper functions from your existing backend files
from gem_backend import run_scraper as run_gem
from ted_backend import run_scraper as run_ted
from malaysia_backend import run_scraper as run_malaysia
from nepal_backend import run_scraper as run_nepal
from vietnam_backend import run_scraper as run_vietnam
from global_backend import run_scraper as run_global

def run_master_update():
    print(f"🚀 [MASTER UPDATE] Starting sequence at {datetime.now().strftime('%H:%M:%S')}...")
    
    # 1. GeM Update
    print("\n--- 🇮🇳 Updating GeM Dashboard ---")
    try:
        run_gem([], update_source="Master_Scheduler")
        print("✅ GeM Data Saved.")
    except Exception as e:
        print(f"❌ GeM Failed: {e}")
    time.sleep(5) 

    # 2. TED Update
    print("\n--- 🇪🇺 Updating EU TED Dashboard ---")
    try:
        run_ted([], update_source="Master_Scheduler")
        print("✅ TED Data Saved.")
    except Exception as e:
        print(f"❌ TED Failed: {e}")
    time.sleep(5)

    # 3. Malaysia Update
    print("\n--- 🇲🇾 Updating Malaysia Dashboard ---")
    try:
        run_malaysia([], update_source="Master_Scheduler")
        print("✅ Malaysia Data Saved.")
    except Exception as e:
        print(f"❌ Malaysia Failed: {e}")
    time.sleep(5)

    # 4. Nepal Update
    print("\n--- 🇳🇵 Updating Nepal Dashboard ---")
    try:
        run_nepal([]) 
        print("✅ Nepal Data Saved.")
    except Exception as e:
        print(f"❌ Nepal Failed: {e}")
    time.sleep(5)

    # 5. Vietnam Update
    print("\n--- 🇻🇳 Updating Vietnam Dashboard ---")
    try:
        run_vietnam([])
        print("✅ Vietnam Data Saved.")
    except Exception as e:
        print(f"❌ Vietnam Failed: {e}")
    time.sleep(5)

    # 6. Global Update
    print("\n--- 🌍 Updating Global Dashboard ---")
    try:
        run_global([], update_source="Master_Scheduler")
        print("✅ Global Data Saved.")
    except Exception as e:
        print(f"❌ Global Failed: {e}")

    print(f"\n🏁 [FINISHED] All 6 Dashboards updated successfully at {datetime.now().strftime('%H:%M:%S')}!")

if __name__ == "__main__":
    # This runs immediately when you click "Run Python File"
    run_master_update()
