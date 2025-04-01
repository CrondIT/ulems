""" Import render and redirect. """
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from .models import Event, Category, Participant, Competency, UserImage
from .models import PrintTemplate, Award

from .forms import EventForm, CategoryForm, ParticipantForm, AwardForm
from .forms import CompetencyForm, UserImageForm, PrintTemplateForm

from . import makepdf

from django.core.files.storage import FileSystemStorage

import csv

from django.db.models import Count


# ----------------------------------------------------------------------------
def sort_reverse(sort_str):
    """
        Remove - at the begin of the string if - exist
        or add - if it not exist
    """
    if sort_str[0] == '-':
        new_str = sort_str[1:]
    else:
        new_str = '-' + sort_str

    return new_str


# ----------------------------------------------------------------------------
def is_sort_exist(sort_str, saved_str):
    """
        Return True, if saved in user profile sort string
        equal pressed sort value
    """

    is_sort_exist = False
    if sort_str[0] == '-':
        sort_str = sort_str[1:]
    if saved_str[0] == '-':
        saved_str = saved_str[1:]
    if sort_str == saved_str:
        is_sort_exist = True

    return is_sort_exist


# ----------------------------------------------------------------------------
def check_textblock_xy(
        page_width, page_height, start_x, start_y, delta_x, delta_y):
    """
        Remove - at the begin of the string if - exist
        or add - if it not exist
    """
    errors = {}

    if start_x > page_width:
        errors['X'] = 'Начало текстового блока по X за пределами страницы.'
    if start_y > page_height:
        errors['Y'] = 'Начало текстового блока по Y за пределами страницы.'
    if (start_x + delta_x) > page_width:
        errors['Ширина'] = 'Слишком большая ширина текстового блока.'
    if (start_y + delta_y) > page_height:
        errors['Высота'] = 'Слишком большая высота текстового блока.'

    return errors


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def index(request):
    """ View main (starter) page """
    context = {}
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['categories_count'] = Category.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        ).count()
    context['competencies_count'] = Competency.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        ).count()
    context['participants_count'] = Participant.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        ).count()
    context['competencies_by_participants'] = Competency.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        ).annotate(count=Count('participants'))
    context['categories_by_participants'] = Category.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event']
        ).annotate(count=Count('participants'))
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
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Мероприятия'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_event
    context['model'] = (Event.objects.filter(
        created_by=context['current_user']).annotate(
            count=Count('home_participant_event_related'))
        )
    context['ClassForm'] = EventForm
    form = context['ClassForm'](
        current_user=context['current_user']
        )
    if request.method == "POST":
        if 'save' in request.POST:
            pk = request.POST.get("save")
            if not pk:
                form = context['ClassForm'](
                    request.POST,
                    request.FILES,
                    current_user=context['current_user']
                    )
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context["ClassForm"](
                    request.POST,
                    request.FILES,
                    instance=save_item,
                    current_user=context['current_user']
                    )
            form.save()
            form = context['ClassForm'](current_user=context['current_user'])
        elif 'select' in request.POST:
            pk = request.POST.get("select")
            select_item = context['model'].get(id=pk)
            request.user.profile.current_event = select_item
            context['current_event'] = request.user.profile.current_event
            request.user.save()
        elif 'info' in request.POST:
            pk = request.POST.get("info")
            return redirect('home:view_event', pk)
        elif 'edit' in request.POST:
            pk = request.POST.get("edit")
            edit_item = context['model'].get(id=pk)
            context['id'] = pk
            form = context['ClassForm'](
                current_user=context['current_user'],
                instance=edit_item)
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_event = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        else:
            pass
    context['error'] = error
    context['form'] = form
    return render(request, "home/events.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def view_event(request, event_id):
    """ Detailed selected event view. """
    context = {}
    context['current_event'] = request.user.profile.current_event
    select_item = Event.objects.get(pk=event_id)
    context['item'] = select_item
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
        current_user=context['current_user'])
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
    form = EventForm(
        instance=edit_item,
        current_user=context['current_user'])
    if request.method == "POST":
        form = EventForm(
            request.POST,
            request.FILES,
            instance=edit_item,
            current_user=context['current_user'])
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
    context['item'] = edit_item

    return render(request, "home/event/edit_event.html", context)


# ----------------------------------------------------------------------------
@login_required(login_url="login")
def categories(request):
    """ View, add, edit and delete categories in table.
        Filter for current user and selected event.
    """
    error = ""
    context = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Категории'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_category
    context['model'] = Category.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event'])
    context['model'] = context['model'].order_by(
        context['sort']).annotate(
        count=Count('participants')
        )
    context['ClassForm'] = CategoryForm

    context['form'] = context['ClassForm'](
        current_user=context['current_user'])
    form = context['form']
    if 'save' in request.POST:
        pk = request.POST.get('save')
        if not pk:
            form = context['ClassForm'](
                request.POST,
                current_user=context['current_user'])
            new_item = form.save(commit=False)
            new_item.created_by = context['current_user']
            new_item.event_related = context['current_event']
        else:
            save_item = context['model'].get(id=pk)
            save_item.updated_by = context['current_user']
            form = context['ClassForm'](
                request.POST,
                instance=save_item,
                current_user=context['current_user'])
        form.save()
        form = context['ClassForm'](
            current_user=context['current_user'])
    elif 'delete' in request.POST:
        pk = request.POST.get('delete')
        delete_item = context['model'].get(id=pk)
        delete_item.delete()
    elif 'edit' in request.POST:
        pk = request.POST.get('edit')
        edit_item = context['model'].get(id=pk)
        form = context['ClassForm'](
            instance=edit_item,
            current_user=context['current_user'])
    elif 'sort' in request.POST:
        sort_str = request.POST.get('sort')
        if is_sort_exist(sort_str, context['sort']):
            context['sort'] = sort_reverse(context['sort'])
        else:
            context['sort'] = sort_str
        request.user.profile.sort_category = context['sort']
        request.user.save()
        context['model'] = context['model'].order_by(
            context['sort'])
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
    context = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Участники'
    context['all_selected'] = False
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_participant
    context['current_competency'] = None
    context['database'] = Participant
    context['model'] = context['database'].objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event'])
    error = context['sort']
    context['model'] = context['model'].order_by(
        context['sort'])
    context['ClassForm'] = ParticipantForm
    form = context['ClassForm'](
        current_user=context['current_user'],
        current_event=context['current_event'],
        current_competency=context['current_competency'])
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](
                    request.POST,
                    current_user=context['current_user'],
                    current_event=context['current_event'],
                    current_competency=context['current_competency'])
                new_item = form.save(commit=False)
                new_item.created_by = context['current_user']
                new_item.event_related = context['current_event']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                # context['current_competency'] = None
                form = context['ClassForm'](
                    request.POST,
                    instance=save_item,
                    current_user=context['current_user'],
                    current_event=context['current_event'],
                    current_competency=context['current_competency'])
            form.save()
            form = context['ClassForm'](
                current_user=context['current_user'],
                current_event=context['current_event'],
                current_competency=context['current_competency'])
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = context['model'].get(id=pk)
            if context['current_competency'] is not None:
                context['current_competency'] = Competency.objects.get(
                    id=edit_item.competency.id)
            form = context['ClassForm'](
                instance=edit_item,
                current_user=context['current_user'],
                current_event=context['current_event'],
                current_competency=context['current_competency'])
            context['anchor'] = 'row_' + pk
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_participant = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        elif 'select_all' in request.POST:
            error = "all selected pressed"
            context['all_selected'] = True
        elif 'deselect_all' in request.POST:
            error = "all selected pressed"
            context['all_selected'] = False
        elif 'export' in request.POST:
            data = {}
            with open("participants.csv", 'w', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=[
                        'first_name',
                        'middle_name',
                        'last_name',
                        'organization',
                        'category',
                        'competency',
                        'award',
                        'created_date',
                        'updated_date',
                        'created_by',
                        'updated_by',
                        'event_related'
                    ])
                writer.writeheader()
                for item in context['model']:
                    data = {
                        'first_name': item.first_name,
                        'middle_name': item.middle_name,
                        'last_name': item.last_name,
                        'organization': item.organization,
                        'category': item.category,
                        'competency': item.competency,
                        'award': item.award,
                        'created_date': item.created_date,
                        'updated_date': item.updated_date,
                        'created_by': item.created_by,
                        'updated_by': item.updated_by,
                        'event_related': item.event_related
                    }
                    writer.writerow(data)
        elif 'import' in request.POST:
            import_participants = []
            if 'file' in request.FILES:
                file = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(
                    'user_{0}/{1}'.format(
                        context['current_user'].id, file.name),
                    file
                                    )
                with open(fs.path(filename), 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    # upload data to import_participants
                    for row in reader:
                        import_participants.append({
                            'first_name': row['first_name'],
                            'middle_name': row['middle_name'],
                            'last_name': row['last_name'],
                            'organization': row['organization'],
                            'category': row['category'],
                            'competency': row['competency'],
                            'award': row['award']
                             })
                # wtite data to database participant, category and competency
                # create new records in  category and competency
                for item in import_participants:
                    if not Category.objects.filter(
                            title=item['category'],
                            created_by=context['current_user'],
                            event_related=context['current_event']).exists():
                        Category.objects.create(
                            title=item['category'],
                            print_title=item['category'],
                            created_by=context['current_user'],
                            event_related=context['current_event']
                        )
                    if not Competency.objects.filter(
                            title=item['competency'],
                            created_by=context['current_user'],
                            event_related=context['current_event']).exists():
                        Competency.objects.create(
                            title=item['competency'],
                            print_title=item['competency'],
                            created_by=context['current_user'],
                            event_related=context['current_event']
                        )

                    Participant.objects.create(
                        first_name=item['first_name'],
                        middle_name=item['middle_name'],
                        last_name=item['last_name'],
                        organization=item['organization'],
                        created_by=context['current_user'],
                        event_related=context['current_event'],
                        category=Category.objects.get(
                            title=item['category'],
                            created_by=context['current_user'],
                            event_related=context['current_event']),
                        competency=Competency.objects.get(
                            title=item['competency'],
                            created_by=context['current_user'],
                            event_related=context['current_event'])
                    )

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
    error = ""
    context = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Компетенции'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_competency
    context['model'] = Competency.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event'])
    context['model'] = context['model'].order_by(
        context['sort']).annotate(
        count=Count('participants')
        )
    context['ClassForm'] = CompetencyForm
    form = CompetencyForm()
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](request.POST)
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
                usr.event_related = context['current_event']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context['ClassForm'](request.POST, instance=save_item)
            if form.is_valid():
                form.save()
                form = context['ClassForm']()
            else:
                error = "Форма заполнена неверно!"
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = context['model'].get(id=pk)
            form = context['ClassForm'](instance=edit_item)
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_competency = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        elif 'import' in request.POST:
            import_competencies = []
            if 'file' in request.FILES:
                file = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(
                    'user_{0}/{1}'.format(
                        context['current_user'].id, file.name),
                    file
                                    )
                with open(fs.path(filename), 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    # upload data to import_participants
                    for row in reader:
                        import_competencies.append({
                            'title': row['title'],
                            'print_title': row['print_title']
                            })
                # wtite data to database participant, category and competency
                # create new records in  category and competency
                for item in import_competencies:
                    Competency.objects.create(
                        title=item['title'],
                        print_title=item['print_title'],
                        created_by=context['current_user'],
                        event_related=context['current_event']
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
    error = ""
    context = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Изображения'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_image
    context['model'] = UserImage.objects.filter(
        created_by=context['current_user'])
    context['ClassForm'] = UserImageForm
    form = context['ClassForm']()
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](
                    request.POST,
                    request.FILES)
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
            else:
                user_image = context['model'].get(id=pk)
                user_image.updated_by = context['current_user']
                form = context['ClassForm'](
                    request.POST,
                    request.FILES,
                    instance=user_image)
            form.save()
            form = context['ClassForm']()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            user_image = context['model'].get(id=pk)
            user_image.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            user_image = context['model'].get(id=pk)
            form = context['ClassForm'](instance=user_image)
        elif 'edit_print_templates' in request.POST:
            pk = request.POST.get('edit_print_templates')
            user_image = context['model'].get(id=pk)
            request.user.profile.current_image = user_image
            request.user.save()
            return redirect('home:print_templates')
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_image = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
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
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Настройка печати'
    context['current_user'] = request.user
    context['user_image'] = request.user.profile.current_image
    context['image_width'] = context['user_image'].image.width
    context['image_height'] = context['user_image'].image.height
    context['current_event'] = request.user.profile.current_event
    context['user_image_id'] = context['user_image'].id
    context['sort'] = request.user.profile.sort_template
    context['model'] = PrintTemplate.objects.filter(
        created_by=context['current_user'],
        user_image_related=context['user_image'])
    context['model'] = context['model'].order_by(
        context['sort'])
    context['participants'] = Participant.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event'])
    if request.method == "POST":
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = PrintTemplateForm(request.POST)
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
                usr.user_image_related = context['user_image']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = PrintTemplateForm(request.POST, instance=save_item)
                context['errors'] = check_textblock_xy(
                    context['user_image'].width,
                    context['user_image'].height,
                    save_item.start_x,
                    save_item.start_y,
                    save_item.delta_x,
                    save_item.delta_x
                    )
            form.save()
            form = PrintTemplateForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = context['model'].get(id=pk)
            context['id'] = pk
            form = PrintTemplateForm(instance=edit_item)
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_participant = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        elif 'preview_all' in request.POST:
            page_data = {}
            text_data = []
            pk = request.POST.get('selected')
            participant = context['participants'].get(id=pk)
            for print_template in context['model']:
                img = print_template.user_image_related.image
                match print_template.print_item:
                    case "fio":
                        print_text = f" {participant.first_name}  {
                                   participant.middle_name} {
                                   participant.last_name}"
                    case "category":
                        print_text = participant.category.print_title
                    case "competency":
                        print_text = participant.competency.print_title
                    case "event":
                        print_text = participant.event_related.print_title
                    case _:
                        print_text = "произвольный текст," \
                            "я еще ничего не придумал"

                text_data.append({
                    "print_item": print_template.print_item,
                    "start_x": print_template.start_x,
                    "start_y": print_template.start_y,
                    "delta_x": print_template.delta_x,
                    "delta_y": print_template.delta_y,
                    "font_color": print_template.font_color,
                    "font_size": print_template.font_size,
                    "font_leading": print_template.font_leading,
                    "font_alignment": print_template.font_alignment,
                    "text": print_text
                                })

            page_data['page_width'] = context['user_image'].width
            page_data['page_height'] = context['user_image'].height
            page_data['image'] = img
            context['error'] = page_data
            makepdf.make_pdf3(page_data, text_data)
        elif 'cancel' in request.POST:
            pass
        else:
            pass
    context['form'] = form

    return render(request, "home/print_templates.html", context)


# -------------------------------------------------------------------------------
@login_required(login_url="login")
def awards(request):
    """ View, add, edit and delete awards in table.
        Filter for current user and selected event.
    """
    error = ""
    context = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Награды (дипломы)'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_award
    context['model'] = Award.objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event'])
    context['model'] = context['model'].order_by(
        context['sort'])
    context['ClassForm'] = AwardForm
    form = context['ClassForm'](
        current_user=context['current_user'],
        current_event=context['current_event'])
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](
                    request.POST,
                    current_user=context['current_user'],
                    current_event=context['current_event'])
                usr = form.save(commit=False)
                usr.created_by = context['current_user']
                usr.event_related = context['current_event']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context['ClassForm'](
                    request.POST,
                    instance=save_item,
                    current_event=context['current_event'],
                    current_user=context['current_user'])
            form.save()
            form = context['ClassForm'](
                current_event=context['current_event'],
                current_user=context['current_user'])
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = context['model'].get(id=pk)
            form = context['ClassForm'](
                instance=edit_item,
                current_event=context['current_event'],
                current_user=context['current_user'])
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_award = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        else:
            pass

    context['form'] = form
    context['error'] = error

    return render(request, "home/awards.html", context)
