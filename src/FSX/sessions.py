import os, io
import pandas as pd
from playwright.sync_api import sync_playwright

def download_and_clean_csv(context, session_id):
    url = f"https://fsxlive.foresightsports.com/Stats/Export?sessionId={session_id}"
    resp = context.request.get(url)
    if resp.status != 200:
        raise Exception(f"Export failed ({resp.status}): {session_id}")
    text = resp.text()

    # --- Clean out HTML or garbage lines ---
    lines = text.splitlines()
    csv_lines = []
    for line in lines:
        l = line.strip()
        # keep lines that look like CSV (contain commas and no '<')
        if "," in l and not l.startswith("<"):
            csv_lines.append(l)
    cleaned = "\n".join(csv_lines)

    return cleaned

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="auth_state.json")
    page = context.new_page()

    # Collect session IDs
    page.goto("https://fsxlive.foresightsports.com/Stats")
    page.wait_for_selector("tr.row-link[data-href]")
    session_ids = page.locator("tr.row-link[data-href]").evaluate_all(r"""
        rows => rows.map(r => {
            const qs = r.getAttribute('data-href').split('?')[1];
            return new URLSearchParams(qs).get('SessionID');
        })
    """)

    all_dfs = []
    for sid in session_ids:
        print(f"🔄 Exporting session {sid}")
        csv_text = download_and_clean_csv(context, sid)
        # pandas will skip any malformed rows
        df = pd.read_csv(io.StringIO(csv_text), on_bad_lines='skip')
        df["SessionID"] = sid
        all_dfs.append(df)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv("all_sessions_exported.csv", index=False)
    print("✅ All sessions exported to all_sessions_exported.csv")

    browser.close()
