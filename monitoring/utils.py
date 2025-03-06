import requests
import socket
import subprocess
import logging
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from alert.models import Alert
logger = logging.getLogger(__name__)


class ServerChecking:
    def is_server_reachable(self,hostname):
        try:
            output = subprocess.run(["ping", "-n", "2", hostname], capture_output=True, text=True, timeout=5)
            return "Reply from" in output.stdout
        except Exception as e:
            return False


    # 2️⃣ PORT CHECK FUNCTION (Checks if HTTP/HTTPS are Running)
    def is_port_open(self,hostname, port):
        try:
            with socket.create_connection((hostname, port), timeout=5):
                return True
        except (socket.timeout, socket.error):
            return False

    # 3️⃣ WEBSITE STATUS CHECK FUNCTION
    def check_website_status(self,url):
        try:
            response = requests.get(url, timeout=5)
            return response.status_code not in [502, 503, 504]
        except requests.RequestException:
            return False

def check_website_status(url):
    status=""
    try:
        response = requests.get(url, timeout=5)  # Set timeout to avoid long delays
        if response.status_code>=200 and response.status_code<400:
            status="UP"
            return status
        else:
            status="DOWN"
            return status
    except requests.exceptions.ConnectionError:
        status="DOWN"
        return status
    except requests.exceptions.Timeout:
        status="DOWN"
        return status
    except requests.exceptions.RequestException:
        status="DOWN"
        return status


def check_server_status(hostname,url):
    check=ServerChecking()
    server_up = check.is_server_reachable(hostname)
    port_80_open = check.is_port_open(hostname, 80)
    port_443_open = check.is_port_open(hostname, 443)
    website_up = check.check_website_status(url)
    new_status = "UP" if server_up and website_up and (port_80_open or port_443_open) else "DOWN"
    return new_status

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