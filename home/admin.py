from django.contrib import admin

from .models import Competency, Event, Category, Participant
from .models import Profile, UserImage, PrintTemplate


# Register your models here.
class AuditAdmin(admin.ModelAdmin):
    fieldset_preset = ['created_date', 'updated_date',
                       'created_by', 'updated_by']
    readonly_fields = ['created_date', 'updated_date',
                       'created_by', 'updated_by']
    actions_on_top = True

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()


admin.site.register(Competency, AuditAdmin)
admin.site.register(Event, AuditAdmin)
admin.site.register(Category, AuditAdmin)
admin.site.register(Participant, AuditAdmin)
admin.site.register(Profile, AuditAdmin)
admin.site.register(UserImage, AuditAdmin)
admin.site.register(PrintTemplate, AuditAdmin)