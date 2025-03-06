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
import monitoring.utils as utils

logger = logging.getLogger(__name__)



def check_websites(interval):
    websites = Website.objects.filter(interval=interval)
    logger.info(f"Checking {websites.count()} websites for {interval}-second interval")
    
    for website in websites:
        monitoring_type=website.monitoring_type
        
        if monitoring_type=="website":
            website_status=utils.check_website_status(website.url)
            if website.status!=website_status:
                utils.send_alert(website,website_status)
            website.status=website_status
            website.last_checked=now()
            website.save()
            continue
        elif monitoring_type=="server":
            hostname = website.url.replace("http://", "").replace("https://", "").split("/")[0]
            new_status=utils.check_server_status(hostname,website.url)
            if website.status != new_status:
                utils.send_alert(website, new_status)
            website.status = new_status
            website.last_checked = now()
            website.save()
            continue
        elif monitoring_type=="both":
            hostname = website.url.replace("http://", "").replace("https://", "").split("/")[0]
            new_status_server=utils.check_server_status(hostname,website.url)
            new_status_website=utils.check_website_status(website.url)
            new_status=""
            if new_status_server=="UP" and new_status_website=="UP":
                new_status="UP"
            else:
                new_status="DOWN"
            if website.status!=new_status:
                utils.send_alert(website,new_status)
            website.status=new_status
            website.last_checked=now()
            website.save()
    return f"Checked {websites.count()} websites for {interval}-second interval"

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
