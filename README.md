# Golf Data Analysis

This project collects and analyzes personal launch monitor data. It includes Playwright scripts for scraping sessions from the FSX Live website and a simple Streamlit dashboard for quick visualization.

## Scripts in `src/`

- **src/golf.py** – Utility notebook turned script that aggregates all CSV files from the `sessions/` folder, normalizes club names, generates plots and exports a combined data file.
- **src/train_model.py** – Example machine‑learning training script that uses an open dataset to predict swing parameters with a random forest model.
- **src/FSX/dashboard.py** – Streamlit application that reads `data/formatted_all_rounds_data.csv` and displays interactive tables and charts of shot performance.
- **src/FSX/main.py** – Playwright automation that logs in to FSX Live, visits each round and extracts detailed shot information to `all_rounds_data.csv`.
- **src/FSX/rounds.py** – Alternative Playwright scraper for round data that iterates through the stats tables and collects metrics for each shot.
- **src/FSX/sessions.py** – Uses a stored authentication state (`auth_state.json`) to export session summaries directly to `all_sessions_exported.csv`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r src/FSX/requirements.txt
   playwright install
   ```
2. Create a `.env` file in the project root with your FSX credentials:
   ```ini
   FSX_USERNAME=your_email@example.com
   FSX_PASSWORD=your_password
   ```
3. Run the Streamlit dashboard:
   ```bash
   streamlit run src/FSX/dashboard.py
   ```

The dashboard expects a CSV at `data/formatted_all_rounds_data.csv`. Generate this file by running one of the scraping scripts described below.

## Collecting New Data

1. Ensure your `.env` file contains valid FSX credentials.
2. Run `python src/FSX/main.py` to scrape all available rounds. This will create `all_rounds_data.csv` with shot details.
3. Alternatively, `python src/FSX/rounds.py` or `python src/FSX/sessions.py` can be used for different export formats. `sessions.py` relies on `auth_state.json`, which stores a logged‑in browser state.
4. Move or process the resulting CSV into `data/formatted_all_rounds_data.csv` so the Streamlit dashboard can read it.
