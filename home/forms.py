from .models import Event, Category, Participant, Competency
from .models import Profile, UserImage, PrintTemplate


from django.forms import ModelForm, TextInput, DateInput
from django.forms import Textarea, Select, NumberInput


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'print_title', 'description',
                  'from_date', 'to_date', 'image']
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
            "description": Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание'
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
            })
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
        fields = ['title', 'print_title']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                }),
                "print_title": Textarea(attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Наименование для печати'
                })
              
                
            }


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
                  'category', 'competency']
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
                })
            }

    def __init__(self, *args, **kwargs):
      	# Extract the user from the view
        user = kwargs.pop('current_user')
        event = kwargs.pop('current_event')
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
                    'rows': 4,
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
                  'font_color',
                  'font_size'
                  ]
        widgets = {
                "print_item": Select(attrs={
                    'class': 'form-control',
                    'placeholder': 'Поле печати'
                }),
                "start_x": NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Начальная позиция по Х'
                }),
                "start_y": NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Начальная позиция по Y'
                }),
                "delta_x": NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Дельта X'
                }),
                "font_color": TextInput(attrs={
                    'type': 'color',
                    'class': 'form-control',
                    'placeholder': 'Цвет шрифта'
                }),
                "font_size": NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Размер шрифта'
                })
            }
