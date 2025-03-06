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
import monitoring.utils as utils


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
                new_status = utils.check_website_status(url)
                # Save to database
                Website.objects.create(user=user, url=url, status=new_status,interval=interval,monitoring_type=monitoring_type)
            elif monitoring_type=='server':
                hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
                new_status=utils.check_server_status(hostname,url)
                Website.objects.create(user=user, url=url, status=new_status,interval=interval,monitoring_type=monitoring_type)
            elif monitoring_type=='both':
                hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
                new_status_server=utils.check_server_status(hostname,url)
                new_status_website=utils.check_website_status(url)
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
