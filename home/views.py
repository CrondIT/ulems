""" Import render and redirect. """
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from .models import Event, Category, Participant, Competency, UserImage

from .forms import AddEventForm, CategoryForm, ParticipantForm
from .forms import CompetencyForm, UserImageForm


# --------------------------------------------------------------------------
@login_required(login_url="login")
def index(request):
    """ View main (starter) page """
    return render(request, "home/index.html")


# ---------------------------------------------------------------------------
@login_required(login_url="login")
def events(request):
    """
        Print, select and delete events in table.
        Also detailed event view and add event (open in separate page).
    """
    error = ""
    context = {}
    context['title'] = 'Мероприятия'
    context['current_event'] = request.user.profile.current_event
    context['events'] = Event.objects.filter(created_by=request.user)
    if request.method == "POST":
        if 'select' in request.POST:
            pk = request.POST.get("select")
            select_item = context['events'].get(id=pk)
            request.user.profile.current_event = select_item
            context['current_event'] = request.user.profile.current_event
            request.user.save()
        elif 'info' in request.POST:
            pk = request.POST.get("info")
            return redirect('home:event', pk)
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = Event.objects.get(id=pk)
            delete_item.delete()
        else:
            error = "Нужно выбрать мероприятие!"
            context['error'] = error
    return render(request, "home/events.html", context)


# ------------------------------------------------------------------------------
@login_required(login_url="login")
def event(request, event_id):
    """ Detailed event view. """
    select_item = Event.objects.get(pk=event_id)
    return render(request, "home/event/event.html", {
        "event": select_item
    })


# ------------------------------------------------------------------------------
@login_required(login_url="login")
def add_event(request):
    """ Add new event. """
    error = ""
    if request.method == "POST":
        form = AddEventForm(request.POST, request.FILES)
        if form.is_valid():
            usr = form.save(commit=False)
            usr.created_by = request.user
            form.save()
            return redirect('home:events')
        else:
            error = "Ошибка заполнения"

    form = AddEventForm()
    data = {
        'form': form,
        'error': error
    }
    return render(request, "home/event/add_event.html", data)


# ------------------------------------------------------------------------------
@login_required(login_url="login")
def categories(request):
    """ View, add, edit and delete categories in table."""
    form = CategoryForm()
    error = ""
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
                save_item = Category.objects.get(id=pk)
                save_item.updated_by = request.user
                form = CategoryForm(request.POST, instance=save_item)
            form.save()
            form = CategoryForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = Category.objects.get(id=pk)
            delete_item.delete()  
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = Category.objects.get(id=pk)   
            form = CategoryForm(instance=edit_item)
        elif 'sort':
            context['categories'] = Category.objects.order_by(request.POST['sort'])
            form = CategoryForm(request.POST)
        else:
            pass

    context['form'] = form
    context['error'] = error

    return render(request, "home/categories.html", context)


# -------------------------------------------------------------------------------
@login_required(login_url="login")
def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    return render(request, "home/category/category.html", {
        "category": category
    })


# -------------------------------------------------------------------------------
@login_required(login_url="login")
def participants(request):
    error = ""
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
                save_item = Participant.objects.get(id=pk)
                save_item.updated_by = context['user']
                form = ParticipantForm(request.POST, instance=save_item)
            form.save()
            form = ParticipantForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = Participant.objects.get(id=pk)
            delete_item.delete()  
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = Participant.objects.get(id=pk)   
            form = ParticipantForm(instance=edit_item)
        elif 'sort':
            context['participants'] = Participant.objects.order_by(request.POST['sort'])
            form = ParticipantForm(request.POST)

    context['form'] = form
    context['error'] = error  

    return render(request, "home/participants.html", context)


# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def participant(request, participant_id):
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

# ------------------------------------------------------------------------------------
@login_required(login_url="login")
def user_images(request):
    
    form = UserImageForm()
    error=""
    context = {}
    context['user_images'] = UserImage.objects.filter(created_by=request.user)
    context['title'] = 'Изображения'
    context['current_user'] = request.user   
    if request.method == 'POST':
        
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = UserImageForm(request.POST, request.FILES)
                usr = form.save(commit=False)
                usr.created_by = request.user
            else:
                user_image = UserImage.objects.get(id=pk)
                user_image.updated_by = request.user
                form = UserImageForm(request.POST, request.FILES, instance=user_image)
            form.save()
            form = UserImageForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            user_image = UserImage.objects.get(id=pk)
            user_image.delete()  
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            user_image = UserImage.objects.get(id=pk)   
            form = UserImageForm(instance=user_image)
        elif 'sort':
            context['user_images'] = UserImage.objects.order_by(request.POST['sort'])
            form = UserImageForm(request.POST)

    context['form'] = form
    context['error'] = error  

    return render(request, "home/user_images.html", context)

# ------------------------------------------------------------------------------------
