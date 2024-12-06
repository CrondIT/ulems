from .models import Event, Category, Participant, Competency
from .models import Profile, UserImage


from django.forms import ModelForm, TextInput, DateInput, Textarea

from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

class AddEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'print_title', 'description',
                  'from_date', 'to_date', 'image'
                  ]

        def __init__(self, *args, **kwargs):
            # Extract the user from the view
            user = kwargs.pop('user')
            super(ParticipantForm, self).__init__(*args, **kwargs)
            # Filter 
            self.fields['image'].queryset = Category.objects.filter(
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
                "print_title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование для печати'
                })
            }


class UserImageForm(ModelForm):
    class Meta:
        model = UserImage
        fields = ['title', 'image']
        widgets = {
                "title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование'
                })
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
                "print_title": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Наименование для печати'
                })
            }   


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['current_event']
