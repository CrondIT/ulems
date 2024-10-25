from django.contrib import admin
from .models import Competency, Event, Category, Participant

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    fields = ['title', 'print_title', 'created_date', 'updated_date', 'author']
    readonly_fields =  ['created_date', 'updated_date', 'author']

admin.site.register(Competency)
admin.site.register(Event)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Participant)