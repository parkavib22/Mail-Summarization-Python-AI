# Mail Summarization and Attachment Download Using Python

This project follows the approach described in the project report: fetch the latest emails through Gmail IMAP, summarize email text by returning the first three sentences, and download attachments into a local `downloads/` folder.

## Files
- `app.py` — Flask backend, Gmail IMAP connection, summarization, and attachment download
- `templates/index.html` — web page
- `static/script.js` — form submission and results display
- `static/style.css` — page styling
- `requirements.txt` — Python dependencies

## Setup
1. Install Python 3.7 or later.
2. Open a terminal in this project folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

## Gmail sign-in
Enable IMAP in Gmail settings if needed. If Google requires two-step verification, create and use a Google App Password. Do not use your normal Gmail password. Never commit passwords, app passwords, or other secrets to GitHub.

## Important
- The app fetches the latest five messages from the inbox.
- Attachments are saved locally in the `downloads/` folder.
- The summary is extractive: it returns the first three sentences, matching the method described in the report. It is not a GPT-based AI summary.
- This is a starter implementation based on the report's code and stated workflow. Test it with a test Gmail account before relying on it.
