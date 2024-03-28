from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms


from .forms import ListingForm
from .models import User, Category, Listing, LISTING_STATUS, Comment, Bid


def index(request):
    listings = Listing.objects.filter(status='active')
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    categories = Category.objects.all()
    categoriesList = [{category.name, category.id} for category in categories]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category_id):
    category = Category.objects.get(id=category_id)
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })

def create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, author=request.user)  # Pass the current user to the form
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to a success page or any other URL
    else:
        form = ListingForm(author=request.user)  # Pass the current user to the form

    return render(request, 'auctions/create.html', {'form': form})

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    isUserAuthor = request.user == listing.author
    isOnWatchList = False
    comments = Comment.objects.filter(listing_item=listing)
    current_bid = Bid.objects.filter(listing_item=listing).order_by('-value').first()

    if request.user.is_authenticated:
        isOnWatchList = request.user.watchlist.filter(id=listing_id)

    return render(request, 'auctions/listing.html', {
    'listing': listing,
    'isUserAuthor': isUserAuthor,
    'isOnWatchList': isOnWatchList,
    'comments': comments,
    'current_bid': current_bid if current_bid else listing.starting_bid
    })

def edit_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing, author=request.user)
        if form.is_valid():
            form.save()
            return redirect('listing', listing_id=listing_id)
    else:
        form = ListingForm(instance=listing, author=request.user)
    return render(request, 'auctions/edit_listing.html', {'form': form, 'listing': listing})

# edit or create comment
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == 'POST':
        comment = request.POST['comment']
        Comment.objects.create(listing_item=listing, comment=comment, author=request.user)
    return redirect('listing', listing_id=listing_id)

def bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == 'POST':
        bid = request.POST['bid']
        Bid.objects.create(listing_item=listing, bidder=request.user, value=bid)
    return redirect('listing', listing_id=listing_id)

def delete(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.delete()
    return redirect('index')

def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    request.user.watchlist.add(listing)
    return redirect('listing', listing_id=listing_id)

def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    request.user.watchlist.remove(listing)
    return redirect('listing', listing_id=listing_id)

def watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, 'auctions/index.html', {'listings': watchlist})
