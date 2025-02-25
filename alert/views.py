from django.shortcuts import render
from alert.models import Alert
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.

def alertView(request,user_id):
    user=User.objects.get(id=user_id)
    alerts = Alert.objects.filter(user=user).order_by('-timeStamp')
    return render(request, 'alert.html', {'alerts': alerts,'userId':user_id})

@csrf_exempt
def mark_as_read(request, alert_id):
    """Marks an alert as read (AJAX request)."""
    alert = get_object_or_404(Alert, id=alert_id)
    alert.is_read = True
    alert.save()
    return JsonResponse({'success': True})


@csrf_exempt
def clear_alert(request, alert_id):
    """Deletes an alert (AJAX request)."""
    alert = get_object_or_404(Alert, id=alert_id)
    alert.delete()
    return JsonResponse({'success': True})
