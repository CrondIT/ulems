from django.shortcuts import render
from .models import Event

# Create your views here.
def index(request):
    return render(request,"home/index.html")

def  events(request):
    return render(request, "home/events.html", {
        "events": Event.objects.all()
    })
