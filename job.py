import smtplib
from email.mime.text import MIMEText
import requests

def job_search():
    url = "https://remotive.io/api/remote-jobs?category=software-dev"
    response = requests.get(url)
    jobs = response.json().get("jobs", [])

    results = ""
    for job in jobs[:10]:  # Limit to top 10 jobs
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
    password = "moksmpndczbvzgqy"  # Consider storing this in an environment variable for safety

    msg = MIMEText(body)
    msg['Subject'] = "Daily Job Listings - Developer Jobs"
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

# Call the function
job_search()
