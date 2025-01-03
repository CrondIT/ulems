""" Import render and redirect. """
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from .models import Event, Category, Participant, Competency, UserImage
from .models import PrintTemplate

from .forms import EventForm, CategoryForm, ParticipantForm
from .forms import CompetencyForm, UserImageForm, PrintTemplateForm

from . import makepdf


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def index(request):
    """ View main (starter) page """
    context = {}
    context['current_event'] = request.user.profile.current_event
    return render(request, "home/index.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def events(request):
    """
        Print, select and delete events in table.
        Also detailed event view and add event (open in separate page).
        Filter for current user.
    """
    error = ""
    context = {}
    context['title'] = 'Мероприятия'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['events'] = Event.objects.filter(
        created_by=context['current_user']
        )
    if request.method == "POST":
        if 'select' in request.POST:
            pk = request.POST.get("select")
            select_item = context['events'].get(id=pk)
            request.user.profile.current_event = select_item
            context['current_event'] = request.user.profile.current_event
            request.user.save()
        elif 'info' in request.POST:
            pk = request.POST.get("info")
            return redirect('home:view_event', pk)
        elif 'edit' in request.POST:
            pk = request.POST.get("edit")
            return redirect('home:edit_event', pk)
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = Event.objects.get(id=pk)
            delete_item.delete()
        elif 'sort' in request.POST:
            context['events'] = context['events'].order_by(
                request.POST['sort']
                )
        else:
            pass
    context['error'] = error
    return render(request, "home/events.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def view_event(request, event_id):
    """ Detailed selected event view. """
    context = {}
    context['current_event'] = request.user.profile.current_event
    select_item = Event.objects.get(pk=event_id)
    context['event'] = select_item
    return render(request, "home/event/view_event.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def add_event(request):
    """ Add new event. """
    context = {}
    error = ""
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    form = EventForm(
        request.POST,
        request.FILES,
        current_user=context['current_user']
        )
    if request.method == "POST":
        if form.is_valid():
            usr = form.save(commit=False)
            usr.created_by = context['current_user']
            form.save()
            return redirect('home:events')
        else:
            error = form.errors

    context['form'] = form
    context['error'] = error

    return render(request, "home/event/add_event.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def edit_event(request, event_id):
    """ Edit event. """
    errors = "no error "
    context = {}
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    edit_item = Event.objects.get(id=event_id)
    form = EventForm(instance=edit_item,
                     current_user=context['current_user']
                     )
    if request.method == "POST":
        form = EventForm(request.POST,
                         request.FILES,
                         instance=edit_item,
                         current_user=context['current_user']
                         )
        if form.is_valid():
            usr = form.save(commit=False)
            usr.updated_by = request.user
            form.save()
            errors = errors + " save"
            return redirect('home:events')
        else:
            errors = errors + "Error"

    context['form'] = form
    context['errors'] = errors
    context['event'] = edit_item

    return render(request, "home/event/edit_event.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def categories(request):
    """ View, add, edit and delete categories in table.
        Filter for current user and selected event.
    """
    form = CategoryForm()
    error = ""
    context = {}
    context['title'] = 'Категории'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['categories'] = Category.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        )
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = CategoryForm(request.POST)
                new_item = form.save(commit=False)
                new_item.created_by = context['current_user']
                new_item.event_related = context['current_event']
            else:
                save_item = Category.objects.get(id=pk)
                save_item.updated_by = context['current_user']
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
        elif 'sort' in request.POST:
            context['categories'] = context['categories'].order_by(
                request.POST['sort']
                )
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
    """ View, add, edit and delete participants in table.
        Filter for current user and selected event.
    """

    error = "s"
    context = {}
    context['title'] = 'Участники'
    context['all_selected'] = False
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['participants'] = Participant.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        )
    form = ParticipantForm(
        current_user=context['current_user'],
        current_event=context['current_event']
        )
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = ParticipantForm(
                    request.POST,
                    current_user=context['current_user'],
                    current_event=context['current_event']
                    )
                new_item = form.save(commit=False)
                new_item.created_by = context['current_user']
                new_item.event_related = context['current_event']
            else:
                save_item = Participant.objects.get(id=pk)
                save_item.updated_by = context['current_user']
                form = ParticipantForm(
                    request.POST,
                    instance=save_item,
                    current_user=context['current_user'],
                    current_event=context['current_event']
                    )
            form.save()
            form = ParticipantForm(
                current_user=context['current_user'],
                current_event=context['current_event']
                )
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = Participant.objects.get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = Participant.objects.get(id=pk)
            form = ParticipantForm(
                instance=edit_item,
                current_user=context['current_user'],
                current_event=context['current_event']
                )
        elif 'sort' in request.POST:
            context['participants'] = context['participants'].order_by(
                    request.POST['sort']
                    )
        elif 'select_all' in request.POST:
            error = "all selected pressed"
            context['all_selected'] = True
        elif 'deselect_all' in request.POST:
            error = "all selected pressed"
            context['all_selected'] = False    
        else:
            pass

    context['form'] = form
    context['error'] = error

    return render(request, "home/participants.html", context)
# ------------------------------------------------------------------------------
@login_required(login_url="login")
def participant(request, participant_id):
    participant = Participant.objects.get(pk=participant_id)
    return render(request, "home/participant/participant.html", {
        "participant": participant
    })


# -------------------------------------------------------------------------------
@login_required(login_url="login")
def competencies(request):
    """ View, add, edit and delete competencies in table.
        Filter for current user and selected event.
    """
    form = CompetencyForm()
    error = ""
    context = {}
    context['title'] = 'Компетенции'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['competencies'] = Competency.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        )
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = CompetencyForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
                usr.event_related = context['current_event']
            else:
                save_item = context['competencies'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = CompetencyForm(request.POST, instance=save_item)
            form.save()
            form = CompetencyForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['competencies'].get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = context['competencies'].get(id=pk)   
            form = CompetencyForm(instance=edit_item)
        elif 'sort' in request.POST:
            context['competencies'] = context['competencies'] .order_by(
                request.POST['sort']
                )
        else:
            pass

    context['form'] = form
    context['error'] = error

    return render(request, "home/competencies.html", context)


# ------------------------------------------------------------------------------
@login_required(login_url="login")
def competency(request, competency_id):
    competency = Competency.objects.get(pk=competency_id)
    return render(request, "home/competency/competency.html", {
        "competency": competency
    })


# ------------------------------------------------------------------------------
@login_required(login_url="login")
def user_images(request):
    """ View, add, edit and delete user images in table.
        Filter for event and current user.
    """
    form = UserImageForm()
    error = ""
    context = {}
    context['title'] = 'Изображения'
    context['current_user'] = request.user
    context['current_event'] = request.user.profile.current_event
    context['user_images'] = UserImage.objects.filter(
        created_by=context['current_user']
        )
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = UserImageForm(request.POST, request.FILES)
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
            else:
                user_image = context['user_images'].get(id=pk)
                user_image.updated_by = context['current_user']
                form = UserImageForm(
                    request.POST,
                    request.FILES,
                    instance=user_image
                    )
            form.save()
            form = UserImageForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            user_image = context['user_images'].get(id=pk)
            user_image.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            user_image = context['user_images'].get(id=pk)
            form = UserImageForm(instance=user_image)
        elif 'edit_print_templates' in request.POST:
            pk = request.POST.get('edit_print_templates')
            user_image = context['user_images'].get(id=pk)
            request.user.profile.current_image = user_image
            request.user.save()
            return redirect('home:print_templates')
        elif 'sort' in request.POST:
            context['user_images'] = context['user_images'].order_by(
                request.POST['sort']
                )
        else:
            pass

    context['form'] = form
    context['error'] = error

    return render(request, "home/user_images.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def print_templates(request):
    """ Edit template with user image. """
    form = PrintTemplateForm()
    context = {}
    context['title'] = 'Настройка печати'
    context['current_user'] = request.user
    context['user_image'] = request.user.profile.current_image
    context['image_width'] = context['user_image'].image.width
    context['image_height'] = context['user_image'].image.height
    context['current_event'] = request.user.profile.current_event
    context['user_image_id'] = context['user_image'].id
    context['print_templates'] = PrintTemplate.objects.filter(
        created_by=context['current_user'],
        user_image_related=context['user_image']
        )
    context['participants'] = Participant.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        )
    if request.method == "POST":
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = PrintTemplateForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
                usr.user_image_related = context['user_image']
            else:
                save_item = context['print_templates'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = PrintTemplateForm(request.POST, instance=save_item)
            form.save()
            form = PrintTemplateForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['print_templates'].get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = context['print_templates'].get(id=pk)
            form = PrintTemplateForm(instance=edit_item)
        elif 'sort' in request.POST:
            context['print_templates'] = context['print_templates'].order_by(
                request.POST['sort']
                )
        elif 'preview_all' in request.POST:
            page_data = {}
            text_data = []
            pk = request.POST.get('selected')
            participant = context['participants'].get(id=pk)
            for print_template in context['print_templates']:
                img = print_template.user_image_related.image
                match print_template.print_item:
                    case "fio":
                        text = f" {participant.first_name}  {
                                   participant.middle_name} {
                                   participant.last_name}"
                    case "category":
                        text = participant.category.print_title
                    case "competency":
                        text = participant.competency.print_title
                    case "event":
                        text = participant.event_related.print_title
                    case _:
                        text = "просто произвольный текст потому что я еще ничего не придумал"

                text_data.append({"print_item": print_template.print_item,
                                  "start_x": print_template.start_x,
                                  "start_y": print_template.start_y,
                                  "delta_x": print_template.delta_x,
                                  "font_color": print_template.font_color,
                                  "font_size": print_template.font_size,
                                  "text": text
                                  })
            
            page_data['page_width'] = context['user_image'].width
            page_data['page_height'] = context['user_image'].height
            page_data['image'] = img
            context['error'] = page_data
            mypdf = makepdf.make_pdf2(page_data, text_data)
        elif 'preview' in request.POST:
            
            pk = request.POST.get('preview')
            print_item = context['print_templates'].get(id=pk)
            context['error'] = print_item.user_image_related.image
            mypdf = makepdf.make_pdf(context['user_image'].width,
                                     context['user_image'].height,
                                     print_item.font_size,
                                     print_item.user_image_related.image,
                                     "Петров Иван Сидорович",
                                     print_item.start_x, print_item.start_y
                                     )
            
        else:
            pass
    context['form'] = form
   
    return render(request, "home/print_templates.html", context)
