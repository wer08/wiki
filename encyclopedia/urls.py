from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search",views.search, name="search"),
    path("add", views.add, name="add"),
    path("edit", views.edit, name="edit"),
    path("random_page", views.random_page, name="random"),
    path("<str:title>", views.entry, name="entry")  
]
