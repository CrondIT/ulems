from django.shortcuts import render, redirect
from .models import Event, Category, Participant, Competency, Competency, User, Profile
from .forms import AddEventForm, CategoryForm, ParticipantForm, CompetencyForm, ProfileForm
from django.contrib.auth.decorators import login_required

# Create your views here.

# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def index(request):
    return render(request,"home/index.html")
# ------------------------------------------------------------------------------------
def  events(request):
    
    error = ""
    context = {}
    context['events'] = Event.objects.all()
    context['title'] = 'Мероприятия'
    context['current_event'] = request.user.profile.current_event 
    if request.method == "POST":
       
        if 'select' in request.POST:
            pk = request.POST.get("select")
            event = Event.objects.get(id=pk)
            request.user.profile.current_event = event
            context['current_event'] = request.user.profile.current_event
            request.user.save()
        else:
            error = "Нужно выбрать мероприятие!"

        
    context['error'] = error
    return render(request, "home/events.html", context)
# ------------------------------------------------------------------------------------
def event(request, event_id):
    event = Event.objects.get(pk=event_id)
    return render(request, "home/event/event.html", {
        "event": event
    })
# ------------------------------------------------------------------------------------    
def add_event(request):
    error=""
    if request.method == "POST":
        form = AddEventForm(request.POST)
        if form.is_valid():
            usr = form.save(commit=False)
            usr.created_by = request.user
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

# ------------------------------------------------------------------------------------
def categories(request):
    
    form = CategoryForm()
    error=""
    context = {}
    context['categories'] = Category.objects.all()
    context['title'] = 'Категории'
    context['current_event'] = request.user.profile.current_event   
    if request.method == 'POST':
        
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                
                form = CategoryForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = request.user

            else:
                category = Category.objects.get(id=pk)
                category.updated_by = request.user
                form = CategoryForm(request.POST, instance=category)
            form.save()
            form = CategoryForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            category = Category.objects.get(id=pk)
            category.delete()  
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            category = Category.objects.get(id=pk)   
            form = CategoryForm(instance=category)
        elif 'sort':
            context['categories'] = Category.objects.order_by(request.POST['sort'])
            form = CategoryForm(request.POST)

    context['form'] = form
    context['error'] = error  

    return render(request, "home/categories.html", context)

# ------------------------------------------------------------------------------------
def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    return render(request, "home/category/category.html", {
        "category": category
    })
# ------------------------------------------------------------------------------------
def  participants(request):
    form = ParticipantForm()
    error=""
    context = {}
    context['participants'] = Participant.objects.all()
    context['title'] = 'Участники'
    context['current_event'] = request.user.profile.current_event
       
    if request.method == 'POST':
        
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                
                form = ParticipantForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = request.user

            else:
                participant = Participant.objects.get(id=pk)
                participant.updated_by = request.user
                form = ParticipantForm(request.POST, instance=participant)
            form.save()
            form = ParticipantForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            participant = Participant.objects.get(id=pk)
            participant.delete()  
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            participant = Participant.objects.get(id=pk)   
            form = ParticipantForm(instance=participant)
        elif 'sort':
            context['participants'] = Participant.objects.order_by(request.POST['sort'])
            form = ParticipantForm(request.POST)

    context['form'] = form
    context['error'] = error  

    return render(request, "home/participants.html", context)
    
# ------------------------------------------------------------------------------------
def  participant(request, participant_id):
    participant = Participant.objects.get(pk=participant_id)
    return render(request, "home/participant/participant.html", {
        "participant": participant
    })
# ------------------------------------------------------------------------------------
def  competencies(request):
    form = CompetencyForm()
    error=""
    context = {}
    context['competencies'] = Competency.objects.all()
    context['title'] = 'Компетенции'
    context['current_event'] = request.user.profile.current_event      
    if request.method == 'POST':
       
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                 
                form = CompetencyForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = request.user

            else:
                competency = Competency.objects.get(id=pk)
                competency.updated_by = request.user
                form = CompetencyForm(request.POST, instance=competency)
            form.save()
            form = CompetencyForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            competency = Competency.objects.get(id=pk)
            competency.delete()  
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            competency = Competency.objects.get(id=pk)   
            form = CompetencyForm(instance=competency)
        elif 'sort':
            context['competencies'] = Competency.objects.order_by(request.POST['sort'])
            form = CompetencyForm(request.POST)
    context['form'] = form
    context['error'] = error  

    return render(request, "home/competencies.html", context)
# ------------------------------------------------------------------------------------
def  competency(request, competency_id):
    competency = Competency.objects.get(pk=competency_id)
    return render(request, "home/competency/competency.html", {
        "competency": competency
    })


