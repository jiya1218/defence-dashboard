import os
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# ---------------- CONFIG ----------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
FILE_NAME = "Data_collection3.xlsx"

# ---------------- SEARCH PAGES ----------------
scrape_sites = {
    "Naval News  Malaysia Defence": "https://www.navalnews.com/?s=Malaysia+defence+",
    # "Naval News  Malaysia Defence2": "https://www.navalnews.com/page/2/?s=Malaysia+defence+",
    # "Naval News  Malaysia Defence3": "https://www.navalnews.com/page/3/?s=Malaysia+defence+",
    "Naval Malaysian Armed Forces": "https://www.navalnews.com/?s=Malaysian+Armed+Forces",
    # "Naval Malaysian Armed Forces2": "https://www.navalnews.com/page/2/?s=Malaysian+Armed+Forces",
    "Naval News Ministry of Defence Malaysia": "https://www.navalnews.com/?s=Ministry+of+Defence+Malaysia",
    # "Naval News Ministry of Defence Malaysia2": "https://www.navalnews.com/page/2/?s=Ministry+of+Defence+Malaysia",
    # "Naval News Ministry of Defence Malaysia3": "https://www.navalnews.com/page/3/?s=Ministry+of+Defence+Malaysia",
    "Naval News Royal Malaysian Navy": "https://www.navalnews.com/?s=Royal+Malaysian+Navy",
    # "Naval News Royal Malaysian Navy2": "https://www.navalnews.com/page/2/?s=Royal+Malaysian+Navy",
    # "Naval News Royal Malaysian Navy3": "https://www.navalnews.com/page/3/?s=Royal+Malaysian+Navy",
    "Naval News Royal Malaysian Air Force": "https://www.navalnews.com/?s=Royal+Malaysian+Air+Force",
    # "Naval News Royal Malaysian Air Force2": "https://www.navalnews.com/page/2/?s=Royal+Malaysian+Air+Force",
    "Naval News Malaysian Army": "https://www.navalnews.com/?s=Malaysian+Army",
    "Naval News littoral combat ship (LCS)": "https://www.navalnews.com/?s=littoral+combat+ship+%28LCS%29+Malaysian+",
    "Naval News patrol vessel procurement": "https://www.navalnews.com/?s=patrol+vessel+procurement+Malaysian+",
    # "Naval News patrol vessel procurement2": "https://www.navalnews.com/page/2/?s=patrol+vessel+procurement+Malaysian+",
    "Naval News submarine upgrade Malaysia": "https://www.navalnews.com/?s=submarine+upgrade+Malaysia",
    "Naval News naval modernization Malaysia": "https://www.navalnews.com/?s=naval+modernization+Malaysia",
    "Naval News maritime security Malaysia": "https://www.navalnews.com/?s=maritime+security+Malaysia",
    # "Naval News maritime security Malaysia2": "https://www.navalnews.com/page/2/?s=maritime+security+Malaysia",
    # "Naval News maritime security Malaysia3": "https://www.navalnews.com/page/3/?s=maritime+security+Malaysia",
    "Naval News naval contract Malaysia": "https://www.navalnews.com/?s=naval+contract+Malaysia",
    # "Naval News naval contract Malaysia2": "https://www.navalnews.com/page/2/?s=naval+contract+Malaysia",
    # "Naval News naval contract Malaysia3": "https://www.navalnews.com/page/3/?s=naval+contract+Malaysia",
    "Naval News air defence system Malaysia": "https://www.navalnews.com/?s=air+defence+system+Malaysia",
    # "Naval News air defence system Malaysia2": "https://www.navalnews.com/page/2/?s=air+defence+system+Malaysia",
    "Naval News radar system procurement": "https://www.navalnews.com/?s=radar+system+procurement+malaysia+",
    "Naval News missile defence Malaysia": "https://www.navalnews.com/?s=missile+defence+Malaysia",
    # "Naval News missile defence Malaysia2": "https://www.navalnews.com/page/2/?s=missile+defence+Malaysia",
    "Naval News military tender Malaysia": "https://www.navalnews.com/?s=military+tender+Malaysia",
    "Naval News procurement Malaysia defence": "https://www.navalnews.com/?s=procurement+Malaysia+defence",
    # "Naval News procurement Malaysia defence2": "https://www.navalnews.com/page/2/?s=procurement+Malaysia+defence",
    "Naval News RFP defence Malaysia": "https://www.navalnews.com/?s=RFP+defence+Malaysia",
    "Naval News contract award defence Malaysia": "https://www.navalnews.com/?s=contract+award+defence+Malaysia",
    "Naval News defence acquisition Malaysia": "https://www.navalnews.com/?s=defence+acquisition+Malaysia",
    # "Naval News defence acquisition Malaysia2": "https://www.navalnews.com/page/2/?s=defence+acquisition+Malaysia",
    "Naval News UAV tender Malaysia": "https://www.navalnews.com/?s=UAV+tender+Malaysia",
    "Naval News missile tender Malaysia": "https://www.navalnews.com/?s=missile+tender+Malaysia",
    "Naval News missile procurement Malaysia defence": "https://www.navalnews.com/?s=missile+procurement+Malaysia+defence",
    # "Naval News missile procurement Malaysia defence2": "https://www.navalnews.com/page/2/?s=missile+procurement+Malaysia+defence",
    "Naval News guided missile contract Malaysia": "https://www.navalnews.com/?s=guided+missile+contract+Malaysia",
    "Naval News anti-ship missile procurement Malaysia": "https://www.navalnews.com/?s=anti-ship+missile+procurement+Malaysia",
    # "Naval News anti-ship missile procurement Malaysia2": "https://www.navalnews.com/page/2/?s=anti-ship+missile+procurement+Malaysia",
    "Naval News loitering munitions tender": "https://www.navalnews.com/?s=loitering+munitions+tender",
    "Naval News military tender Malaysia": "https://www.navalnews.com/?s=military+tender+Malaysia",
    "Naval News defence procurement Malaysia": "https://www.navalnews.com/?s=defence+procurement+Malaysia",
    # "Naval News defence procurement Malaysia2": "https://www.navalnews.com/page/2/?s=defence+procurement+Malaysia",
    "Naval News RMN defence contract Malaysia": "https://www.navalnews.com/?s=RMN+defence+contract+Malaysia",
    "Naval News Malaysia military procurement program": "https://www.navalnews.com/?s=Malaysia+military+procurement+program",
    "Naval News missile system supplier Malaysia": "https://www.navalnews.com/?s=missile+system+supplier+Malaysia",
    "Naval News ammunition supplier Malaysia defence": "https://www.navalnews.com/?s=ammunition+supplier+Malaysia+defence",
    "Naval News Defence": "https://www.navalnews.com/?s=malaysia+defence",
    "Naval News Ammunition": "https://www.navalnews.com/?s=ammunition",
    # "Naval News Ammunition1": "https://www.navalnews.com/?s=counter+drone+system",
    # "Naval News Ammunition2": "https://www.navalnews.com/page/2/?s=ammunition+malaysia+",
    "Naval News unmanned system": "https://www.navalnews.com/?s=unmanned+system+",
    # "Naval News unmanned system1": "https://www.navalnews.com/page/2/?s=unmanned+system+",
    # "Naval News unmanned system2": "https://www.navalnews.com/page/3/?s=unmanned+system+",
    # "Naval News unmanned system3": "https://www.navalnews.com/?s=unmanned+system+malaysia",
    # "Naval counter drone system4": "https://www.navalnews.com/?s=counter+drone+system+malaysia",
    # "Naval counter drone system5": "https://www.navalnews.com/?s=counter+drone+system",
    "Naval counter missile malaysia": "https://www.navalnews.com/?s=missile++tender+malaysia+",
    # "Naval counter missile malaysia1": "https://www.navalnews.com/?s=missile+malaysia+",
    # "Naval counter missile malaysia2": "https://www.navalnews.com/page/2/?s=missile+malaysia+",
    # "Naval counter missile malaysia3": "https://www.navalnews.com/page/3/?s=missile+malaysia+",
    # "Naval counter Defence Tender": "https://www.navalnews.com/?s=defence+tender++malaysia+",
    "Naval counter Defence Tender1": "https://www.navalnews.com/?s=defense+tender++malaysia+",
    "Naval counter Uav1": "https://www.navalnews.com/?s=UAV+",
    # "Naval counter Uav2": "https://www.navalnews.com/page/2/?s=UAV+",
    # "Naval counter Uav3": "https://www.navalnews.com/page/3/?s=UAV+",
    # "Naval counter Uav4": "https://www.navalnews.com/page/4/?s=UAV+",
    "Naval counter Weapon1": "https://www.navalnews.com/?s=weapon+Malaysia+",
    # "Naval counter Weapon2": "https://www.navalnews.com/page/2/?s=weapon+Malaysia+",
    # "Naval counter Weapon3": "https://www.navalnews.com/page/3/?s=weapon+Malaysia+",
    # "Naval counter Weapon4": "https://www.navalnews.com/page/4/?s=weapon+Malaysia+",
    "Naval counter Defense": "https://www.navalnews.com/?s=Defense+Malaysia+",
    # "Naval counter Defense2": "https://www.navalnews.com/page/2/?s=Defense+Malaysia+",
    # "Naval counter Defense3": "https://www.navalnews.com/page/3/?s=Defense+Malaysia+",
    
    "Bernama Drone" :"https://www.bernama.com/en/search.php?terms=drone+",
    # "Bernama Drone2" :"https://www.bernama.com/en/search.php?cat1=&terms=drone%20&page=2",
    "Bernama Missile1" :"https://www.bernama.com/en/search.php?terms=missile+",
    # "Bernama Missile2" :"https://www.bernama.com/en/search.php?cat1=&terms=missile%20&page=2",
    # "Bernama Missile3" :"https://www.bernama.com/en/search.php?cat1=&terms=missile%20&page=3",
    "Bernama Defence" :"https://www.bernama.com/en/search.php?terms=defence",
    # "Bernama Defence2" :"https://www.bernama.com/en/search.php?cat1=&terms=defence&page=2",
    # "Bernama Defence3" :"https://www.bernama.com/en/search.php?cat1=&terms=defence&page=3",
    # "Bernama Defence4" :"https://www.bernama.com/en/search.php?cat1=&terms=defence&page=4",
    "Bernama Defense1" :"https://www.bernama.com/en/search.php?cat1=all&terms=defense&submit=search",
    # "Bernama Defense2" :"https://www.bernama.com/en/search.php?cat1=all&terms=defense&page=2",
    # "Bernama Defense3" :"https://www.bernama.com/en/search.php?cat1=all&terms=defense&page=3",
    "Bernama Weapon1" :"https://www.bernama.com/en/search.php?cat1=all&terms=weapons&submit=search",
    # "Bernama Weapon1" :"https://www.bernama.com/en/search.php?cat1=all&terms=weapons&page=2",
    
    "Janes Malaysia defence contract award Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=defence%20contract%20award%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysia missile system supplier Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=missile%20system%20supplier%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysia military procurement program" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Malaysia%20military%20procurement%20program&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysia military procurement program2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Malaysia%20military%20procurement%20program&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysia defence contract award" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Malaysia%20defence%20contract%20award&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysia RMN defence contract Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=RMN%20defence%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysia MINDEF tender Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=MINDEF%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes defence procurement Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=defence%20procurement%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes defence procurement Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=defence%20procurement%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes military tender Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=military%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes defence tender Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=defence%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes defence tender Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=defence%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes military ammunition procurement Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=military%20ammunition%20procurement%20Malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes ammunition supply contract Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=ammunition%20supply%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes small arms procurement Malaysia defence" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=small%20arms%20procurement%20Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes loitering munitions tender" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=loitering%20munitions%20tender&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes C-UAS contract Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=C-UAS%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes C-UAS contract Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=C-UAS%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes anti-ship missile procurement Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=anti-ship%20missile%20procurement%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes air defence missile tender Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=air%20defence%20missile%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes guided missile contract Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=guided%20missile%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes missile procurement Malaysia defence" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=missile%20procurement%20Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes missile tender Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=missile%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes UAV procurement Malaysia defence" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=UAV%20procurement%20Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes defence acquisition Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=defence%20acquisition%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes defence acquisition Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=defence%20acquisition%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes procurement Malaysia defence" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=procurement%20Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes procurement Malaysia defence2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=procurement%20Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes procurement Malaysia defence3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=procurement%20Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes military tender Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=military%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes defence tender Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=defence%20tender%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes military vehicle procurement malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=military%20vehicle%20procurement%20malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes defence equipment supply Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=defence%20equipment%20supply%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes defence equipment supply Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=defence%20equipment%20supply%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes armoured vehicle Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=armoured%20vehicle%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes armoured vehicle Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=armoured%20vehicle%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes missile defence Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=missile%20defence%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes missile defence Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=missile%20defence%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes missile defence Malaysia3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=missile%20defence%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes radar system procurement" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=radar%20system%20procurement%20malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes air defence system Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=air%20defence%20system%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes air defence system Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=air%20defence%20system%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes air defence system Malaysia3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=air%20defence%20system%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes naval contract Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=naval%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes naval contract Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=naval%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes naval contract Malaysia3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=naval%20contract%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes maritime security Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=maritime%20security%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes maritime security Malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=maritime%20security%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes maritime security Malaysia3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=maritime%20security%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes patrol vessel procurement malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=patrol%20vessel%20procurement%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Royal Malaysian Air Force" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Royal%20Malaysian%20Air%20Force&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Royal Malaysian Air Force2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Royal%20Malaysian%20Air%20Force&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Royal Malaysian Air Force3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=Royal%20Malaysian%20Air%20Force&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysian Army" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Malaysian%20Army&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysian Army2" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=defence%20equipment%20supply%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysian Army3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=Malaysian%20Army&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Royal Malaysian Navy" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Royal%20Malaysian%20Navy&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Royal Malaysian Navy2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Royal%20Malaysian%20Navy&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Royal Malaysian Navy3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=Royal%20Malaysian%20Navy&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Royal Malaysian Navy4" :"https://www.janes.com/search/4?indexCatalogue=site-search&searchQuery=Royal%20Malaysian%20Navy&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Ministry of Defence Malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Ministry%20of%20Defence%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Ministry of Defence Malaysia1" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Ministry%20of%20Defence%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Ministry of Defence Malaysia2" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=Ministry%20of%20Defence%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Ministry of Defence Malaysia3" :"https://www.janes.com/search/4?indexCatalogue=site-search&searchQuery=Ministry%20of%20Defence%20Malaysia&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysian Armed Forces" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Malaysian%20Armed%20Forces&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysian Armed Forces2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Malaysian%20Armed%20Forces&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysian Armed Forces3" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=Malaysian%20Armed%20Forces&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Malaysia defence" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysia defence1" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysia defence2" :"https://www.janes.com/search/3?indexCatalogue=site-search&searchQuery=Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysia defence3" :"https://www.janes.com/search/4?indexCatalogue=site-search&searchQuery=Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Malaysia defence4" :"https://www.janes.com/search/5?indexCatalogue=site-search&searchQuery=Malaysia%20defence&orderBy=Newest&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes unmanned system malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=unmanned%20system%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes unmanned system malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=unmanned%20system%20malaysia&orderBy=Relevance&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Small arms" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Small%20arms%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Ammunition malaysia" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Ammunition%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Ammunition malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Ammunition%20malaysia&orderBy=Relevance&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Missile malaysia1" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Missile%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Missile malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Missile%20malaysia&orderBy=Relevance&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Defense malaysia1" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Defense%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Defense malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Defense%20malaysia&orderBy=Relevance&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Defence malaysia1" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=Defence%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    # "Janes Defence malaysia2" :"https://www.janes.com/search/2?indexCatalogue=site-search&searchQuery=Defence%20malaysia&orderBy=Relevance&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Anti Drone" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=anti%20drone&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes micro UAV" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=micro%20UAV&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    "Janes Weapon" :"https://www.janes.com/search?indexCatalogue=site-search&searchQuery=weapon%20malaysia&scoringInfo=cHJpb3JpdGlzZV9jb250ZW50X3R5cGU7SGlnaENvbnRlbnRUeXBlOlBhZ2U=",
    
    "Shephard Malaysia" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=1",
    "Shephard Malaysia2" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=2",
    "Shephard Malaysia3" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=3",
    "Shephard Malaysia4" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=4",
    # "Shephard Malaysia5" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=5",
    # "Shephard Malaysia6" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=6",
    # "Shephard Malaysia7" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=7",
    # "Shephard Malaysia8" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=8",
    # "Shephard Malaysia9" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=9",
    # "Shephard Malaysia10" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=10",
    # "Shephard Malaysia11" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=11",
    # "Shephard Malaysia12" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=12",
    # "Shephard Malaysia13" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=13",
    # "Shephard Malaysia14" :"https://www.shephardmedia.com/search/?q=malaysia+&sort_by=-created&page=14",
    "Shephard Unmanned System malaysia" :"https://www.shephardmedia.com/search/?q=Unmanned+System+malaysia+&sort_by=-created",
    # "Shephard Unmanned System malaysia2" :"https://www.shephardmedia.com/search/?q=Unmanned+System+malaysia+&sort_by=-created&page=2",
    "Shephard Counter Drone malaysia1" :"https://www.shephardmedia.com/search/?q=Counter+drones+malaysia+&sort_by=-created#",
    # "Shephard Counter Drone malaysia2" :"https://www.shephardmedia.com/search/?q=Counter+drones+malaysia+&sort_by=-created&page=2",
    # "Shephard Counter Drone malaysia3" :"https://www.shephardmedia.com/search/?q=Counter+drones+malaysia+&sort_by=-created&page=3",
    "Shephard Small arms tender malaysia1" :"https://www.shephardmedia.com/search/?q=Small+arms+tender+malaysia+&sort_by=-created",
    # "Shephard Small arms tender malaysia2" :"https://www.shephardmedia.com/search/?q=Small+arms+tender+malaysia+&sort_by=-created&page=2",
    # "Shephard Small arms tender malaysia3" :"https://www.shephardmedia.com/search/?q=Small+arms+tender+malaysia+&sort_by=-created&page=3",
    # "Shephard Small arms tender malaysia4" :"https://www.shephardmedia.com/search/?q=Small+arms+tender+malaysia+&sort_by=-created&page=4",
    "Shephard Ammunitions malaysia1" :"https://www.shephardmedia.com/search/?q=Ammunitions+malaysia+",
    # "Shephard Ammunitions malaysia2" :"https://www.shephardmedia.com/search/?q=Ammunitions+malaysia+&page=2",
    # "Shephard Ammunitions malaysia3" :"https://www.shephardmedia.com/search/?q=Ammunitions+malaysia+&page=3",
    "Shephard Missile malaysia" :"https://www.shephardmedia.com/search/?q=Missile+malaysia+&sort_by=-created",
    # "Shephard Missile malaysia2" :"https://www.shephardmedia.com/search/?q=Missile+malaysia+&sort_by=-created&page=2",
    # "Shephard Missile malaysia3" :"https://www.shephardmedia.com/search/?q=Missile+malaysia+&sort_by=-created&page=3",
    "Shephard Missile Defence" :"https://www.shephardmedia.com/search/?q=Defence+malaysia&sort_by=-created",
    # "Shephard Missile Defence2" :"https://www.shephardmedia.com/search/?q=Defence+malaysia&sort_by=-created&page=2",
    "Shephard Missile Defense" :"https://www.shephardmedia.com/search/?q=defense+malaysia+&sort_by=-created",
    # "Shephard Missile Defense" :"https://www.shephardmedia.com/search/?q=defense+malaysia+&sort_by=-created",
    # "Shephard Missile Defense2" :"https://www.shephardmedia.com/search/?q=defense+malaysia+&sort_by=-created&page=2",
    "Shephard Micro UAV" :"https://www.shephardmedia.com/search/?q=micro+uav&sort_by=-created",
    # "Shephard Micro UAV2" :"https://www.shephardmedia.com/search/?q=micro+uav&sort_by=-created&page=2",
    "Shephard Weapon" :"https://www.shephardmedia.com/search/?q=weapon+malaysia+&sort_by=-created",
    # "Shephard Weapon2" :"https://www.shephardmedia.com/search/?q=weapon+malaysia+&sort_by=-created&page=2",
    
    "MalayMail Malaysian Army": "https://www.malaymail.com/search?query=Malaysian%20Army&pgno=1",
    # "MalayMail Malaysian Army2": "https://www.malaymail.com/search?query=Malaysian%20Army&pgno=2",
    # "MalayMail Malaysian Army3": "https://www.malaymail.com/search?query=Malaysian%20Army&pgno=3",
    # "MalayMail Malaysian Army4": "https://www.malaymail.com/search?query=Malaysian%20Army&pgno=4",
    "MalayMail Malaysian Royal Malaysian Air Force": "https://www.malaymail.com/search?query=Royal+Malaysian+Air+Force",
    # "MalayMail Malaysian Royal Malaysian Air Force2": "https://www.malaymail.com/search?query=Royal%20Malaysian%20Air%20Force&pgno=2",
    # "MalayMail Malaysian Royal Malaysian Air Force3": "https://www.malaymail.com/search?query=Royal%20Malaysian%20Air%20Force&pgno=3",
    # "MalayMail Malaysian Royal Malaysian Air Force4": "https://www.malaymail.com/search?query=Royal%20Malaysian%20Air%20Force&pgno=4",
    "MalayMail Malaysian Royal Malaysian Navy": "https://www.malaymail.com/search?query=Royal+Malaysian+Navy",
    # "MalayMail Malaysian Royal Malaysian Navy2": "https://www.malaymail.com/search?query=Royal%20Malaysian%20Navy&pgno=2",
    # "MalayMail Malaysian Royal Malaysian Navy3": "https://www.malaymail.com/search?query=Royal%20Malaysian%20Navy&pgno=3",
    # "MalayMail Malaysian Royal Malaysian Navy4": "https://www.malaymail.com/search?query=Royal%20Malaysian%20Navy&pgno=4",
    "MalayMail Malaysian Ministry of Defence Malaysia": "https://www.malaymail.com/search?query=Ministry+of+Defence+Malaysia",
    # "MalayMail Malaysian Ministry of Defence Malaysia2": "https://www.malaymail.com/search?query=Ministry%20of%20Defence%20Malaysia&pgno=2",
    # "MalayMail Malaysian Ministry of Defence Malaysia3": "https://www.malaymail.com/search?query=Ministry%20of%20Defence%20Malaysia&pgno=3",
    # "MalayMail Malaysian Ministry of Defence Malaysia4": "https://www.malaymail.com/search?query=Ministry%20of%20Defence%20Malaysia&pgno=4",
    "MalayMail Armed Forces": "https://www.malaymail.com/search?query=Malaysian+Armed+Forces",
    # "MalayMail Armed Forces2": "https://www.malaymail.com/search?query=Malaysian%20Armed%20Forces&pgno=2",
    # "MalayMail Armed Forces3": "https://www.malaymail.com/search?query=Malaysian%20Armed%20Forces&pgno=3",
    # "MalayMail Armed Forces4": "https://www.malaymail.com/search?query=Malaysian%20Armed%20Forces&pgno=4",
    "MalayMail littoral combat ship (LCS)": "https://www.malaymail.com/search?query=littoral+combat+ship+%28LCS%29+malaysia+",
    # "MalayMail littoral combat ship (LCS)2": "https://www.malaymail.com/search?query=littoral%20combat%20ship%20%28LCS%29%20malaysia&pgno=2",
    # "MalayMail littoral combat ship (LCS)3": "https://www.malaymail.com/search?query=littoral%20combat%20ship%20%28LCS%29%20malaysia&pgno=3",
    "MalayMail patrol vessel procurement": "https://www.malaymail.com/search?query=patrol+vessel+procurement+malaysia+",
    # "MalayMail patrol vessel procurement2": "https://www.malaymail.com/search?query=patrol%20vessel%20procurement%20malaysia&pgno=2",
    "MalayMail offshore patrol vessel (OPV)": "https://www.malaymail.com/search?query=offshore+patrol+vessel+%28OPV%29+malaysia",
    "MalayMail submarine upgrade Malaysia": "https://www.malaymail.com/search?query=submarine+upgrade+Malaysia",
    "MalayMail naval modernization Malaysia": "https://www.malaymail.com/search?query=naval+modernization+Malaysia",
    "MalayMail maritime security Malaysia": "https://www.malaymail.com/search?query=maritime+security+Malaysia",
    # "MalayMail maritime security Malaysia2": "https://www.malaymail.com/search?query=maritime%20security%20Malaysia&pgno=2",
    # "MalayMail maritime security Malaysia3": "https://www.malaymail.com/search?query=maritime%20security%20Malaysia&pgno=3",
    # "MalayMail maritime security Malaysia4": "https://www.malaymail.com/search?query=maritime%20security%20Malaysia&pgno=4",
    # "MalayMail maritime security Malaysia5": "https://www.malaymail.com/search?query=maritime%20security%20Malaysia&pgno=5",
    "MalayMail naval contract Malaysia": "https://www.malaymail.com/search?query=naval+contract+Malaysia",
    # "MalayMail naval contract Malaysia2": "https://www.malaymail.com/search?query=naval%20contract%20Malaysia&pgno=2",
    "MalayMail air defence system Malaysia": "https://www.malaymail.com/search?query=air+defence+system+Malaysia",
    # "MalayMail air defence system Malaysia1": "https://www.malaymail.com/search?query=air%20defence%20system%20Malaysia&pgno=2",
    "MalayMail radar system procurement Malaysia": "https://www.malaymail.com/search?query=radar+system+procurement+malaysia+",
    "MalayMail missile defence Malaysia": "https://www.malaymail.com/search?query=missile+defence+Malaysia",
    # "MalayMail missile defence Malaysia2": "https://www.malaymail.com/search?query=missile%20defence%20Malaysia&pgno=2",
    "MalayMail armoured vehicle Malaysia": "https://www.malaymail.com/search?query=armoured+vehicle+Malaysia",
    "MalayMail military vehicle procurement": "https://www.malaymail.com/search?query=military+vehicle+procurement+malaysia+",
    "MalayMail Defense Tender Malaysia": "https://www.malaymail.com/search?query=defence+tender+Malaysia",
    # "MalayMail Defense Tender Malaysia2": "https://www.malaymail.com/search?query=defence%20tender%20malaysia&pgno=2",
    # "MalayMail Defense Tender Malaysia3": "https://www.malaymail.com/search?query=defence%20tender%20malaysia&pgno=3",
    "MalayMail military tender Malaysia": "https://www.malaymail.com/search?query=military+tender+Malaysia",
    "MalayMail procurement Malaysia defence": "https://www.malaymail.com/search?query=procurement+Malaysia+defence",
    # "MalayMail procurement Malaysia defence1": "https://www.malaymail.com/search?query=procurement%20Malaysia%20defence&pgno=2",
    # "MalayMail procurement Malaysia defence2": "https://www.malaymail.com/search?query=procurement%20Malaysia%20defence&pgno=3",
    # "MalayMail procurement Malaysia defence3": "https://www.malaymail.com/search?query=procurement%20Malaysia%20defence&pgno=4",
    "MalayMail defence acquisition Malaysia": "https://www.malaymail.com/search?query=defence+acquisition+Malaysia",
    # "MalayMail defence acquisition Malaysia2": "https://www.malaymail.com/search?query=defence%20acquisition%20Malaysia&pgno=2",
    # "MalayMail defence acquisition Malaysia3": "https://www.malaymail.com/search?query=defence%20acquisition%20Malaysia&pgno=3",
    # "MalayMail defence acquisition Malaysia4": "https://www.malaymail.com/search?query=defence%20acquisition%20Malaysia&pgno=4",
    "MalayMail government tender military Malaysia": "https://www.malaymail.com/search?query=government+tender+military+Malaysia",
    "MalayMail UAV procurement Malaysia defence": "https://www.malaymail.com/search?query=UAV+procurement+Malaysia+defence",
    "MalayMail military drone procurement Malaysia": "https://www.malaymail.com/search?query=military+drone+procurement+Malaysia",
    "MalayMail missile procurement Malaysia defence": "https://www.malaymail.com/search?query=missile+procurement+Malaysia+defence",
    "MalayMail military tender Malaysia": "https://www.malaymail.com/search?query=military+tender+Malaysia",
    "MalayMail defence procurement Malaysia": "https://www.malaymail.com/search?query=defence+procurement+Malaysia",
    # "MalayMail defence procurement Malaysia2": "https://www.malaymail.com/search?query=defence%20procurement%20Malaysia&pgno=2",
    # "MalayMail defence procurement Malaysia3": "https://www.malaymail.com/search?query=defence%20procurement%20Malaysia&pgno=3",
    # "MalayMail defence procurement Malaysia4": "https://www.malaymail.com/search?query=defence%20procurement%20Malaysia&pgno=4",
    "MalayMail MINDEF tender Malaysia": "https://www.malaymail.com/search?query=MINDEF+tender+Malaysia",
    "MalayMail RMN defence contract Malaysia": "https://www.malaymail.com/search?query=RMN+defence+contract+Malaysia",
    "MalayMail Malaysia defence contract award": "https://www.malaymail.com/search?query=Malaysia+defence+contract+award",
    "MalayMail Unmanned System malaysia": "https://www.malaymail.com/search?query=Unmanned+System+malaysia+",
    # "MalayMail Unmanned System malaysia2": "https://www.malaymail.com/search?query=Unmanned%20System%20malaysia&pgno=2",
    "MalayMail Counter Drone Malaysia": "https://www.malaymail.com/search?query=Counter+drones+malaysia+",
    "MalayMail Ammunition Malaysia": "https://www.malaymail.com/search?query=ammunition+malaysia",
    # "MalayMail Ammunition Malaysia2": "https://www.malaymail.com/search?query=ammunition%20malaysia&pgno=2",
    # "MalayMail Ammunition Malaysia3": "https://www.malaymail.com/search?query=ammunition%20malaysia&pgno=3",
    "MalayMail Missile Malaysia": "https://www.malaymail.com/search?query=missile+malaysia+",
    # "MalayMail Missile Malaysia2": "https://www.malaymail.com/search?query=missile%20malaysia&pgno=2",
    # "MalayMail Missile Malaysia3": "https://www.malaymail.com/search?query=missile%20malaysia&pgno=3",
    "MalayMail Defense Malaysia": "https://www.malaymail.com/search?query=defense+malaysia+",
    # "MalayMail Defense Malaysia2": "https://www.malaymail.com/search?query=defense%20malaysia&pgno=2",
    # "MalayMail Defense Malaysia3": "https://www.malaymail.com/search?query=defense%20malaysia&pgno=3",
    "MalayMail Defence Malaysia": "https://www.malaymail.com/search?query=defence+malaysia+",
    # "MalayMail Defence Malaysia2": "https://www.malaymail.com/search?query=defence%20malaysia&pgno=2",
    # "MalayMail Defence Malaysia3": "https://www.malaymail.com/search?query=defence%20malaysia&pgno=3",
    "MalayMail Anti Drone Malaysia": "https://www.malaymail.com/search?query=anti+drone+malaysia+",
    "MalayMail Defense Tender Malaysia": "https://www.malaymail.com/search?query=defence+tender+malaysia+",
    # "MalayMail Defense Tender Malaysia2": "https://www.malaymail.com/search?query=defence%20tender%20malaysia&pgno=2",
    # "MalayMail Defense Tender Malaysia3": "https://www.malaymail.com/search?query=defence%20tender%20malaysia&pgno=3",
    "MalayMail Weapon Malaysia": "https://www.malaymail.com/search?query=weapon+malaysia+",
    
    "Malaisiakini Unmanned System": "https://www.malaysiakini.com/en/search?keywords=Unmanned+System+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Counter drones": "https://www.malaysiakini.com/en/search?keywords=Counter+drones+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Small arms": "https://www.malaysiakini.com/en/search?keywords=Small+arms+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Ammunitions": "https://www.malaysiakini.com/en/search?keywords=Ammunitions+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Missile": "https://www.malaysiakini.com/en/search?keywords=Missile+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Missile1": "https://www.malaysiakini.com/en/search?keywords=Missile+Malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Missile2": "https://www.malaysiakini.com/en/search?keywords=Missile+Malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini Defence": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defence1": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Defence2": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Defence3": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=3",
    "Malaisiakini Defence Tender": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defence Tender1": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Defence Tender2": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Defence Tender3": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=3",
    "Malaisiakini Defense Tender": "https://www.malaysiakini.com/en/search?keywords=Defense+tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defense Tender": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Defense": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defense1": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Defense2": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini Anti drone malaysia ": "https://www.malaysiakini.com/en/search?keywords=anti+drone+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Weapon malaysia ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Weapon malaysia1 ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Weapon malaysia2 ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Weapon malaysia3 ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=3",
    
    "Malaisiakini Unmanned System": "https://www.malaysiakini.com/en/search?keywords=Unmanned+System+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Counter drones": "https://www.malaysiakini.com/en/search?keywords=Counter+drones+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Small arms": "https://www.malaysiakini.com/en/search?keywords=Small+arms+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Ammunitions": "https://www.malaysiakini.com/en/search?keywords=Ammunitions+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Missile": "https://www.malaysiakini.com/en/search?keywords=Missile+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Missile1": "https://www.malaysiakini.com/en/search?keywords=Missile+Malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Missile2": "https://www.malaysiakini.com/en/search?keywords=Missile+Malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini Defence": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defence1": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Defence2": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Defence3": "https://www.malaysiakini.com/en/search?keywords=Defence++Malaysia+&category=&startDate=&endDate=&sort=desc&page=3",
    "Malaisiakini Defence Tender": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defence Tender1": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Defence Tender2": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Defence Tender3": "https://www.malaysiakini.com/en/search?keywords=Defence++tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=3",
    "Malaisiakini Defense Tender": "https://www.malaysiakini.com/en/search?keywords=Defense+tender+Malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defense Tender": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Defense": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Defense1": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Defense2": "https://www.malaysiakini.com/en/search?keywords=Defense+malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini Anti drone malaysia ": "https://www.malaysiakini.com/en/search?keywords=anti+drone+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini Weapon malaysia ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Weapon malaysia1 ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Weapon malaysia2 ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Weapon malaysia3 ": "https://www.malaysiakini.com/en/search?keywords=weapon+malaysia+&category=&startDate=&endDate=&sort=desc&page=3",
    "Malaisiakini Malaysia defence contract award": "https://www.malaysiakini.com/en/search?keywords=Malaysia+defence+contract+award&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini RMN defence contract Malaysia": "https://www.malaysiakini.com/en/search?keywords=RMN+defence+contract+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini defence procurement Malaysia": "https://www.malaysiakini.com/en/search?keywords=defence+procurement+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini military tender Malaysia": "https://www.malaysiakini.com/en/search?keywords=military+tender+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini defence tender Malaysia": "https://www.malaysiakini.com/en/search?keywords=defence+tender+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini defence tender Malaysia2": "https://www.malaysiakini.com/en/search?keywords=defence+tender+Malaysia&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini defence tender Malaysia3": "https://www.malaysiakini.com/en/search?keywords=defence+tender+Malaysia&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini small arms procurement Malaysia defence": "https://www.malaysiakini.com/en/search?keywords=small+arms+procurement+Malaysia+defence&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini missile procurement Malaysia defence": "https://www.malaysiakini.com/en/search?keywords=missile+procurement+Malaysia+defence&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini military drone procurement Malaysia": "https://www.malaysiakini.com/en/search?keywords=military+drone+procurement+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini government tender military Malaysia": "https://www.malaysiakini.com/en/search?keywords=government+tender+military+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini government tender military Malaysia1": "https://www.malaysiakini.com/en/search?keywords=government+tender+military+Malaysia&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini government tender military Malaysia2": "https://www.malaysiakini.com/en/search?keywords=government+tender+military+Malaysia&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini contract award defence Malaysia": "https://www.malaysiakini.com/en/search?keywords=contract+award+defence+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini procurement Malaysia defence": "https://www.malaysiakini.com/en/search?keywords=procurement+Malaysia+defence&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini procurement Malaysia defence1": "https://www.malaysiakini.com/en/search?keywords=procurement+Malaysia+defence&category=&startDate=&endDate=&sort=desc&page=1",
    "Malaisiakini military tender Malaysia": "https://www.malaysiakini.com/en/search?keywords=military+tender+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini military tender Malaysia1": "https://www.malaysiakini.com/en/search?keywords=military+tender+Malaysia&category=&startDate=&endDate=&sort=desc&page=1",
    "Malaisiakini military vehicle procurement": "https://www.malaysiakini.com/en/search?keywords=military+vehicle+procurement+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini defence equipment supply Malaysia": "https://www.malaysiakini.com/en/search?keywords=defence+equipment+supply+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini armoured vehicle Malaysia": "https://www.malaysiakini.com/en/search?keywords=armoured+vehicle+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini missile defence Malaysia": "https://www.malaysiakini.com/en/search?keywords=missile+defence+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini missile defence Malaysia1": "https://www.malaysiakini.com/en/search?keywords=missile+defence+Malaysia&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini missile defence Malaysia2": "https://www.malaysiakini.com/en/search?keywords=missile+defence+Malaysia&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini shipbuilding tender Malaysia": "https://www.malaysiakini.com/en/search?keywords=shipbuilding+tender+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini naval contract Malaysia": "https://www.malaysiakini.com/en/search?keywords=naval+contract+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini naval contract Malaysia1": "https://www.malaysiakini.com/en/search?keywords=naval+contract+Malaysia&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini naval contract Malaysia2": "https://www.malaysiakini.com/en/search?keywords=naval+contract+Malaysia&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini maritime security Malaysia": "https://www.malaysiakini.com/en/search?keywords=maritime+security+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini maritime security Malaysia1": "https://www.malaysiakini.com/en/search?keywords=maritime+security+Malaysia&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini maritime security Malaysia2": "https://www.malaysiakini.com/en/search?keywords=maritime+security+Malaysia&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini patrol vessel procurement": "https://www.malaysiakini.com/en/search?keywords=patrol+vessel+procurement&category=&startDate=&endDate=&sort=desc&page=0",
    "Malaisiakini littoral combat ship (LCS) malaysia": "https://www.malaysiakini.com/en/search?keywords=littoral+combat+ship+%28LCS%29+malaysia+&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini littoral combat ship (LCS) malaysia1": "https://www.malaysiakini.com/en/search?keywords=littoral+combat+ship+%28LCS%29+malaysia+&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini littoral combat ship (LCS) malaysia2": "https://www.malaysiakini.com/en/search?keywords=littoral+combat+ship+%28LCS%29+malaysia+&category=&startDate=&endDate=&sort=desc&page=2",
    "Malaisiakini Malaysian Army": "https://www.malaysiakini.com/en/search?keywords=Malaysian+Army&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Malaysian Army1": "https://www.malaysiakini.com/en/search?keywords=Malaysian+Army&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Malaysian Army2": "https://www.malaysiakini.com/en/search?keywords=Malaysian+Army&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Malaysian Army3": "https://www.malaysiakini.com/en/search?keywords=Malaysian+Army&category=&startDate=&endDate=&sort=desc&page=3",
    "Malaisiakini Royal Malaysian Air Force": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Air+Force&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Royal Malaysian Air Force1": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Air+Force&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Royal Malaysian Air Force2": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Air+Force&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Royal Malaysian Air Force3": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Air+Force&category=&startDate=&endDate=&sort=desc&page=3",
    "Malaisiakini Royal Malaysian Navy": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Navy&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Royal Malaysian Navy1": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Navy&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Royal Malaysian Navy2": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Navy&category=&startDate=&endDate=&sort=desc&page=2",
    # "Malaisiakini Royal Malaysian Navy3": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Navy&category=&startDate=&endDate=&sort=desc&page=3",
    # "Malaisiakini Royal Malaysian Navy4": "https://www.malaysiakini.com/en/search?keywords=Royal+Malaysian+Navy&category=&startDate=&endDate=&sort=desc&page=4",
    "Malaisiakini Ministry of Defence Malaysia": "https://www.malaysiakini.com/en/search?keywords=Ministry+of+Defence+Malaysia&category=&startDate=&endDate=&sort=desc&page=0",
    # "Malaisiakini Ministry of Defence Malaysia1": "https://www.malaysiakini.com/en/search?keywords=Ministry+of+Defence+Malaysia&category=&startDate=&endDate=&sort=desc&page=1",
    # "Malaisiakini Ministry of Defence Malaysia2": "https://www.malaysiakini.com/en/search?keywords=Ministry+of+Defence+Malaysia&category=&startDate=&endDate=&sort=desc&page=2",
    
    # "Astro Awani Unmanned System": "https://theedgemalaysia.com/news-search-results?keywords=Unmanned%20System&to=2026-03-15&from=1999-01-01&language=english&offset=0",
    # "Astro Awani Unmanned System1": "https://theedgemalaysia.com/news-search-results?keywords=Unmanned%20System&to=2026-03-15&from=1999-01-01&language=english&offset=10",
    # "Astro Awani Unmanned System2": "https://theedgemalaysia.com/news-search-results?keywords=Unmanned%20System&to=2026-03-15&from=1999-01-01&language=english&offset=20",
    # "Astro counter drone malaysia ": "https://theedgemalaysia.com/news-search-results?keywords=counter%20drone%20malaysia%20&to=2026-03-15&from=1999-01-01&language=english&offset=0",
    # "Astro counter drone malaysia1": "https://theedgemalaysia.com/news-search-results?keywords=counter%20drone%20malaysia%20&to=2026-03-15&from=1999-01-01&language=english&offset=10",
    
    # "Free Malaysia Today": "https://www.freemalaysiatoday.com/search?term=defence%20malaysia&category=all",
    # "The Star": "https://www.thestar.com.my/search?query=defence%20malaysia",
    # "The Star": "https://www.thestar.com.my/search?query=unmaned+system",
    # "The Star": "https://www.thestar.com.my/search?query=counter+drone+system",
    # "The Star": "https://www.thestar.com.my/search?query=small+arms+malaysia",
    # "The Star": "https://www.thestar.com.my/search?query=ammunition+malaysia",
    # "The Star": "https://www.thestar.com.my/search?query=missile+malaysia"

}

# ---------------- FORMAT DATE ----------------
def format_date(date_text):
    try:
        dt = pd.to_datetime(date_text, errors="coerce")
        if pd.isna(dt):
            return "0000-00-00 00:00:00"
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "0000-00-00 00:00:00"

# ---------------- GET ARTICLE DATE ----------------
def get_article_date(url, session):
    try:
        r = session.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        meta_tags = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "pubdate"}),
            ("meta", {"name": "publishdate"}),
            ("meta", {"itemprop": "datePublished"})
        ]
        for tag, attr in meta_tags:
            m = soup.find(tag, attr)
            if m and m.get("content"):
                return format_date(m["content"])
        t = soup.find("time")
        if t:
            return format_date(t.get_text(strip=True))
    except:
        pass
    return "0000-00-00 00:00:00"

# ---------------- GET ARTICLE TEXT ----------------
def get_article_text(url, session):
    try:
        r = session.get(url, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return text[:5000]
    except:
        return ""

# ---------------- SIMPLE SUMMARY ----------------
def generate_summary(text):
    if not text:
        return "No summary available"
    sentences = text.split(". ")
    summary = ". ".join(sentences[:3])
    return summary

# ---------------- SCRAPE NEWS ----------------
def scrape_news():
    articles = []
    seen = set()
    headers = {"User-Agent": "Mozilla/5.0"}
    with requests.Session() as session:
        for source, url in scrape_sites.items():
            logging.info(f"{source} → Loading news...")
            try:
                r = session.get(url, headers=headers, timeout=20)
                soup = BeautifulSoup(r.text, "html.parser")
                count = 0
                for a in soup.find_all("a", href=True):
                    title = a.get_text(" ", strip=True)
                    href = a["href"]
                    if not title or not href: continue
                    if len(title.split()) < 5: continue
                    if href.startswith(("javascript:", "mailto:", "#")): continue
                    full_url = urljoin(url, href)
                    key = (title, full_url)
                    if key in seen: continue
                    seen.add(key)
                    date = get_article_date(full_url, session)
                    text = get_article_text(full_url, session)
                    summary = generate_summary(text)
                    articles.append({
                        "Source": source,
                        "Title": title,
                        "Date": date,
                        "Summary": summary,
                        "Link": full_url
                    })
                    count += 1
                logging.info(f"{source} → {count} articles collected")
            except Exception as e:
                logging.warning(f"{source} scraping error: {e}")
    return articles

def collect_and_save():
    logging.info("Starting news collection...")
    new_articles = scrape_news()
    if not new_articles:
        logging.info("No articles found")
        return
    new_df = pd.DataFrame(new_articles)
    if os.path.exists(FILE_NAME):
        old_df = pd.read_excel(FILE_NAME)
        combined = pd.concat([old_df, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=["Title", "Link"])
        combined.to_excel(FILE_NAME, index=False)
        logging.info(f"Database updated → {len(combined)} total articles")
    else:
        new_df.to_excel(FILE_NAME, index=False)
        logging.info(f"Database created → {len(new_df)} articles")

if __name__ == "__main__":
    collect_and_save()
