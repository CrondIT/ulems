from .models import Event, Category
from django.forms import ModelForm, TextInput, DateInput, Textarea

class AddEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'print_title', 'description','from_date','to_date']

        widgets = {
            "title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Наименование'
            }),
            "print_title": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Наименование для печати'
            }),
             "description": Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание'
            }),
             "from_date": DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Дата начала'
            }),
             "to_date": DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Дата окончания'
            })
        }

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'print_title']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                }),
                "print_title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование для печати'
                })
            }