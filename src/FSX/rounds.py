import playwright
from playwright.sync_api import sync_playwright
import pandas as pd
import time

# Function to log in to the website
def login(page, username, password):
    page.goto("https://fsxlive.foresightsports.com/")
    page.click("#sign-in-btn")
    page.fill("#sign-in-username", username)
    page.fill("#sign-in-password", password)
    
    # Hide the overlay after signing in
    page.wait_for_selector(".md-overlay", state="visible")
    page.evaluate("document.querySelector('.md-overlay').style.display = 'none'")
    
    # Click on the 'SIGN IN' button
    page.click("button.btn-primary:has-text('SIGN IN')")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("div.navbar-container")
    print("Logged in successfully.")

# Function to scrape the detailed metrics for each shot
def scrape_metrics_for_shot(shot):
    metrics = {}
    try:
        metrics["Carry"] = shot.query_selector("div.shot-analysis-item:has-text('Carry') .shot-analysis-item-data").inner_text().strip()
        metrics["Total Distance"] = shot.query_selector("div.shot-analysis-item:has-text('Total Distance') .shot-analysis-item-data").inner_text().strip()
        metrics["Ball Speed"] = shot.query_selector("div.shot-analysis-item:has-text('Ball Speed') .shot-analysis-item-data").inner_text().strip()
        metrics["Launch Angle"] = shot.query_selector("div.shot-analysis-item:has-text('Launch Angle') .shot-analysis-item-data").inner_text().strip()
        metrics["Total Spin"] = shot.query_selector("div.shot-analysis-item:has-text('Total Spin') .shot-analysis-item-data").inner_text().strip()
        metrics["Push/Pull"] = shot.query_selector("div.shot-analysis-item:has-text('Push/Pull') .shot-analysis-item-data").inner_text().strip()
        metrics["Side Spin"] = shot.query_selector("div.shot-analysis-item:has-text('Side Spin') .shot-analysis-item-data").inner_text().strip()
        metrics["Back Spin"] = shot.query_selector("div.shot-analysis-item:has-text('Back Spin') .shot-analysis-item-data").inner_text().strip()
        metrics["Descent Angle"] = shot.query_selector("div.shot-analysis-item:has-text('Descent Angle') .shot-analysis-item-data").inner_text().strip()
        metrics["Peak Height"] = shot.query_selector("div.shot-analysis-item:has-text('Peak Height') .shot-analysis-item-data").inner_text().strip()
        metrics["Offline"] = shot.query_selector("div.shot-analysis-item:has-text('Offline') .shot-analysis-item-data").inner_text().strip()
    except Exception as e:
        print(f"Error scraping shot metrics: {e}")
    
    return metrics

# Function to scrape session data
def scrape_session_data(page):
    # Wait for the session table to load
    page.wait_for_selector("table.stats-summary-table")
    
    # Find all session rows in the table (rows with `data-href`)
    session_rows = page.locator("table.stats-summary-table tbody tr.row-link")
    row_count = session_rows.count()
    
    all_sessions_data = []

    for i in range(row_count):
        try:
            # Re-locate the session row each time just before clicking
            session_row = session_rows.nth(i)
            print("Clicking on the session row...")

            session_row.click()  # Clicking on the session row
            page.wait_for_load_state("networkidle")  # Wait for the session details page to fully load

            # Wait for the shot analysis data to appear on the session details page
            page.wait_for_selector(".shot-analysis-data", timeout=30000)  # Wait for shot analysis data
            
            # Scrape data for each shot in the session
            shot_details = page.query_selector_all(".shot-analysis-data")
            print(f"Found {len(shot_details)} shots in the session.")
            
            session_data = [scrape_metrics_for_shot(shot) for shot in shot_details]
            
            # Append the session data
            all_sessions_data.extend(session_data)

            # Go back to the main stats page to continue scraping the next session
            page.go_back()
            page.wait_for_load_state("networkidle")  # Ensure the main stats page is fully loaded

            # Add a slight delay to ensure all elements are stable
            time.sleep(2)
        except Exception as e:
            print(f"Error while processing session: {e}")
            continue

    # Convert to a DataFrame
    return pd.DataFrame(all_sessions_data)

# Main script
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Log in credentials
    username = "otot"
    password = "Otot#102991!"

    # Log in to the website
    login(page, username, password)

    # Scrape the session data from the stats page
    page.goto("https://fsxlive.foresightsports.com/Stats")
    page.wait_for_load_state("networkidle")  # Ensure stats page is fully loaded
    
    combined_data = scrape_session_data(page)

    # Save the combined data to CSV
    combined_data.to_csv("combined_session_data.csv", index=False)
    print("All data scraped and saved to combined_session_data.csv.")

    browser.close()
