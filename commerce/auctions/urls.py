from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("create", views.create, name="create"),
    path("edit/<int:listing_id>", views.edit_listing, name="edit"),
]
