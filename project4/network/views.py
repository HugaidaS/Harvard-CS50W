from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Like


def index(request):
    posts = Post.objects.all().order_by("-created_at")
    post_likes = 0
    is_liked_by_user = False
    for current_post in posts:
        post_likes = current_post.like_set.count()

        if request.user.is_authenticated:
            try:
                Like.objects.get(user=request.user, post=current_post)
                is_liked_by_user = True
            except Like.DoesNotExist:
                is_liked_by_user = False
    return render(request, "network/index.html", {
        "posts": posts, "post_likes": post_likes, "is_liked_by_user": is_liked_by_user})


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, user_id):
    user = User.objects.get(id=user_id)
    followers = user.followers.all()
    following = user.following.all()
    posts = Post.objects.filter(user=user).order_by("-created_at")
    return render(request, "network/profile.html", {
        "user": user,
        "followers": followers,
        "following": following,
        "posts": posts,
    })


def post(request):
    if request.method == "POST":
        user = request.user
        content = request.POST["content"]
        new_post = Post(user=user, content=content)
        new_post.save()
        return HttpResponseRedirect(reverse("index"))


def like(request, post_id):
    if request.method == "POST":
        new_post = Post.objects.get(id=post_id)
        user = request.user
        try:
            user_like = Like.objects.get(user=user, post=new_post)
            user_like.delete()

            return JsonResponse({
                'likes': new_post.like_set.count(),
                'is_liked_by_user': False
            })
        except Like.DoesNotExist:
            user_like = Like(user=user, post=new_post)
            user_like.save()
            return JsonResponse({
                'likes': new_post.like_set.count(),
                'is_liked_by_user': True
            })


def edit(request, post_id):
    if request.method == "PUT":
        post = Post.objects.get(id=post_id)
        post.content = request.POST["content"]
        post.save()
        return HttpResponseRedirect(reverse("index"))