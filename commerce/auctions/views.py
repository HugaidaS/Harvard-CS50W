from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from .forms import ListingForm
from .models import User, Category, Listing, LISTING_STATUS, Comment, Bid


def index(request):
    listings = Listing.objects.filter(status='active')

    return render(request, "auctions/index.html", {
        "listings": listings,
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
    categories = Category.objects.all()
    if request.method == 'POST':
        # Retrieve the form data from the POST request
        title = request.POST.get('title')
        description = request.POST.get('description')
        starting_bid = request.POST.get('starting_bid')
        image_url = request.POST.get('image_url')
        category_id = request.POST.get('category')

        # Set the status to 'active' by default
        status = 'active'

        # Validate the form data
        if not title or not description or not starting_bid or not image_url or not category_id:
            # One or more fields are missing
            return render(request, 'auctions/create.html', {'error': 'All fields are required.', 'categories': categories})

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            # The category does not exist
            return render(request, 'auctions/create.html', {'error': 'Invalid category.', 'categories': categories})

        # Save the form data to the database
        listing = Listing(title=title, description=description, starting_bid=starting_bid, status=status, image_url=image_url, category=category, author=request.user)
        listing.save()

        return redirect('listing', listing_id=listing.id)
    else:
        return render(request, 'auctions/create.html', {'categories': categories})


def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    isUserAuthor = request.user == listing.author
    isOnWatchList = False
    comments = Comment.objects.filter(listing_item=listing).order_by('-creation_date')

    current_bid = Bid.objects.filter(listing_item=listing).order_by('-value').first()
    current_bidder = current_bid.bidder if current_bid else None
    total_bids = Bid.objects.filter(listing_item=listing).count()

    if request.user.is_authenticated:
        isOnWatchList = request.user.watchlist.filter(id=listing_id)

    return render(request, 'auctions/listing.html', {
    'listing': listing,
    'isUserAuthor': isUserAuthor,
    'isOnWatchList': isOnWatchList,
    'comments': comments,
    'current_bid': current_bid if current_bid else listing.starting_bid,
    'current_bidder': current_bidder,
    'total_bids': total_bids
    })

from django.core.exceptions import ValidationError

def edit_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == 'POST':
        # Retrieve the form data from the POST request
        title = request.POST.get('title')
        description = request.POST.get('description')
        starting_bid = request.POST.get('starting_bid')
        status = request.POST.get('status')
        image_url = request.POST.get('image_url')
        category_id = request.POST.get('category')

        # Validate the form data
        if not title or not description or not starting_bid or not status or not image_url or not category_id:
            # One or more fields are missing
            return render(request, 'auctions/edit_listing.html', {'error': 'All fields are required.'})

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            # The category does not exist
            return render(request, 'auctions/edit_listing.html', {'error': 'Invalid category.'})

        # Save the form data to the database
        listing.title = title
        listing.description = description
        listing.starting_bid = starting_bid
        listing.status = status
        listing.image_url = image_url
        listing.category = category

        # If the listing status is 'closed', set the winner to the user with the highest bid
        if status == 'closed':
            highest_bid = listing.bids.order_by('-value').first()
            if highest_bid:
                listing.winner = highest_bid.bidder

        listing.save()

        return redirect('listing', listing_id=listing_id)
    else:
        form = ListingForm(instance=listing, author=request.user)
    return render(request, 'auctions/edit_listing.html', {'form': form, 'listing': listing})


def close_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    # Check if the current user is the author of the listing and if the listing is active
    if request.user == listing.author and listing.status == 'active':
        # Close the listing
        listing.status = 'closed'

        # Set the winner to the user with the highest bid, if any
        highest_bid = listing.bids.order_by('-value').first()
        if highest_bid:
            listing.winner = highest_bid.bidder

        # Save the changes to the database
        listing.save()

        messages.success(request, 'The listing has been successfully closed.')
    else:
        messages.error(request, 'You are not authorized to close this listing.')

    return redirect('listing', listing_id=listing_id)


# edit or create comment
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == 'POST':
        comment = request.POST['comment']

        # Validate the comment
        if not comment or len(comment) < 5:
            messages.error(request, 'Your comment must be at least 5 characters long.')
            return redirect('listing', listing_id=listing_id)

        Comment.objects.create(listing_item=listing, comment=comment, author=request.user)

    return redirect('listing', listing_id=listing_id)


def bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == 'POST':
        bid = request.POST['bid']

        # Validate the bid
        if not bid:
            messages.error(request, 'Your bid must not be empty.')
            return redirect('listing', listing_id=listing_id)

        bid = float(bid)
        current_bid = Bid.objects.filter(listing_item=listing).order_by('-value').first()

        if request.user == listing.author:
            messages.error(request, 'You cannot bid on your own listing.')
            return redirect('listing', listing_id=listing_id)

        # If there are no bids yet, compare with the starting bid
        if current_bid is None:
            if bid <= listing.starting_bid:
                messages.error(request, 'Your bid must be higher than the starting bid.')
                return redirect('listing', listing_id=listing_id)
        else:
            # If there are bids, compare with the highest bid
            if bid <= current_bid.value:
                messages.error(request, 'Your bid must be higher than the current bid.')
                return redirect('listing', listing_id=listing_id)

        # If the bid is higher, create a new bid
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

def profile(request, user_id):
    user = User.objects.get(id=user_id)
    listings = Listing.objects.filter(author=user)
    watchlistListIDs = [listing.id for listing in user.watchlist.all()]
    watchlist = Listing.objects.filter(id__in=watchlistListIDs)
    return render(request, 'auctions/profile.html', {'listings': listings, 'watchlist': watchlist, 'user': user})