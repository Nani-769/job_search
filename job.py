import smtplib
import os
import logging
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        self.base_url = "https://remotive.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def scrape_jobs(self, max_jobs=15):
        """Scrape job listings from multiple categories"""
        job_categories = [
            "/remote-jobs/software-dev",
            "/remote-jobs/frontend",
            "/remote-jobs/backend", 
            "/remote-jobs/full-stack"
        ]
        
        all_jobs = []
        
        for category in job_categories:
            try:
                url = f"{self.base_url}{category}"
                logger.info(f"Scraping {url}")
                
                # Add random delay to avoid rate limiting
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Try multiple selectors as websites can change
                job_cards = (soup.find_all('a', class_='job-tile-title') or 
                           soup.find_all('a', class_='job-tile') or
                           soup.find_all('div', class_='job-item'))
                
                category_jobs = []
                for job in job_cards:
                    try:
                        if job.name == 'a':
                            title = job.get_text(strip=True)
                            link = job.get('href')
                            if link and not link.startswith('http'):
                                link = f"{self.base_url}{link}"
                        else:
                            # Handle different HTML structures
                            title_elem = job.find('a') or job.find('h3') or job.find('h2')
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                link = title_elem.get('href')
                                if link and not link.startswith('http'):
                                    link = f"{self.base_url}{link}"
                            else:
                                continue
                        
                        if title and link:
                            # Try to get company name and other details
                            company_elem = job.find_parent().find('span', class_='company-name')
                            company = company_elem.get_text(strip=True) if company_elem else "Company not specified"
                            
                            category_jobs.append({
                                'title': title,
                                'link': link,
                                'company': company,
                                'category': category.split('/')[-1]
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error parsing job: {e}")
                        continue
                
                all_jobs.extend(category_jobs)
                logger.info(f"Found {len(category_jobs)} jobs in {category}")
                
            except requests.RequestException as e:
                logger.error(f"Error fetching {category}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error scraping {category}: {e}")
                continue
        
        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            job_key = (job['title'].lower(), job['company'].lower())
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        return unique_jobs[:max_jobs]
    
    def format_jobs_email(self, jobs):
        """Format jobs into HTML email"""
        if not jobs:
            return "No new job listings found today. 🔍"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .job-item {{ 
                    border: 1px solid #ddd; 
                    margin: 10px 0; 
                    padding: 15px; 
                    border-radius: 5px; 
                    background-color: #f9f9f9;
                }}
                .job-title {{ color: #0066cc; font-weight: bold; font-size: 18px; }}
                .company {{ color: #666; font-style: italic; }}
                .category {{ 
                    background-color: #e7f3ff; 
                    padding: 3px 8px; 
                    border-radius: 3px; 
                    font-size: 12px;
                    color: #0066cc;
                }}
                .link {{ margin-top: 10px; }}
                .header {{ color: #333; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h2 class="header">🚀 Daily Developer Jobs - {datetime.now().strftime('%B %d, %Y')}</h2>
            <p>Found <strong>{len(jobs)}</strong> job opportunities for you:</p>
        """
        
        for job in jobs:
            html_content += f"""
            <div class="job-item">
                <div class="job-title">{job['title']}</div>
                <div class="company">📍 {job['company']}</div>
                <span class="category">{job['category'].replace('-', ' ').title()}</span>
                <div class="link">
                    <a href="{job['link']}" target="_blank">View Job Details →</a>
                </div>
            </div>
            """
        
        html_content += """
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an automated job alert. Good luck with your applications! 💪
            </p>
        </body>
        </html>
        """
        
        return html_content
    
    def send_email(self, jobs):
        """Send email with job listings"""
        try:
            # Get credentials from environment variables (more secure)
            sender = os.getenv('SENDER_EMAIL')
            receiver = os.getenv('RECEIVER_EMAIL') 
            password = os.getenv('EMAIL_PASSWORD')
            
            if not all([sender, receiver, password]):
                logger.error("Email credentials not found in environment variables")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔥 Daily Developer Jobs - {len(jobs)} New Opportunities!"
            msg['From'] = sender
            msg['To'] = receiver
            
            # Create HTML content
            html_body = self.format_jobs_email(jobs)
            
            # Create plain text version
            text_body = f"Daily Developer Jobs - {datetime.now().strftime('%B %d, %Y')}\n\n"
            if jobs:
                for job in jobs:
                    text_body += f"Title: {job['title']}\n"
                    text_body += f"Company: {job['company']}\n"
                    text_body += f"Category: {job['category']}\n"
                    text_body += f"Link: {job['link']}\n\n"
            else:
                text_body += "No new job listings found today."
            
            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully with {len(jobs)} jobs")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

def main():
    """Main function to run the job scraper"""
    logger.info("Starting job scraper...")
    
    scraper = JobScraper()
    
    try:
        jobs = scraper.scrape_jobs()
        logger.info(f"Successfully scraped {len(jobs)} jobs")
        
        if scraper.send_email(jobs):
            logger.info("Job scraping and email sending completed successfully")
        else:
            logger.error("Failed to send email")
            
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        # Send error notification
        error_scraper = JobScraper()
        error_scraper.send_email([])  # Send empty jobs to trigger "no jobs found" message

if __name__ == "__main__":
    main()
