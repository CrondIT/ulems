from django.contrib import admin
from .models import Competency, Event, Category, Participant

# Register your models here.
admin.site.register(Competency)
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(Participant)