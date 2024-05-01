from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from .models import User, Availability
from django.contrib.auth.decorators import login_required
from .forms import ProfileImageForm, AvailabilityForm


@login_required
def index(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ProfileImageForm(instance=request.user)

    return render(request, "mydoctorapp/index.html", {
        "user": request.user,
        "form": form
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
            return render(request, "mydoctorapp/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "mydoctorapp/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        role = request.POST["role"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "mydoctorapp/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name,
                                            role=role)
            user.save()
        except IntegrityError:
            return render(request, "mydoctorapp/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mydoctorapp/register.html")


def appointments(request):
    return render(request, "mydoctorapp/appointments.html")


def messages(request):
    return render(request, "mydoctorapp/messages.html")


def availability_view(request):
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.doctor = request.user
            availability.save()
            # Redirect to a new URL:
            return HttpResponseRedirect('/availability')
    else:
        form = AvailabilityForm()

    # Get the availability data for the current user
    availability_list = Availability.objects.filter(doctor=request.user)

    return render(request, 'mydoctorapp/availability.html', {'form': form, 'availability_list': availability_list})


def delete_availability_view(request, availability_id):
    availability = get_object_or_404(Availability, id=availability_id)
    if request.user == availability.doctor:
        availability.delete()
    return HttpResponseRedirect('/availability')