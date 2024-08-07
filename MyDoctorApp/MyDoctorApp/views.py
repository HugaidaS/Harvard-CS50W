from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, reverse, get_object_or_404, redirect
from .models import User, Availability, Appointment
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


@login_required
def appointments(request):
    # Query all appointments for the current user as doctor or patient
    appointments_list = (Appointment.objects.filter(Q(doctor=request.user) | Q(patient=request.user)))

    userRecord = User.objects.get(id=request.user.id)

    # Pass the appointments to the template
    return render(request, "mydoctorapp/appointments.html",
                  {"appointments": appointments_list, "role": userRecord.role})


@login_required
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


@login_required
def delete_availability_view(request, availability_id):
    availability = get_object_or_404(Availability, id=availability_id)
    if request.user == availability.doctor:
        try:
            appointment = Appointment.objects.get(availability=availability)
            appointment.delete()
        except Appointment.DoesNotExist:
            pass
        availability.delete()
    return HttpResponseRedirect('/availability')


@login_required
def doctors(request):
    current_user = User.objects.get(id=request.user.id)

    if 'my' in request.path:
        doctors_list = current_user.saved_users.all()
    else:
        doctors_list = User.objects.filter(role='doctor')
    return render(request, 'mydoctorapp/doctors.html', {'doctors': doctors_list})


def patients(request):
    current_user = User.objects.get(id=request.user.id)
    patients_list = current_user.saved_users.all()
    return render(request, 'mydoctorapp/patients.html', {'patients': patients_list})


@login_required
def doctor(request, doctor_id):
    doctor_record = get_object_or_404(User, id=doctor_id)
    current_user = User.objects.get(id=request.user.id)
    is_saved = current_user.saved_users.filter(id=doctor_id).exists()
    return render(request, 'mydoctorapp/doctor.html', {'doctor': doctor_record, 'is_saved': is_saved})


@login_required
def patient(request, patient_id):
    patient_record = get_object_or_404(User, id=patient_id)
    current_user = User.objects.get(id=request.user.id)
    is_saved = current_user.saved_users.filter(id=patient_id).exists()
    return render(request, 'mydoctorapp/patient.html', {'patient': patient_record, 'is_saved': is_saved})


@login_required
def add_to_saved_users(request, user_to_save_id):
    user_to_save = get_object_or_404(User, id=user_to_save_id)
    current_user = User.objects.get(id=request.user.id)
    if not current_user.saved_users.filter(id=user_to_save.id).exists():
        current_user.saved_users.add(user_to_save)
        if current_user.role == 'doctor':
            return HttpResponseRedirect(reverse("my_patients"))
        else:
            return HttpResponseRedirect(reverse("my_doctors"))
    else:
        return render(request, "mydoctorapp/error.html", {
            "message": "User is already in the saved users list."
        })


@login_required
def remove_from_saved_users(request, user_to_remove_id):
    user_to_remove = get_object_or_404(User, id=user_to_remove_id)
    current_user = User.objects.get(id=request.user.id)
    if current_user.saved_users.filter(id=user_to_remove.id).exists():
        current_user.saved_users.remove(user_to_remove)
        if current_user.role == 'doctor':
            return HttpResponseRedirect(reverse("my_patients"))
        else:
            return HttpResponseRedirect(reverse("my_doctors"))
    else:
        return render(request, "mydoctorapp/error.html", {
            "message": "User is not in the saved users list."
        })


@login_required
def book_appointment(request, doctor_id, availability_id):
    doctorRecord = get_object_or_404(User, id=doctor_id)
    availability = get_object_or_404(Availability, id=availability_id)
    if availability.is_reserved:
        return render(request, "mydoctorapp/error.html", {
            "message": "This appointment is already reserved."
        })
    start_datetime = timezone.make_aware(datetime.combine(availability.appointment_date, availability.start_time))
    end_datetime = timezone.make_aware(datetime.combine(availability.appointment_date, availability.end_time))
    appointment = Appointment(doctor=doctorRecord, patient=request.user, start_time=start_datetime,
                              end_time=end_datetime, availability=availability)
    appointment.save()
    availability.is_reserved = True
    availability.save()
    return HttpResponseRedirect(reverse("appointments"))


@login_required
def update_appointment_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = User.objects.get(id=request.user.id)
    availability = appointment.availability

    # Check if the user is authorized to update the status of the appointment
    if user != appointment.doctor and user != appointment.patient:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # If the user is a doctor
    if user.role == 'doctor':
        if new_status != 'Completed':
            if new_status == 'Patient Absent':
                appointment.patient.missed_appointments += 1
                appointment.patient.save()
        availability.delete()

    # If the user is a patient
    elif user.role == 'patient':
        user.missed_appointments += 1
        user.save()
        availability.is_reserved = False
        availability.save()

    else:
        return JsonResponse({'error': 'Unauthorized action.'}, status=401)

    # Delete appointment
    appointment.delete()

    return JsonResponse({'message': 'Appointment status updated successfully'}, status=200)