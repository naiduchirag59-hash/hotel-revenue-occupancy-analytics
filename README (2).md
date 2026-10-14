# Hotel Revenue & Occupancy Analytics (CA4 Project 37)

Interactive business analytics dashboard for hotel bookings using a real public dataset.

## Status
This is a runnable project starter. The app and analysis framework are prepared, but the project title and dataset must be approved by faculty before you begin analysis, as required by the CA4 instructions. Run the app and review the actual results before writing final findings or submitting.

## Dataset
- Dataset: Hotel Booking Demand
- Public dataset copy: https://github.com/aaqibqadeer/Hotel-booking-demand/blob/master/hotel_bookings.csv
- Original research article: N. Antonio, A. de Almeida, and L. Nunes (2019), *Hotel booking demand datasets*, Data in Brief, 22, 41–49. https://doi.org/10.1016/j.dib.2018.11.126
- The research article describes real booking records for one resort hotel and one city hotel, including canceled and completed bookings. See the article for provenance and terms.
- Important limitation: the available fields do not include total room inventory, so actual occupancy percentage cannot be computed. ADR × nights is only a room-value proxy, not verified revenue.

## Business questions
1. How do booking volumes vary by month, year, and hotel type?
2. How does ADR vary by hotel type and arrival month?
3. What proportion of bookings are canceled, and how does this vary by hotel type and market segment?
4. How do distribution channels and market segments contribute to booking volume?
5. Which customer types account for the largest booking counts?
6. What operational or commercial questions should management investigate further?

## Included
- `app.py`: Streamlit dashboard with interactive filters and Plotly charts.
- `requirements.txt`: Python dependencies.
- `report_template.docx`: CA4 report draft/template; replace placeholders and insert verified findings and screenshots.
- `dataset_approval_note.md`: proposed title/dataset summary to submit to faculty.

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app downloads the CSV on first run. For offline use, download the CSV from the source above and save it as `data/hotel_bookings.csv`.

## GitHub setup
1. Create a **public** repository named `hotel-revenue-occupancy-analytics` (or another name you prefer).
2. Upload the files in this folder, including `app.py`, `requirements.txt`, `README.md`, `runtime.txt`, and `data/README.md`. Do not commit private data or credentials.
3. In GitHub, open the repository and confirm the files are visible.
4. For command-line upload:

```bash
git init
git add .
git commit -m "Initial hotel analytics capstone"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/hotel-revenue-occupancy-analytics.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

## Streamlit Community Cloud deployment
1. Push the repository to GitHub.
2. Sign in at https://share.streamlit.io/ with your GitHub account.
3. Choose **Create app**, select the repository and `main` branch, and set the main file path to `app.py`.
4. Deploy and wait for the build to finish.
5. Open the public app URL and test all filters and tabs.
6. Add the deployed URL to your report only after it is live and tested.

## Before submission
- Obtain faculty approval for project title and dataset.
- Run the app and validate calculations against the source data.
- Record actual data-cleaning steps, charts, findings, and recommendations.
- Capture genuine screenshots of your own running app.
- Fill in student details, GitHub URL, Streamlit URL, and references in the report.
