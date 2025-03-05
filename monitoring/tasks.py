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

def check_websites(interval):
    websites = Website.objects.filter(interval=interval)
    logger.info(f"Checking {websites.count()} websites for {interval}-second interval")

    for website in websites:
        try:
            response = requests.get(website.url, timeout=5)
            new_status = "DOWN" if response.status_code in [502, 503, 504] else "UP"
        except requests.exceptions.RequestException:
            new_status = "DOWN"

        # Alert user if status changes
        if website.status != new_status:
            alert_messages(website.url, website.user, new_status)
            if new_status == "DOWN":
                send_alert_email(website.url, website.user.email)

        website.status = new_status
        website.last_checked = now()
        website.save()

    return f"Checked {websites.count()} websites for {interval}-second interval"

@shared_task
def check_10_sec():
    return check_websites(10)

@shared_task
def check_1_min():
    return check_websites(60)

@shared_task
def check_2_min():
    return check_websites(120)

@shared_task
def check_5_min():
    return check_websites(300)

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
