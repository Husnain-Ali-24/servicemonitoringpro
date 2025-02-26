import requests
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Website
from alert.models import Alert
from django.utils import timezone
import logging
from django.utils.timezone import now

logger = logging.getLogger(__name__)

@shared_task
def check_website_status():
    websites = Website.objects.all()
    logger.info(f"Found {websites.count()} websites to check")  # Debugging line
    
    for website in websites:
        time_since_last_check = (now() - website.last_checked).total_seconds()
        if time_since_last_check >= website.interval:
            try:
                logger.info(f"Checking {website.url}")  # Debugging line
                response = requests.get(website.url, timeout=5)
                new_status=""
                if response.status_code in [502, 503, 504]:
                    new_status="DOWN"
                else:
                    new_status="UP"
            except requests.exceptions.ConnectionError:
                new_status="DOWN"
            except requests.exceptions.Timeout:
                new_status="DOWN"
            except requests.exceptions.RequestException:
                new_status="DOWN"

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

    return "Website Server Status Checked"

def alert_messages(website_url,website_user,new_status):
    alert=Alert.objects.create(
        user=website_user,
        url=website_url,
        status=new_status,
        message="Your website server is down.",
        is_read=False
    )
    alert.save()

def alert_messages_up(website_url,website_user,new_status):
    alert=Alert.objects.create(
        user=website_user,
        url=website_url,
        status=new_status,
        message="Your website server is Up Again.",
        is_read=False
    )
    alert.save()
def send_alert_email(website_url,email):
    subject = "⚠️ Website Server Down Alert"
    message = f"The website Server {website_url} is currently DOWN. Please check it immediately!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]  # Change this to the user's email
    
    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"Alert email sent for {website_url}")
    except Exception as e:
        logger.error(f"Failed to send email for {website_url}: {e}")
