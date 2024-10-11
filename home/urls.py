from django.urls import path
from . import views

app_name = "home"
urlpatterns=[
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
    path("event/<int:event_id>", views.event, name="event"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
]