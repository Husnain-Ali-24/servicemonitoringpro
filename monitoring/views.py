from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Website
import requests
from django.contrib.auth.models import User
from django.urls import reverse

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
        interval = int(interval)
        user=User.objects.get(id=user_id)

        if url and interval:
            # Ensure the URL starts with http:// or https://
            if not url.startswith(("http://", "https://")):
                url = "http://" + url  

            # Check if the website is reachable
            try:
                response = requests.get(url, timeout=5)  # Set timeout to avoid long delays
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

            # Save to database
            Website.objects.create(user=user, url=url, status=new_status,interval=interval)

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

