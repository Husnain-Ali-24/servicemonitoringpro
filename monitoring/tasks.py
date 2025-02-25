import requests
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Website
from alert.models import Alert
from django.utils import timezone
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
            new_status = "UP" if 200 <= response.status_code < 300 else "DOWN"
        except requests.RequestException as e:
            logger.error(f"Error checking {website.url}: {e}")  # Debugging line
            new_status = "DOWN"

        # Check if status changed to DOWN
        
        if website.status != new_status and new_status == "DOWN":
            
            send_alert_email(website.url,website.user.email)
            alert_messages(website.url,website.user,new_status)

        if website.status != new_status and new_status == "UP":
            alert_messages_up(website.url,website.user,new_status)

        # Update status in the database
        website.status = new_status
        website.save()
        logger.info(f"Checked {website.url}: {website.status}")

    return "Website Status Checked"

def alert_messages(website_url,website_user,new_status):
    alert=Alert.objects.create(
        user=website_user,
        url=website_url,
        status=new_status,
        message="Your website is down.",
        is_read=False
    )
    alert.save()

def alert_messages_up(website_url,website_user,new_status):
    alert=Alert.objects.create(
        user=website_user,
        url=website_url,
        status=new_status,
        message="Your website is Up Again.",
        is_read=False
    )
    alert.save()
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
