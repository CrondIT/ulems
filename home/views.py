from django.shortcuts import render
from .models import Event, Category

# Create your views here.
def index(request):
    return render(request,"home/index.html")

def  events(request):
    return render(request, "home/events.html", {
        "events": Event.objects.all()
    })

def event(request, event_id):
    event = Event.objects.get(pk=event_id)
    return render(request, "home/event.html", {
        "event": event
    })
     

def  categories(request):
    return render(request, "home/categories.html", {
        "categories": Category.objects.all()
    })
