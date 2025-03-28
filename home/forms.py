from .models import Event, Category, Participant, Competency
from .models import Profile, UserImage, PrintTemplate, Award


from django.forms import ModelForm, TextInput, DateInput
from django.forms import Textarea, Select, NumberInput
from django.forms import CheckboxInput


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
        self.fields['image'].queryset = UserImage.objects.filter(
            created_by=user
        )


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'print_title', 'badge', 'certificate']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                }),
                "print_title": Textarea(attrs={
                    'class': 'form-control',
                    'rows': 4,
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
        self.fields['badge'].queryset = UserImage.objects.filter(
                                        created_by=user
                                        )
        self.fields['certificate'].queryset = UserImage.objects.filter(
                                        created_by=user
                                        )


class UserImageForm(ModelForm):
    class Meta:
        model = UserImage
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


class ParticipantForm(ModelForm):
    class Meta:
        model = Participant
        fields = ['first_name', 'middle_name', 'last_name', 'organization',
                  'category', 'competency', 'award']
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
                "organization": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Организация'
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
        award_competency = kwargs.pop('current_competency')
        flag = False
        if award_competency is not None:
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
                competency=award_competency
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
        fields = ['print_item',
                  'start_x',
                  'start_y',
                  'delta_x',
                  'delta_y',
                  'font_color',
                  'font_size',
                  'font_alignment',
                  'font_leading'
                  ]
        widgets = {
                    "print_item": Select(attrs={
                     'class': 'form-control',
                     'placeholder': 'Поле печати'
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
        fields = ['title', 'competency', 'award']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
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
        super(AwardForm, self).__init__(*args, **kwargs)
        # Filter
        self.fields['award'].queryset = UserImage.objects.filter(
            created_by=user
        )
        self.fields['competency'].queryset = Competency.objects.filter(
            event_related=event,
            created_by=user
        )
