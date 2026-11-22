import imaplib
import email
import os
import re
from email.header import decode_header
from email.message import Message
from pathlib import Path

import nltk
from flask import Flask, jsonify, render_template, request
from nltk.tokenize import sent_tokenize

app = Flask(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def decode_mime(value):
    """Decode an email header or filename into readable text."""
    if not value:
        return ""
    decoded_parts = decode_header(value)
    output = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            output.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            output.append(part)
    return "".join(output)


def get_text_body(message: Message):
    """Extract the plain-text body from an email message."""
    parts = message.walk() if message.is_multipart() else [message]
    body_chunks = []
    for part in parts:
        if part.get_content_type() != "text/plain":
            continue
        if part.get_filename():
            continue
        payload = part.get_payload(decode=True)
        if payload:
            charset = part.get_content_charset() or "utf-8"
            body_chunks.append(payload.decode(charset, errors="replace"))
    return "\n".join(body_chunks)


def save_attachments(message: Message):
    """Save attachments from a message into the downloads folder."""
    saved = []
    for part in message.walk():
        filename = part.get_filename()
        if not filename:
            continue
        safe_name = os.path.basename(decode_mime(filename))
        if not safe_name:
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue

        destination = DOWNLOAD_DIR / safe_name
        # Avoid overwriting files with the same name.
        stem, suffix = destination.stem, destination.suffix
        counter = 1
        while destination.exists():
            destination = DOWNLOAD_DIR / f"{stem}_{counter}{suffix}"
            counter += 1

        destination.write_bytes(payload)
        saved.append(destination.name)
    return saved


def fetch_emails(username, password, limit=5):
    """Fetch the latest messages from a Gmail inbox using IMAP."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(username, password)
        status, _ = mail.select("INBOX")
        if status != "OK":
            raise RuntimeError("Could not open the inbox.")

        status, messages = mail.search(None, "ALL")
        if status != "OK":
            raise RuntimeError("Could not retrieve inbox messages.")

        message_ids = messages[0].split()[-limit:]
        email_texts = []
        attachment_names = []

        for message_id in reversed(message_ids):
            status, data = mail.fetch(message_id, "(RFC822)")
            if status != "OK" or not data or not isinstance(data[0], tuple):
                continue

            msg = email.message_from_bytes(data[0][1])
            subject = decode_mime(msg.get("Subject", "(No subject)"))
            sender = decode_mime(msg.get("From", "Unknown sender"))
            body = get_text_body(msg)
            email_texts.append(
                f"Subject: {subject}\nFrom: {sender}\n{body}".strip()
            )
            attachment_names.extend(save_attachments(msg))

        return "\n\n".join(email_texts), attachment_names
    finally:
        try:
            mail.logout()
        except Exception:
            pass


def summarize_text(text):
    """Return the first three sentences, following the project PDF approach."""
    if not text.strip():
        return "No readable email text was found."
    try:
        sentences = sent_tokenize(text)
    except LookupError:
        nltk.download("punkt", quiet=True)
        # Newer NLTK versions may require this tokenizer data as well.
        try:
            nltk.download("punkt_tab", quiet=True)
        except Exception:
            pass
        sentences = sent_tokenize(text)
    return " ".join(sentences[:3]) or text[:500]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/fetch-emails", methods=["POST"])
def fetch_and_summarize():
    data = request.get_json(silent=True) or {}
    username = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Please enter your email address and app password."}), 400

    try:
        email_content, attachments = fetch_emails(username, password)
        summary = summarize_text(email_content)
        return jsonify({
            "summary": summary,
            "attachments": attachments,
            "attachment_count": len(attachments)
        })
    except imaplib.IMAP4.error:
        return jsonify({
            "error": "Gmail could not sign in. Check IMAP access and use a Google App Password if required."
        }), 401
    except Exception as exc:
        app.logger.exception("Email processing failed")
        return jsonify({"error": f"Email processing failed: {exc}"}), 500


if __name__ == "__main__":
    # Run locally. Do not use debug=True on a public server.
    app.run(host="127.0.0.1", port=5000, debug=False)
