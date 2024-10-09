from django.urls import path
from . import views

app_name = "home"
urlpatterns=[
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("categories", views.categories, name="categories")
]