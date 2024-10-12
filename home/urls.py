from django.urls import path
from . import views

app_name = "home"
urlpatterns=[
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("event/<int:event_id>", views.event, name="event"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("participants", views.participants, name="participants"),
    path("participant/<int:participant_id>", views.participant, name="participant"),
    path("competencies", views.competencies, name="competencies"),
    path("competency/<int:competency_id>", views.competency, name="competency"),
]