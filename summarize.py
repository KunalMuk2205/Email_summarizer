import imaplib
import email
import os
from dotenv import load_dotenv
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
import smtplib

load_dotenv()

# Load model
model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)


def get_email_summaries():
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("EMAIL_PASSWORD")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    # Fetch emails from today only
    result, data = mail.search(None, 'SINCE "29-May-2025"')  # update date dynamically as needed
    email_ids = data[0].split()

    summaries = []
    for eid in email_ids[-5:]:  # last 5 emails
        result, data = mail.fetch(eid, "(RFC822)")
        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        subject = msg["Subject"]
        body = get_body_from_email(msg)
        summary = summarize_text(body)
        summaries.append({"subject": subject, "summary": summary})
    return summaries


def get_body_from_email(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""  # fallback empty string if no plain text found


def summarize_text(text):
    inputs = tokenizer(text, truncation=True, padding="longest", return_tensors="pt")
    summary_ids = model.generate(**inputs, max_length=60, num_beams=4)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def send_to_email(subject, content):
    sender = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("SEND_TO_EMAIL")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    message = f"Subject: {subject}\n\n{content}"
    server.sendmail(sender, receiver, message)
    server.quit()


def send_to_whatsapp(text):
    from twilio.rest import Client

    sid = os.getenv("TWILIO_SID")
    auth = os.getenv("TWILIO_AUTH")
    client = Client(sid, auth)
    client.messages.create(
        from_="whatsapp:+14155238886",
        to="whatsapp:" + os.getenv("MY_WHATSAPP"),
        body=text
    )


def run_daily_summary():
    summaries = get_email_summaries()
    combined = "\n\n".join([f"Subject: {s['subject']}\nSummary: {s['summary']}" for s in summaries])
    send_to_email("Daily Email Summary", combined)
    send_to_whatsapp(combined)


if __name__ == "__main__":
    run_daily_summary()
