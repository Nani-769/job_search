import smtplib
import os
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import requests

def job_search():
    # query = "1 year experience OR entry level insurance health claims OR health claim executive site:linkedin.com/jobs OR site:angel.co OR site:indeed.com"
query = "developer job with 2+ years experience site:linkedin.com/jobs OR site:angel.co OR site:indeed.com"
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = ""
    for g in soup.find_all('div', class_='tF2Cxc'):
        link_tag = g.find('a')
        title_tag = g.find('h3')
        if link_tag and title_tag:
            title = title_tag.get_text()
            link = link_tag['href']
            results += f"{title}\n{link}\n\n"

    if results:
        send_email(results)
    else:
        send_email("No job listings found today.")

def send_email(body):
    sender = "rellaramu769@gmail.com"
    receiver = "rellaramu1818@gmail.com"
    password ="moksmpndczbvzgqy"        
    # os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(body)
    msg['Subject'] = "Daily Job Listings - Health Claims"
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

# Call the function directly (GitHub Actions handles scheduling)
job_search()
