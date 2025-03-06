import requests
import socket
import subprocess
import logging
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .models import Website
from alert.models import Alert

logger = logging.getLogger(__name__)

# 1️⃣ PING FUNCTION (Checks if Server is Reachable)
def is_server_reachable(hostname):
    try:
        output = subprocess.run(["ping", "-n", "2", hostname], capture_output=True, text=True, timeout=5)
        return "Reply from" in output.stdout
    except Exception as e:
        logger.error(f"Ping failed for {hostname}: {e}")
        return False


# 2️⃣ PORT CHECK FUNCTION (Checks if HTTP/HTTPS are Running)
def is_port_open(hostname, port):
    try:
        with socket.create_connection((hostname, port), timeout=5):
            return True
    except (socket.timeout, socket.error):
        return False

# 3️⃣ WEBSITE STATUS CHECK FUNCTION
def check_website_status(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code not in [404,502, 503, 504]
    except requests.RequestException:
        return False

# 4️⃣ COMBINED SERVER MONITORING FUNCTION
def check_websites(interval):
    websites = Website.objects.filter(interval=interval)
    logger.info(f"Checking {websites.count()} websites for {interval}-second interval")
    
    for website in websites:
        monitoring_type=website.monitoring_type
        website_status=""
        if monitoring_type=="website":
            try:
                response = requests.get(website.url, timeout=5)  # Set timeout to avoid long delays
                if response.status_code>=200 and response.status_code<400:
                    website_status="UP"
                else:
                    website_status="DOWM"
            except requests.exceptions.ConnectionError:
                website_status="DOWN"
            except requests.exceptions.Timeout:
                website_status="DOWN"
            except requests.exceptions.RequestException:
                website_status="DOWN"
            if website.status!=website_status:
                send_alert(website,website_status)
            website.status=website_status
            website.last_checked=now()
            website.save()
            continue
        elif monitoring_type=="server":
            hostname = website.url.replace("http://", "").replace("https://", "").split("/")[0]
            server_up = is_server_reachable(hostname)
            port_80_open = is_port_open(hostname, 80)
            port_443_open = is_port_open(hostname, 443)
            website_up = check_website_status(website.url)

            new_status = "UP" if server_up and website_up and (port_80_open or port_443_open) else "DOWN"

            if website.status != new_status:
                send_alert(website, new_status)

            website.status = new_status
            website.last_checked = now()
            website.save()
            continue
        elif monitoring_type=="both":
            hostname = website.url.replace("http://", "").replace("https://", "").split("/")[0]
            server_up = is_server_reachable(hostname)
            port_80_open = is_port_open(hostname, 80)
            port_443_open = is_port_open(hostname, 443)
            website_up = check_website_status(website.url)
            new_status_server = "UP" if server_up and website_up and (port_80_open or port_443_open) else "DOWN"
            new_status_website=""
            new_status=""
            try:
                response = requests.get(website.url, timeout=5)  # Set timeout to avoid long delays
                if response.status_code>=200 and response.status_code<400:
                    new_status_website="UP"
                else:
                    new_status_website="DOWN"
            except requests.exceptions.ConnectionError:
                new_status_website="DOWN"
            except requests.exceptions.Timeout:
                new_status_website="DOWN"
            except requests.exceptions.RequestException:
                new_status_website="DOWN"
            if new_status_server=="UP" and new_status_website=="UP":
                new_status="UP"
            else:
                new_status="DOWN"
            if website.status!=new_status:
                send_alert(website,new_status)
            website.status=new_status
            website.last_checked=now()
            website.save()
    return f"Checked {websites.count()} websites for {interval}-second interval"

# 5️⃣ ALERT FUNCTION (Send Emails & Store in Database)
def send_alert(website, status):
    message = f"Your server hosting {website.url} is currently {status}."
    Alert.objects.create(user=website.user, url=website.url, status=status, message=message, is_read=False)
    
    if status == "DOWN":
        try:
            send_alert_email(website.url,website.user.email)
            logger.info(f"Email alert sent for {website.url}")
        except Exception as e:
            logger.error(f"Failed to send alert email for {website.url}: {e}")
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
# 6️⃣ CELERY TASKS (Scheduled Checks)
@shared_task
def check_30_sec():
    return check_websites(30)

@shared_task
def check_1_min():
    return check_websites(60)

@shared_task
def check_2_min():
    return check_websites(120)

@shared_task
def check_5_min():
    return check_websites(300)
