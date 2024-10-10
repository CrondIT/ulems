from django.urls import path
from . import views

app_name = "home"
urlpatterns=[
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("<int:event_id>", views.event, name="event"),
    path("categories", views.categories, name="categories")
]