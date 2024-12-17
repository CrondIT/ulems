from django.urls import path
from . import views

app_name = "home"
urlpatterns = [
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("event/<int:event_id>", views.view_event, name="view_event"),
    path("event/<int:event_id>/edit", views.edit_event, name="edit_event"),
    path("event/", views.add_event, name="add_event"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("participants", views.participants, name="participants"),
    path("participant/<int:participant_id>",
         views.participant,
         name="participant"
         ),
    path("competencies", views.competencies, name="competencies"),
    path("competency/<int:competency_id>",
         views.competency,
         name="competency"
         ),
    path("user_images", views.user_images, name="user_images"),
    # path("user_image/<int:user_image_id>/edit",
    #     views.user_images, name="user_image"
    #     ),
    #vpath("print_templates_table", views.print_templates, name="print_templates_table"),
    
    path("print_templates", views.print_templates,  name="print_templates" ),
]
