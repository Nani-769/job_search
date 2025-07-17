import smtplib
from email.mime.text import MIMEText
import requests

def job_search():
    url = "https://remotive.io/api/remote-jobs?category=software-dev"
    response = requests.get(url)

    # Debug: Check if response is valid JSON
    if response.status_code != 200:
        print("Failed to fetch jobs. Status code:", response.status_code)
        print("Response body:", response.text)
        send_email("Failed to fetch job listings today.")
        return

    try:
        jobs_data = response.json()
    except Exception as e:
        print("Error decoding JSON:", e)
        print("Raw response:", response.text)
        send_email("Error decoding job listings from API.")
        return

    jobs = jobs_data.get("jobs", [])
    results = ""

    for job in jobs[:10]:
        title = job["title"]
        company = job["company_name"]
        link = job["url"]
        location = job["candidate_required_location"]
        results += f"{title} at {company}\nLocation: {location}\n{link}\n\n"

    if results:
        send_email(results)
    else:
        send_email("No developer job listings found today.")

def send_email(body):
    sender = "rellaramu769@gmail.com"
    receiver = "rellaramu1818@gmail.com"
    password = "moksmpndczbvzgqy"  # Store securely

    msg = MIMEText(body)
    msg['Subject'] = "Daily Job Listings - Developer Jobs"
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

# Run the job search
job_search()
