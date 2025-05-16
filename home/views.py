""" Import render and redirect. """
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from .models import Event, Category, Participant, Competency, UserImage
from .models import PrintTemplate, Award, UserFont

from .forms import EventForm, CategoryForm, ParticipantForm, AwardForm
from .forms import CompetencyForm, UserImageForm, PrintTemplateForm
from .forms import UserFontForm

from . import makepdf

from django.core.files.storage import FileSystemStorage

import csv

from django.db.models import Count

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from django.template.defaulttags import register

from django.core.paginator import Paginator


# ----------------------------------------------------------------------------
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


# ----------------------------------------------------------------------------
def sort_button_pressed(sort_str):
    """
        Choose rigth font awesome icon
        for ascent or descent sorting button
    """
    if sort_str[0] == '-':
        sort_button = 'fa fa-sort-amount-desc'
        sort_text = sort_str[1:]
    else:
        sort_button = 'fa fa-sort-amount-asc'
        sort_text = sort_str
    return sort_button, sort_text


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
        page_width, page_height, start_x, start_y, delta_x, delta_y
        ):
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
    context['edit_forms'] = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Мероприятия'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_event
    context['model'] = Event.objects.filter(
        created_by=context['current_user'])
    context['model'] = context['model'].order_by(
        context['sort']).annotate(
        count=Count('home_participant_event_related')
        )
    context['ClassForm'] = EventForm
    context['form'] = context['ClassForm'](
        current_user=context['current_user']
        )
    form = context['form']

    # Генерация форм для каждого объекта
    for item in context['model']:
        context['edit_forms'][item.id] = context['ClassForm'](
            instance=item,
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
                context['id'] = pk
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context["ClassForm"](
                    request.POST,
                    request.FILES,
                    instance=save_item,
                    current_user=context['current_user']
                    )
            if form.is_valid():
                form.save()
                form = context['ClassForm'](
                    current_user=context['current_user']
                    )
                return redirect('home:events')
            else:
                error = "Форма заполнена неверно!"
        elif 'select' in request.POST:
            pk = request.POST.get("select")
            select_item = context['model'].get(id=pk)
            request.user.profile.current_event = select_item
            context['current_event'] = request.user.profile.current_event
            request.user.save()
        elif 'info' in request.POST:
            pk = request.POST.get("info")
            return redirect('home:view_event', pk)
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
            return redirect('home:events')
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
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])
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
def categories(request):
    """ View, add, edit and delete categories in table.
        Filter for current user and selected event.
    """
    error = ""
    context = {}
    context['edit_forms'] = {}
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
    # Генерация форм для каждого объекта
    for item in context['model']:
        context['edit_forms'][item.id] = context['ClassForm'](
            instance=item,
            current_user=context['current_user']
        )
    if request.method == "POST":
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](
                    request.POST,
                    current_user=context['current_user']
                    )
                new_item = form.save(commit=False)
                new_item.created_by = context['current_user']
                new_item.event_related = context['current_event']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context['ClassForm'](
                    request.POST,
                    instance=save_item,
                    current_user=context['current_user']
                    )
            if form.is_valid():
                form.save()
                form = context['ClassForm'](
                    current_user=context['current_user']
                    )
                return redirect('home:categories')
            else:
                error = "Форма заполнена неверно!"
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
            return redirect('home:categories')
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_category = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort']
                )
        else:
            pass
    context['form'] = form
    context['error'] = error
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])
    return render(request, "home/categories.html", context)


# -------------------------------------------------------------------------------
@login_required(login_url="login")
def participants(request):
    """ View, add, edit and delete participants in table.
        Filter for current user and selected event.
    """
    lines_per_page = 25  # Количество записей на странице
    context = {}
    context['edit_forms'] = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Участники'
    context['all_selected'] = False
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_participant
    context['current_category'] = None
    context['database'] = Participant
    context['model'] = context['database'].objects.filter(
        created_by=context['current_user'],
        event_related=context['current_event'])
    error = context['sort']
    context['model'] = context['model'].order_by(
        context['sort'])
    context['ClassForm'] = ParticipantForm
    context['form'] = context['ClassForm'](
        current_user=context['current_user'],
        current_event=context['current_event'],
        current_category=context['current_category']
        )
    form = context['form']
    return_page = request.session.get('return_page', 1)
    paginator = Paginator(context['model'], lines_per_page)
    page_number = request.GET.get('page')
    if not page_number:
        page_number = return_page
    context['page_obj'] = paginator.get_page(page_number)
    print("page_number: ", page_number, "return_page: ", return_page)
    
    # Генерация форм для каждого объекта
    for item in context['page_obj']:
        context['current_category'] = \
            Category.objects.get(id=item.category.id)

        context['edit_forms'][item.id] = context['ClassForm'](
            instance=item,
            current_user=context['current_user'],
            current_event=context['current_event'],
            current_category=context['current_category']
            )

    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](
                    request.POST,
                    current_user=context['current_user'],
                    current_event=context['current_event'],
                    current_category=context['current_category'])
                new_item = form.save(commit=False)
                new_item.created_by = context['current_user']
                new_item.event_related = context['current_event']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context['ClassForm'](
                    request.POST,
                    instance=save_item,
                    current_user=context['current_user'],
                    current_event=context['current_event'],
                    current_category=save_item.category)
            if form.is_valid():
                form.save()
                form = context['ClassForm'](
                    current_user=context['current_user'],
                    current_event=context['current_event'],
                    current_category=context['current_category']
                    )
                request.session['return_page'] = request.POST.get('page', 1)
                return redirect('home:participants')
            else:
                error = "Форма заполнена неверно!"
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
            return redirect('home:participants')
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
        elif 'print_certificate' in request.POST:
            # define page size and canva
            page_width = 210 * mm
            page_height = 297 * mm
            page_size = (page_width, page_height)
            canva = canvas.Canvas("helloworld.pdf", page_size)
            for participant in context['model']:
                user_image = participant.category.certificate
                print_templates = PrintTemplate.objects.filter(
                    user_image_related=user_image
                    )
                page_data = {}
                text_data = []
                for print_template in print_templates:
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
                        case "organization":
                            print_text = participant.organization
                        case "job_title":
                            print_text = participant.job_title
                        case "text":
                            print_text = participant.text
                        case _:
                            print_text = "произвольный текст," \
                                        "я еще ничего не придумал"
                    text = print_text
                    if print_template.before_print_text is not None:
                        text = print_template.before_print_text + text
                    if print_template.after_print_text is not None:
                        text = text + " " + print_template.after_print_text
                    if print_template.user_font is not None:
                        user_font_file_path = print_template.user_font.font
                    else:
                        user_font_file_path = "ARIAL.TTF"

                    text_data.append({
                        "start_x": print_template.start_x,
                        "start_y": print_template.start_y,
                        "delta_x": print_template.delta_x,
                        "delta_y": print_template.delta_y,
                        "font_color": print_template.font_color,
                        "font_size": print_template.font_size,
                        "font_leading": print_template.font_leading,
                        "font_alignment": print_template.font_alignment,
                        "text": text,
                        "user_font_file_path": user_font_file_path
                        })

                page_data['page_width'] = user_image.width
                page_data['page_height'] = user_image.height
                page_data['image'] = user_image.image
                context['error'] = page_data
                canva = makepdf.make_pdf2(page_data, text_data, canva)
            canva.save()
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
                        'job_title',
                        'text',
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
                        'job_title': item.job_title,
                        'text': item.text,
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
                            'job_title': row['job_title'],
                            'text': row['text'],
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
                        job_title=item['job_title'],
                        text=item['text'],
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
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])

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
    context['edit_forms'] = {}
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
    context['form'] = context['ClassForm']()
    form = context['form']
    # Генерация форм для каждого объекта
    for item in context['model']:
        context['edit_forms'][item.id] = context['ClassForm'](
            instance=item
            )
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](
                    request.POST
                    )
                new_item = form.save(commit=False)
                new_item.created_by = context['current_user']
                new_item.event_related = context['current_event']
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context['ClassForm'](
                    request.POST,
                    instance=save_item
                    )
            if form.is_valid():
                form.save()
                form = context['ClassForm']()
                return redirect('home:competencies')
            else:
                error = "Форма заполнена неверно!"
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
            return redirect('home:competencies')
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_competency = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort']
                )
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
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])
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


# ------------------------------------------------------------------------------
@login_required(login_url="login")
def user_fonts(request):
    """ View, add, edit and delete user fonts in table.
        Filter for event and current user.
    """
    error = ""
    context = {}
    context['sort_button'] = 'fa fa-sort'
    context['title'] = 'Шрифты'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_font
    context['model'] = UserFont.objects.filter(
        created_by=context['current_user'])
    context['ClassForm'] = UserFontForm
    form = context['ClassForm']()
    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = context['ClassForm'](
                    request.POST,
                    request.FILES)
                if form.is_valid():
                    new_item = form.save(commit=False)
                    new_item.created_by = context['current_user']
                    form.save()
                    form = context['ClassForm']()
                else:
                    error = form.errors.as_text()
            else:
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context['ClassForm'](
                    request.POST,
                    request.FILES,
                    instance=save_item)
                if form.is_valid():
                    form.save()
                    form = context['ClassForm']()
                else:
                    error = form.errors.as_data()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            edit_item = context['model'].get(id=pk)
            context['id'] = pk
            form = context['ClassForm'](
                instance=edit_item)
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_font = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        else:
            pass

    context['form'] = form
    context['error'] = error

    return render(request, "home/user_fonts.html", context)


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
                    case "organization":
                        print_text = participant.organization
                    case "job_title":
                        print_text = participant.job_title
                    case "text":
                        print_text = participant.text
                    case _:
                        print_text = "произвольный текст," \
                                        "я еще ничего не придумал"
                text = print_text
                if print_template.before_print_text is not None:
                    text = print_template.before_print_text + text
                if print_template.after_print_text is not None:
                    text = text + " " + print_template.after_print_text
                if print_template.user_font is not None:
                    user_font_file_path = print_template.user_font.font
                else:
                    user_font_file_path = "ARIAL.TTF"

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
                    "text": text,
                    "user_font_file_path": user_font_file_path
                    })

            page_data['page_width'] = context['user_image'].width
            page_data['page_height'] = context['user_image'].height
            page_data['image'] = img
            page_data['font'] = user_font_file_path
            context['error'] = page_data

            makepdf.make_pdf(page_data, text_data)

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
    context['edit_forms'] = {}
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
    context['form'] = context['ClassForm'](
        current_user=context['current_user'],
        current_event=context['current_event'])
    form = context['form']
    # Генерация форм для каждого объекта
    for item in context['model']:
        context['edit_forms'][item.id] = context['ClassForm'](
            instance=item,
            current_user=context['current_user'],
            current_event=context['current_event']
        )
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
            if form.is_valid():
                form.save()
                form = context['ClassForm'](
                    current_event=context['current_event'],
                    current_user=context['current_user'
                                         ])
                return redirect('home:awards')
            else:
                error = "Форма заполнена неверно!"
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_item = context['model'].get(id=pk)
            delete_item.delete()
            return redirect('home:awards')
        elif 'sort' in request.POST:
            sort_str = request.POST.get('sort')
            if is_sort_exist(sort_str, context['sort']):
                context['sort'] = sort_reverse(context['sort'])
            else:
                context['sort'] = sort_str
            request.user.profile.sort_award = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort']
                )
        else:
            pass

    context['form'] = form
    context['error'] = error
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])

    return render(request, "home/awards.html", context)
