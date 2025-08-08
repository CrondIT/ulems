from django.urls import path, include
from . import views

app_name = "home"
urlpatterns = [
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("event/<int:event_id>", views.view_event, name="view_event"),
    # path("event/<int:event_id>/edit", views.edit_event, name="edit_event"),
    # path("event/", views.add_event, name="add_event"),
    path("categories", views.categories, name="categories"),
    # path("category/<int:category_id>", views.category, name="category"),
    path("participants/", views.participants, name="participants"),
    path("participant/<int:participant_id>",
         views.participant,
         name="participant"
         ),
    path("competencies", views.competencies, name="competencies"),
    path("competency/<int:competency_id>",
         views.competency,
         name="competency"
         ),
    path("print_images", views.print_images, name="print_images"),
    path("all_events_images",
         views.all_events_images,
         name="all_events_images"
         ),
    path("user_fonts", views.user_fonts, name="user_fonts"),
    path("print_templates", views.print_templates,  name="print_templates"),
    path("awards", views.awards, name="awards"),
    path("users/", include('users.urls')),

]
