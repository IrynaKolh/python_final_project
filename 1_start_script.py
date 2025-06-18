import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
options = webdriver.ChromeOptions()

options.add_argument('--headless')  # Enable headless mode
options.add_argument('--disable-gpu')  # Optional, recommended for Windows
options.add_argument('--window-size=1920x1080')  # Optional, set window size
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
driver.get("https://www.baseball-almanac.com/yearly/yr1901a.shtml")

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.ba-table table.boxed"))
)

# Find all tables with class .boxed
tables = driver.find_elements(By.CSS_SELECTOR, "div.ba-table table.boxed")
# Find first table (Player Review)
first_table = tables[0]
# Find all <a> in first column 
stat_cells = first_table.find_elements(By.CSS_SELECTOR, "td.datacolBlue a")
# Extract text and href from each <a> element
links_and_texts = [(cell.text.strip(), cell.get_attribute("href")) for cell in stat_cells]

output_folder = "started_csv"
os.makedirs(output_folder, exist_ok=True)

# Print the links and texts
for link in links_and_texts :
    print(link)
def scrape_table(metric_name, url):
    print(f"Scraping: {metric_name}")
    driver.get(url)
    time.sleep(2)  # Allow content to load
    data = []
    tables = driver.find_elements(By.CSS_SELECTOR, "div.ba-table table.boxed")
    for table in tables:
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == 8:
                    # American League
                    year_al = cells[0].text.strip()
                    player_al = cells[1].text.strip()
                    stat_al = cells[2].text.strip().split()[0]
                    team_al = cells[3].text.strip()
                    # National League
                    year_nl = cells[4].text.strip()
                    player_nl = cells[5].text.strip()
                    stat_nl = cells[6].text.strip().split()[0]
                    team_nl = cells[7].text.strip()
                    data.append([year_al, "AL", player_al, team_al, stat_al])
                    data.append([year_nl, "NL", player_nl, team_nl, stat_nl])
            except Exception as e:
                print(f":warning: Skipped a row: {e}")
  # Save as CSV
    filename = metric_name.lower().replace(" ", "_") + ".csv"
    file_path = os.path.join(output_folder, filename)
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "League", "Player", "Team", metric_name])
        writer.writerows(data)
    print(f":white_check_mark: Saved: {filename}")
# ========== RUN ALL METRICS ==========
for name, link in links_and_texts :
    scrape_table(name, link)
driver.quit()