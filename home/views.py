from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from .models import Event, Category, Participant, Competency, PrintImage
from .models import PrintTemplate, Award, UserFont, AllEventsImage

from .forms import EventForm, CategoryForm, ParticipantForm, AwardForm
from .forms import CompetencyForm, PrintImageForm, PrintTemplateForm
from .forms import UserFontForm, AllEventsImageForm

from . import makepdf

from django.core.files.storage import FileSystemStorage

import csv
import re

from django.db.models import Count

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from django.template.defaulttags import register

from django.core.paginator import Paginator

from datetime import date, datetime


# Определение правил замены (аналог case)
REPLACEMENT_MAP = {
    'фамилия': 'first_name',
    'имя': 'middle_name',
    'name': 'middle_name',
    'отчество': 'last_name',
    'организация': 'organization',
    'должность': 'job_title',
    'доклад': 'text',
    'категория': 'category.print_title',
    'компетенция': 'competency.print_title',
    'награда': 'award.title',
    'мероприятие': 'event.print_title',
    'дата начала': 'event.from_date',
    'дата окончания': 'event.to_date',
    # Добавьте другие правила по аналогии
}


# ----------------------------------------------------------------------------
def replace_placeholders(text, participant, request):
    """
    Заменяет выражения вида [ключ] на значения из объекта participant
    или event, используя логику, аналогичную оператору `case`.

    Args:
        text (str): Исходный текст c плейсхолдерами.
        participant: Объект, содержащий атрибуты и связанные модели.
        request: Объект запроса для доступа к текущему событию

    Returns:
        str: Текст c заменёнными плейсхолдерами.
    """

    def format_date_if_needed(value):
        """
        Форматирует дату в формате 'день месяц год', если значение — дата.
        """
        if isinstance(value, (date, datetime)):
            # Используем русские названия месяцев
            months = {
                1: 'января', 2: 'февраля', 3: 'марта',
                4: 'апреля', 5: 'мая', 6: 'июня',
                7: 'июля', 8: 'августа', 9: 'сентября',
                10: 'октября', 11: 'ноября', 12: 'декабря'
            }
            day = value.day
            month = months[value.month]
            year = value.year
            return f"{day} {month} {year}"
        return str(value) if value is not None else ''

    def replace_match(match):
        key = match.group(1).lower()  # Извлекаем ключ из квадратных скобок
        path = REPLACEMENT_MAP.get(key)

        if not path:
            return f"[{key}]"  # Если ключ не найден, оставляем как есть

        # Разделяем путь на части
        parts = path.split('.')

        # Определяем начальный объект для поиска значений
        if path.startswith('event.'):
            # Для event путей используем текущее событие из профиля польз.
            current = request.user.profile.current_event
            parts = parts[1:]  # Убираем префикс 'event.'
        else:
            # Для остальных путей используем participant
            current = participant

        try:
            for part in parts:
                # Получаем значение по цепочке
                current = getattr(current, part)
            return format_date_if_needed(current)
        except (AttributeError, ValueError):
            return ''  # Если путь недоступен, возвращаем пустую строку

    return re.sub(r'\[([а-яА-ЯёЁ\w]+)\]', replace_match, text)


# ----------------------------------------------------------------------------
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


# ----------------------------------------------------------------------------
def sort_button():
    """
        Choose font awesome icon
        for initial sort buttton
    """
    return 'fa fa-sort'


# ----------------------------------------------------------------------------
def sort_button_pressed(sort_str):
    """
        Choose font awesome icon
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
def user_profile(request):
    """ view user profile """
    context = {}
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['title'] = 'Профиль пользователя'

    return render(request, "home/user_profile.html", context)


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
    context['sort_button'] = sort_button()
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
    context['sort_button'] = sort_button()
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
        elif 'print_certificate' or 'print_badge' in request.POST:
            page_data = {}

            if 'print_badge' in request.POST:
                pk = request.POST.get('print_badge')
                user_image = item.badge
                outputfilename = item.badge.title+".pdf"
            else:
                pk = request.POST.get('print_certificate')
                user_image = item.certificate
                outputfilename = item.certificate.title+".pdf"

            item = context['model'].get(id=pk)
            participants = Participant.objects.filter(
                created_by=context['current_user'],
                event_related=context['current_event'],
                category=item)
            print_templates = PrintTemplate.objects.filter(
                    user_image_related=user_image
                    )

            page_data['page_width'] = user_image.width
            page_data['page_height'] = user_image.height
#            page_data['image'] = user_image.print_image.image

            page_width = page_data['page_width'] * mm
            page_height = page_data['page_height'] * mm
            page_size = (page_width, page_height)
            canva = canvas.Canvas(outputfilename, page_size)

            for participant in participants:
#               user_image = participant.category.certificate
                print_templates = PrintTemplate.objects.filter(
                    user_image_related=user_image
                    )
                text_data = []
                for print_template in print_templates:
                    if print_template.print_text is not None:
                        print_text = replace_placeholders(
                            print_template.print_text,
                            participant,
                            request
                            )
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
                        "text": print_text,
                        "user_font_file_path": user_font_file_path
                        })
                page_data['image'] = user_image.print_image.image
                canva = makepdf.make_pdf2(page_data, text_data, canva)
            canva.save()
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
    # Получаем и валидируем параметр per_page
    try:
        lines_per_page = int(request.GET.get(
            'per_page',
            request.session.get('per_page', 25)))
        # Ограничение от 1 до 1000
        lines_per_page = max(1, min(lines_per_page, 1000))
    except (ValueError, TypeError):
        lines_per_page = 25  # Значение по умолчанию при ошибке
    request.session['per_page'] = lines_per_page
    # lines_per_page = 25  # Количество записей на странице
    context = {}
    context['edit_forms'] = {}
    context['sort_button'] = sort_button()
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
                    if print_template.print_text is not None:
                        print_text = replace_placeholders(
                            print_template.print_text,
                            participant,
                            request
                            )
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
                        "text": print_text,
                        "user_font_file_path": user_font_file_path
                        })

                page_data['page_width'] = user_image.width
                page_data['page_height'] = user_image.height
                page_data['image'] = (
                    print_template.user_image_related.print_image.image
                    )
                canva = makepdf.make_pdf2(page_data, text_data, canva)
            canva.save()
        elif 'export' in request.POST:
            data = {}
            with open("participants.csv", 'w', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    delimiter=';',
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
                    reader = csv.DictReader(csvfile, delimiter=';')
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
            return redirect('home:participants')

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
    context['sort_button'] = sort_button()
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
                    reader = csv.DictReader(csvfile, delimiter=';')
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
def all_events_images(request):
    """ View, add, edit and delete user images in table.
        Filter for event and current user.
    """
    error = ""
    context = {}
    context['sort_button'] = sort_button()
    context['title'] = 'Изображения'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_all_events_image
    context['model'] = AllEventsImage.objects.filter(
        created_by=context['current_user'])
    context['model'] = context['model'].order_by(
        context['sort'])
    context['ClassForm'] = AllEventsImageForm
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
                save_item = context['model'].get(id=pk)
                save_item.updated_by = context['current_user']
                form = context['ClassForm'](
                    request.POST,
                    request.FILES,
                    instance=save_item)
            form.save()
            form = context['ClassForm']()
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
            request.user.profile.sort_all_events_image = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        else:
            pass

    context['form'] = form
    context['error'] = error
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])
    return render(request, "home/all_events_images.html", context)


# ------------------------------------------------------------------------------
@login_required(login_url="login")
def print_images(request):
    """ View, add, edit and delete user images in table.
        Filter for event and current user.
    """
    error = ""
    context = {}
    context['sort_button'] = sort_button()
    context['title'] = 'Изображения для печати'
    context['current_event'] = request.user.profile.current_event
    context['current_user'] = request.user
    context['sort'] = request.user.profile.sort_image
    context['model'] = PrintImage.objects.filter(
        created_by=context['current_user'])
    context['model'] = context['model'].order_by(
        context['sort'])
    context['ClassForm'] = PrintImageForm
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
            edit_item = context['model'].get(id=pk)
            request.user.profile.current_image = edit_item
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
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])

    return render(request, "home/print_images.html", context)


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
    context['model'] = context['model'].order_by(
        context['sort'])
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
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])

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
    context['image_width'] = context['user_image'].print_image.image.width
    context['image_height'] = context['user_image'].print_image.image.height
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
            request.user.profile.sort_template = context['sort']
            request.user.save()
            context['model'] = context['model'].order_by(
                context['sort'])
        elif 'preview_all' in request.POST:
            page_data = {}
            text_data = []
            pk = request.POST.get('selected')
            participant = context['participants'].get(id=pk)
            for print_template in context['model']:
                img = print_template.user_image_related.print_image.image
                if print_template.print_text is not None:
                    print_text = replace_placeholders(
                        print_template.print_text,
                        participant,
                        request
                    )
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
                    "text": print_text,
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
    context['sort_button_pressed'], context['sort_text'] = \
        sort_button_pressed(context['sort'])

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
