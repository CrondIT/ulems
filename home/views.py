from django.shortcuts import render, redirect
from .models import Event, Category, Participant, Competency
from .forms import AddEventForm, CategoryForm

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

def categories(request):
    form = CategoryForm()
    error=""
    context = {}
    context['categories'] = Category.objects.all()
    context['title'] = 'Категории'
       
    if request.method == 'POST':
        
        if 'save' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                pk = request.POST.get('save')
                if not pk:
                    form = Category(request.POST)
                else:
                    category = Category.objects.get(id=pk)
                    form = CategoryForm(request.POST, instance=category)
                
                form.save()
                form = CategoryForm()
            else:
                error="Ошибка заполнения"    

        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            category = Category.objects.get(id=pk)
            category.delete()  
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            category = Category.objects.get(id=pk)   
            form = CategoryForm(instance=category)

    context['form'] = form
    context['error'] = error  

    return render(request, "home/categories.html", context)

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