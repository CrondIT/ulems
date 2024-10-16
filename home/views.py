from django.shortcuts import render, redirect
from .models import Event, Category, Participant, Competency
from .forms import AddEventForm

# Create your views here.
def index(request):
    return render(request,"home/index.html")

def  events(request):
    return render(request, "home/events.html", {
        "events": Event.objects.all()
    })

def event(request, event_id):
    event = Event.objects.get(pk=event_id)
    return render(request, "home/event/event.html", {
        "event": event
    })
     
def add_event(request):
    error=""
    if request.method == "POST":
        form = AddEventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home:events')
        else:
            error="Ошибка заполнения"

    form = AddEventForm()
    data = {
        'form': form,  
        'error': error
    }
    return render(request, "home/event/add_event.html", data)     

def  categories(request):
    return render(request, "home/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    return render(request, "home/category/category.html", {
        "category": category
    })

def  participants(request):
    return render(request, "home/participants.html", {
        "participants": Participant.objects.all()
    })

def  participant(request, participant_id):
    participant = Participant.objects.get(pk=participant_id)
    return render(request, "home/participant/participant.html", {
        "participant": participant
    })

def  competencies(request):
    return render(request, "home/competencies.html", {
        "competencies": Competency.objects.all()
    })

def  competency(request, competency_id):
    competency = Competency.objects.get(pk=competency_id)
    return render(request, "home/competency/competency.html", {
        "competency": competency
    })