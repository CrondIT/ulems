from .models import Event, Category, Participant, Competency, Profile, UserImage
from django.forms import ModelForm, TextInput, DateInput, Textarea


class AddEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'print_title', 'description','from_date','to_date','cover']
        label = {'from_date':'label1'}

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
                'type': 'date',
                'placeholder': 'Дата начала'
            }),
            "to_date": DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
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
        fields = ['first_name', 'middle_name', 'last_name', 'organization', 'category', 'competency']
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
        user = kwargs.pop('user')
        current_event = kwargs.pop('current_event')
        super(ParticipantForm, self).__init__(*args, **kwargs)
        # Filter 
        self.fields['category'].queryset = Category.objects.filter(event_related=current_event, created_by=user)    
        self.fields['competency'].queryset = Competency.objects.filter(event_related=current_event, created_by=user)  
        

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