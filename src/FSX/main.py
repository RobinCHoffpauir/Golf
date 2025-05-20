from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
username = 'otot'
password = 'Otot#102991!'

# Check if credentials are available
if not username or not password:
    raise ValueError("Username or password not found in environment variables.")

def extract_shot_analysis_data(shot_analysis_container):
    """Extracts all shot analysis data from a given container"""
    shot_data = {}

    analysis_items = shot_analysis_container.query_selector_all(".shot-analysis-item")

    for item in analysis_items:
        label = item.query_selector(".shot-analysis-item-label").text_content().strip()
        data = item.query_selector(".shot-analysis-item-data").text_content().strip()
        shot_data[label] = data

    return shot_data

def extract_shots_data(page):
    """Extracts all the shots data including their analysis"""
    all_shots_data = []
    shots_rows = page.query_selector_all("table.hole-shots-table tbody tr.shot-row")

    for shot_row in shots_rows:
        shot_num = shot_row.query_selector("td:nth-child(1)").text_content().strip()
        club = shot_row.query_selector("td:nth-child(2)").text_content().strip()
        result = shot_row.query_selector("td:nth-child(3)").text_content().strip()
        carry = shot_row.query_selector("td:nth-child(4)").text_content().strip()
        total_distance = shot_row.query_selector("td:nth-child(5)").text_content().strip()
        offline = shot_row.query_selector("td:nth-child(6)").text_content().strip()

        shot_data = {
            'Shot Number': shot_num,
            'Club': club,
            'Result': result,
            'Carry (yds)': carry,
            'Total Distance (yds)': total_distance,
            'Offline (yds)': offline
        }

        # Find the next sibling that contains shot analysis data
        shot_analysis_row = shot_row.evaluate_handle("element => element.nextElementSibling")
        if shot_analysis_row and shot_analysis_row.evaluate("el => el.classList.contains('shot-analysis')"):
            shot_analysis_container = shot_analysis_row.query_selector(".shot-analysis-data-container")
            if shot_analysis_container:
                analysis_data = extract_shot_analysis_data(shot_analysis_container)
                shot_data.update(analysis_data)

        all_shots_data.append(shot_data)

    return all_shots_data

def scrape_rounds(page):
    """Scrape all rounds available on the main page"""
    rounds_data = []

    # Wait until the table with rounds is loaded
    page.wait_for_selector("tr.row-link")

    # Find all rows with class `row-link` (each row represents a round)
    round_rows = page.query_selector_all("tr.row-link")

    for i, round_row in enumerate(round_rows):
        # Ensure each row is refreshed and up to date
        round_row = page.query_selector_all("tr.row-link")[i]

        # Extract data from each round row
        date = round_row.query_selector("td:nth-child(1)").text_content().strip()
        course = round_row.query_selector("td:nth-child(2)").text_content().strip()
        score = round_row.query_selector("td:nth-child(4)").text_content().strip()

        # Log the round details
        print(f"Scraping round {i + 1} - Date: {date}, Course: {course}, Score: {score}")

        # Extract the `data-href` to navigate to the session page
        session_link = round_row.get_attribute("data-href")

        if session_link:
            # Navigate to the session link (the round page)
            page.goto(f"https://fsxlive.foresightsports.com{session_link}")
            page.wait_for_selector("table.hole-shots-table")

            # Scrape the shots data
            shots_data = extract_shots_data(page)
            rounds_data.append({
                'Date': date,
                'Course': course,
                'Score': score,
                'Shots': shots_data
            })

            # Click the back button using XPath
            back_button = page.locator("//button[contains(text(), 'Back')]")  # XPath for the back button
            back_button.click()
            page.wait_for_selector("tr.row-link")  # Wait for the rounds to load again

            # Optional sleep to prevent rate limiting or server load issues
            time.sleep(1)

    return rounds_data

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Navigate to the login page
    page.goto("https://fsxlive.foresightsports.com/")
    
    # Click sign-in button and login
    page.click("#sign-in-btn")
    page.fill("#sign-in-username", username)
    page.fill("#sign-in-password", password)
    
    # Hide the overlay after signing in
    page.wait_for_selector(".md-overlay", state="visible")
    page.evaluate("document.querySelector('.md-overlay').style.display = 'none'")
    
    # Click on the 'SIGN IN' button
    page.click("button.btn-primary:has-text('SIGN IN')")
    page.wait_for_load_state("networkidle")

    # Scrape the data from all rounds
    rounds_data = scrape_rounds(page)

    # Convert to DataFrame and save as CSV
    all_shots = []
    for round_data in rounds_data:
        date = round_data['Date']
        course = round_data['Course']
        score = round_data['Score']
        shots = round_data['Shots']
        for shot in shots:
            shot['Date'] = date
            shot['Course'] = course
            shot['Round Score'] = score
            all_shots.append(shot)

    all_shots_df = pd.DataFrame(all_shots)
    all_shots_df.to_csv("all_rounds_data.csv", index=False)

    # Close the browser
    browser.close()

    print("Scraping complete. Data saved to all_rounds_data.csv")
