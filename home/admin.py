from django.contrib import admin
from .models import Person, Event, Category, Participant

# Register your models here.
admin.site.register(Person)
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(Participant)