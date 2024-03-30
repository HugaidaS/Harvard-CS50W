from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('profile/<int:user_id>', views.profile, name='profile'),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("create", views.create, name="create"),
    path("edit/<int:listing_id>", views.edit_listing, name="edit"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_to_watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path('close_listing/<int:listing_id>', views.close_listing, name='close_listing'),
]
