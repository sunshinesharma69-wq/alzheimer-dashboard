# Alzheimer Drug Repurposing Dashboard

This project turns the notebook findings into a Flask dashboard using the real results from your Alzheimer disease drug repurposing work.

## What is included

- Real GEO-based expression study summary
- Random Forest, SVM, XGBoost, and Logistic Regression comparison
- Top feature genes from the notebook output
- DGIdb interaction evidence
- Final candidate interpretation page

## Files used

- `data/GSE5281_series_matrix.txt.gz`
- `data/interactions-2024.tsv`

## How to run

1. Install Python 3.10+.
2. Open a terminal in `d:\alzheimer`.
3. Run:

```bash
pip install -r requirements.txt
python app.py
```

4. Open the local server shown in the terminal, usually `http://127.0.0.1:5000`.

## Run without VS Code

You can start the dashboard from File Explorer or a PowerShell window by running `run_dashboard.ps1` in this folder.

To make it start automatically after Windows login, use the shortcut placed in the Windows Startup folder:

`C:\Users\DELL\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\AlzheimerDashboard.lnk`

That shortcut runs:

```powershell
powershell -ExecutionPolicy Bypass -File "D:\alzheimer\run_dashboard.ps1"
```

After login, the local link will be available without opening VS Code.

If you want a desktop icon with no console window, use `D:\alzheimer\launch_dashboard.vbs` as the shortcut target.

## Beginner workflow

1. Open the home page first and check the overview cards.
2. Open the full report page for the detailed write-up.
3. If you add more notebook outputs later, replace the static lists in `app.py` with fresh results.
4. Keep the real datasets in the `data/` folder so the project stays reproducible.

## Notes

- The dashboard is populated from the real notebook outputs, not dummy data.
- The app is intentionally simple so you can extend it step by step.
