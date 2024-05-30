from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404, redirect
from .models import User, Availability, Appointment, Chat, Message
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
    # Query all appointments
    appointments_list = Appointment.objects.all()

    # Pass the appointments to the template
    return render(request, "mydoctorapp/appointments.html", {"appointments": appointments_list})


def chats(request):
    # Query chats involving the current user
    chats_list = Chat.objects.filter(Q(doctor=request.user) | Q(patient=request.user))

    # Pass the chats to the template
    return render(request, "mydoctorapp/chats.html", {"chats": chats_list})


def delete_chat(request, chat_id):
    # Retrieve the chat
    chat = get_object_or_404(Chat, id=chat_id)

    # Check if the current user is the doctor or the patient involved in the chat
    if request.user == chat.doctor or request.user == chat.patient:
        # Delete the chat
        chat.delete()

    # Redirect to the chats page
    return HttpResponseRedirect(reverse('chats'))


def chat(request, chat_id=None):
    if request.method == 'POST':
        message_text = request.POST['message']
        if chat_id is not None:
            chat = get_object_or_404(Chat, id=chat_id)
        else:
            # Create a new chat
            chat = Chat.objects.create(doctor=request.user, patient=request.user)
        # Create a new message
        Message.objects.create(chat=chat, sender=request.user, message=message_text)
        return redirect('chat', chat_id=chat.id)
    else:
        chat = get_object_or_404(Chat, id=chat_id)
        messages = chat.messages.all()
        return render(request, 'mydoctorapp/chat.html', {'chat': chat, 'messages': messages})


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


def doctors(request):
    current_user = User.objects.get(id=request.user.id)

    if 'my' in request.path:
        doctors_list = current_user.saved_users.all()
    else:
        doctors_list = User.objects.filter(role='doctor')
    return render(request, 'mydoctorapp/doctors.html', {'doctors': doctors_list})


def doctor(request, doctor_id):
    doctor_record = get_object_or_404(User, id=doctor_id)
    current_user = User.objects.get(id=request.user.id)
    is_saved = current_user.saved_users.filter(id=doctor_id).exists()
    return render(request, 'mydoctorapp/doctor.html', {'doctor': doctor_record, 'is_saved': is_saved})

def patient(request, patient_id):
    patient_record = get_object_or_404(User, id=patient_id)
    return render(request, 'mydoctorapp/patient.html', {'patient': patient_record})


def add_to_saved_users(request, user_to_save_id):
    user_to_save = get_object_or_404(User, id=user_to_save_id)
    current_user = User.objects.get(id=request.user.id)
    if not current_user.saved_users.filter(id=user_to_save.id).exists():
        current_user.saved_users.add(user_to_save)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mydoctorapp/error.html", {
            "message": "User is already in the saved users list."
        })


def remove_from_saved_users(request, user_to_remove_id):
    user_to_remove = get_object_or_404(User, id=user_to_remove_id)
    current_user = User.objects.get(id=request.user.id)
    if current_user.saved_users.filter(id=user_to_remove.id).exists():
        current_user.saved_users.remove(user_to_remove)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mydoctorapp/error.html", {
            "message": "User is not in the saved users list."
        })