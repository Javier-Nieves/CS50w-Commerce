from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create_view, name="create"),
    path("edit/<str:title>", views.edit_view, name="edit"),
    path("listings/<str:title>", views.listing_view, name="view"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("closed", views.closed_view, name="closed"),
    path("categories", views.all_categories, name="allCategories"),
    path("categories/<str:category_name>", views.category_list, name="categoryList"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
