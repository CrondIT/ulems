from django.shortcuts import render, redirect
from .models import Event, Category, Participant, Competency, Competency
from .forms import AddEventForm, CategoryForm, ParticipantForm, CompetencyForm
from django.contrib.auth.decorators import login_required

# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def index(request):
    return render(request,"home/index.html")
# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def  events(request):
    
    error = ""
    context = {}
    context['title'] = 'Мероприятия'
    context['current_event'] = request.user.profile.current_event 
    context['events'] = Event.objects.filter(created_by=request.user)
    if request.method == "POST":
       
        if 'select' in request.POST:
            pk = request.POST.get("select")
            event = Event.objects.get(id=pk)
            request.user.profile.current_event = event
            context['current_event'] = request.user.profile.current_event
            request.user.save()
        elif 'info' in request.POST:
            pk = request.POST.get("info")
            return redirect( 'home:event',pk)  
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            category = Event.objects.get(id=pk)
            category.delete()     
        else:
            error = "Нужно выбрать мероприятие!"

        
    context['error'] = error
    return render(request, "home/events.html", context)
# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def event(request, event_id):
    event = Event.objects.get(pk=event_id)
    return render(request, "home/event/event.html", {
        "event": event
    })
# ------------------------------------------------------------------------------------    
@login_required(login_url="login")
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
@login_required(login_url="login")
def categories(request):
    
    form = CategoryForm()
    error=""
    context = {}
    context['categories'] = Category.objects.filter(created_by=request.user)
    context['title'] = 'Категории'
    context['current_event'] = request.user.profile.current_event   
    if request.method == 'POST':
        
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                
                form = CategoryForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = request.user
                usr.event_related = context['current_event']

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
@login_required(login_url="login")
def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    return render(request, "home/category/category.html", {
        "category": category
    })
# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def  participants(request):
    
    error=""
    context = {}
    context['participants'] = Participant.objects.filter(created_by=request.user)
    context['title'] = 'Участники'
    context['current_event'] = request.user.profile.current_event
    context['user'] = request.user
    form = ParticipantForm(user=request.user, current_event=request.user.profile.current_event)

    if request.method == 'POST':
        
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                
                form = ParticipantForm(request.POST, context)
                usr = form.save(commit=False)
                usr.created_by = context['user']
                usr.event_related = context['current_event']

            else:
                participant = Participant.objects.get(id=pk)
                participant.updated_by = context['user']
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
@login_required(login_url="login")
def  participant(request, participant_id):
    participant = Participant.objects.get(pk=participant_id)
    return render(request, "home/participant/participant.html", {
        "participant": participant
    })
# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def  competencies(request):
    form = CompetencyForm()
    error=""
    context = {}
    context['competencies'] = Competency.objects.filter(created_by=request.user)
    context['title'] = 'Компетенции'
    context['current_event'] = request.user.profile.current_event      
    
    if request.method == 'POST':
       
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                 
                form = CompetencyForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = request.user
                usr.event_related = context['current_event']

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
@login_required(login_url="login")
def  competency(request, competency_id):
    competency = Competency.objects.get(pk=competency_id)
    return render(request, "home/competency/competency.html", {
        "competency": competency
    })


