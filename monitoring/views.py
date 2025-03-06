from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Website
import requests
from django.contrib.auth.models import User
from django.urls import reverse
import requests
import socket
import subprocess


@login_required
def dashboard(request, user_id):
    if not request.user.is_authenticated:  
        return redirect("login")  # Ensure user is logged in
    
    try:
        new_user = User.objects.get(id=user_id)  # ✅ Fetch user
        websites = Website.objects.filter(user=new_user)  # ✅ Filter user's websites
    except User.DoesNotExist:
        new_user = None
        websites = []

    return render(request, "dashboard.html", {"websites": websites, "userId": user_id})


@login_required
def add_website(request,user_id):
    if request.method == "POST":
        url = request.POST.get("website_url")
        interval=request.POST.get("interval")
        monitoring_type=request.POST.get("monitoring_type")
        interval = int(interval)
        user=User.objects.get(id=user_id)

        if url and interval and monitoring_type:
            # Ensure the URL starts with http:// or https://
            if not url.startswith(("http://", "https://")):
                url = "http://" + url  

            # Check if the website is reachable
            if monitoring_type=="website":
                try:
                    response = requests.get(url, timeout=5)  # Set timeout to avoid long delays
                    new_status=""
                    if response.status_code>=200 and response.status_code<400:
                        new_status="UP"
                    else:
                        new_status="DOWN"
                except requests.exceptions.ConnectionError:
                    new_status="DOWN"
                except requests.exceptions.Timeout:
                    new_status="DOWN"
                except requests.exceptions.RequestException:
                    new_status="DOWN"

                # Save to database
                Website.objects.create(user=user, url=url, status=new_status,interval=interval,monitoring_type=monitoring_type)
            elif monitoring_type=='server':
                hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
                server_up = is_server_reachable(hostname)
                port_80_open = is_port_open(hostname, 80)
                port_443_open = is_port_open(hostname, 443)
                website_up = check_website_status(url)
                new_status = "UP" if server_up and website_up and (port_80_open or port_443_open) else "DOWN"
                Website.objects.create(user=user, url=url, status=new_status,interval=interval,monitoring_type=monitoring_type)
            elif monitoring_type=='both':
                hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
                server_up = is_server_reachable(hostname)
                port_80_open = is_port_open(hostname, 80)
                port_443_open = is_port_open(hostname, 443)
                website_up = check_website_status(url)
                new_status_server = "UP" if server_up and website_up and (port_80_open or port_443_open) else "DOWN"
                new_status_website=""
                new_status=""
                try:
                    response = requests.get(url, timeout=5)  # Set timeout to avoid long delays
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

                Website.objects.create(user=user, url=url, status=new_status,interval=interval,monitoring_type=monitoring_type)

        return redirect(reverse("dashboard", args=[user_id]))
    return render(request, "add_website.html",{"userId":user_id})

@login_required
def remove_website(request,website_id,user_id):
    website = get_object_or_404(Website, id=website_id)
    website.delete()
    return redirect(reverse("dashboard", args=[user_id])) 

def logout_view(request):
    logout(request)
    return redirect("dashboard")


# 1️⃣ PING FUNCTION (Checks if Server is Reachable)
def is_server_reachable(hostname):
    try:
        output = subprocess.run(["ping", "-n", "2", hostname], capture_output=True, text=True, timeout=5)
        return "Reply from" in output.stdout
    except Exception as e:
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
        return response.status_code not in [502, 503, 504]
    except requests.RequestException:
        return False