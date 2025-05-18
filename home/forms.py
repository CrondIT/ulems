from .models import Event, Category, Participant, Competency
from .models import Profile, PrintImage, PrintTemplate, Award
from .models import UserFont, AllEventsImage

from django.forms import ModelForm, TextInput, DateInput
from django.forms import Textarea, Select, NumberInput
from django.forms import CheckboxInput

from django.core.exceptions import ValidationError


def validate_font(value):
    if not value.name.endswith('.ttf') and not value.name.endswith('.otf'):
        raise ValidationError(u'Недопустимый формат файла')


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'print_title',
            'description',
            'team_registration',
            'from_date',
            'to_date',
            'image'
            ]
        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Наименование'
            }),
            "print_title": Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Наименование для печати'
            }),
            "description": Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание'
            }),
            "team_registration": CheckboxInput(attrs={
                'class': 'form-check-input',
                'placeholder': 'Можно регистрировать команды'
            }),
            "from_date": DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'type': "date",
                'placeholder': 'Дата начала'
            }),
            "to_date": DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Дата окончания'
            }),
            "image": Select(attrs={
                'class': 'form-select',
                'placeholder': 'Изображение'
                })
        }
        labels = {
            "title": "Наименование мероприятия",
            "print_title": "Наименование для печати",
            "description": "Описание мероприятия",
            "team_registration": "Можно регистрировать команды",
            "from_date": "Дата начала",
            "to_date": "Дата окончания",
            "image": "Изображение"
        }

    def __init__(self, *args, **kwargs):
        # Extract the user from the view
        user = kwargs.pop('current_user')
        super(EventForm, self).__init__(*args, **kwargs)
        # Filter
        self.fields['image'].queryset = AllEventsImage.objects.filter(
            created_by=user
        )


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'print_title', 'badge', 'certificate']
        labels = {
            "title": "Наименование",
            "print_title": "Наименование для печати",
            "badge": "Бэдж",
            "certificate": "Сертификат"
        }
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                }),
                "print_title": Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Наименование для печати'
                }),
                "badge": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Бэдж'
                }),
                "certificate": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Сертификат'
                })
            }

    def __init__(self, *args, **kwargs):
        # Extract the user from the view
        user = kwargs.pop('current_user')
        super(CategoryForm, self).__init__(*args, **kwargs)
        # Filter
        self.fields['badge'].queryset = PrintImage.objects.filter(
                                        created_by=user
                                        )
        self.fields['certificate'].queryset = PrintImage.objects.filter(
                                        created_by=user
                                        )


class ImageForm(ModelForm):
    class Meta:
        model = AllEventsImage
        fields = ['title', 'image']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                })
            }


class PrintImageForm(ModelForm):
    class Meta:
        model = PrintImage
        fields = ['title', 'image', 'width', 'height']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                }),
                "width": NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Ширина, мм'}),
                "height": NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Высота, мм'})
            }


class UserFontForm(ModelForm):
    class Meta:
        model = UserFont
        fields = ['title', 'font']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                })
        }

    def clean_font(self):
        font = self.cleaned_data['font']
        if not font.name.endswith('.ttf') and not font.name.endswith('.otf'):
            raise ValidationError(u'Недопустимый формат файла')

        return font


class ParticipantForm(ModelForm):
    class Meta:
        model = Participant
        fields = ['first_name', 'middle_name', 'last_name', 'organization',
                  'job_title', 'text', 'category', 'competency', 'award']
        labels = {
            "first_name": "Фамилия",
            "middle_name": "Имя",
            "last_name": "Отчество",
            "organization": "Организация",
            "job_title": "Должность",
            "text": "Доклад",
            "category": "Категория",
            "competency": "Компетенция",
            "award": "Награда"
        }
        widgets = {
                "first_name": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Фамилия'
                }),
                "middle_name": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Имя'
                }),
                "last_name": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Отчество'
                }),
                "organization": Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Организация'
                }),
                "job_title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Должность'
                }),
                "text": Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Доклад'
                }),
                "category": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Категория'
                }),
                "competency": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Компетенция'
                }),
                "award": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Награда'
                })
            }

    def __init__(self, *args, **kwargs):
        # Extract the user from the view
        user = kwargs.pop('current_user')
        event = kwargs.pop('current_event')
        award_category = kwargs.pop('current_category')
        flag = False
        if award_category is not None:
            flag = True

        super(ParticipantForm, self).__init__(*args, **kwargs)
        # Filter
        self.fields['category'].queryset = Category.objects.filter(
            event_related=event,
            created_by=user
        )
        self.fields['competency'].queryset = Competency.objects.filter(
            event_related=event,
            created_by=user
        )
        if flag:
            self.fields['award'].queryset = Award.objects.filter(
                event_related=event,
                created_by=user,
                category=award_category
            )
        else:
            self.fields['award'].queryset = Award.objects.filter(
                event_related=event,
                created_by=user
            )


class CompetencyForm(ModelForm):
    class Meta:
        model = Competency
        fields = ['title', 'print_title']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                }),
                "print_title": Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Наименование для печати'
                })
            }


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['current_event']


class PrintTemplateForm(ModelForm):
    class Meta:
        model = PrintTemplate
        fields = [
            'before_print_text',
            'print_item',
            'after_print_text',
            'start_x',
            'start_y',
            'delta_x',
            'delta_y',
            'user_font',
            'font_color',
            'font_size',
            'font_alignment',
            'font_leading'
            ]
        widgets = {
            "before_print_text": Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Фиксированный текст до поля печати'
            }),
            "print_item": Select(attrs={
                'class': 'form-control',
                'placeholder': 'Поле печати'
            }),
            "after_print_text": Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Фиксированный текс после поля печати'
            }),
            "start_x": NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Начало по Х'
             }),
            "start_y": NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Начало по Y'
            }),
            "delta_x": NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Высота текстового блока'
            }),
            "delta_y": NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ширина текстового блока'
            }),
            "user_font": Select(attrs={
                'class': 'form-control',
                'placeholder': 'Шрифт'
            }),
            "font_color": TextInput(attrs={
                'type': 'color',
                'class': 'form-control',
                'placeholder': 'Цвет шрифта'
            }),
            "font_size": NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Размер шрифта'
            }),
            "font_leading": NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Межстрочный интервал'
            }),
            "font_alignment": Select(attrs={
                'class': 'form-control',
                'placeholder': 'Выравнивание текстового блока'
            })
            }


class AwardForm(ModelForm):
    class Meta:
        model = Award
        fields = ['title', 'category', 'award']
        labels = {
            "title": "Наименование",
            "category": "Категория",
            "award": "Награда"
        }
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                }),
                "category": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Категория'
                }),
                "award": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Награда'
                })
            }

    def __init__(self, *args, **kwargs):
        # Extract the user from the view
        user = kwargs.pop('current_user')
        event = kwargs.pop('current_event')
        super(AwardForm, self).__init__(*args, **kwargs)
        # Filter
        self.fields['award'].queryset = PrintImage.objects.filter(
            created_by=user
        )
        self.fields['category'].queryset = Category.objects.filter(
            event_related=event,
            created_by=user
        )
