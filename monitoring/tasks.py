import requests
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Website
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_website_status():
    websites = Website.objects.all()
    logger.info(f"Found {websites.count()} websites to check")  # Debugging line
    
    for website in websites:
        try:
            logger.info(f"Checking {website.url}")  # Debugging line
            response = requests.get(website.url, timeout=5)
            new_status = "UP" if response.status_code < 400 else "DOWN"
        except requests.RequestException as e:
            logger.error(f"Error checking {website.url}: {e}")  # Debugging line
            new_status = "DOWN"

        # Check if status changed to DOWN
        
        if website.status != new_status and new_status == "DOWN":
            
            send_alert_email(website.url,website.user.email)

        # Update status in the database
        website.status = new_status
        website.save()
        logger.info(f"Checked {website.url}: {website.status}")

    return "Website Status Checked"

def send_alert_email(website_url,email):
    subject = "⚠️ Website Down Alert"
    message = f"The website {website_url} is currently DOWN. Please check it immediately!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]  # Change this to the user's email
    
    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"Alert email sent for {website_url}")
    except Exception as e:
        logger.error(f"Failed to send email for {website_url}: {e}")
