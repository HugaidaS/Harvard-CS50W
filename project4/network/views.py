from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse
from .models import User, Post, Like


def index(request):
    posts = Post.objects.all().order_by("-created_at")
    posts_with_likes = get_posts_with_likes(posts, request)

    paginator = Paginator(posts_with_likes, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj
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
    followers_count = user.followers.count()
    following_count = user.following.count()
    followers = user.followers.all()
    following = user.following.all()

    # all users posts in chronological order
    posts = Post.objects.filter(user=user).order_by("-created_at")

    posts_with_likes = get_posts_with_likes(posts, request)

    paginator = Paginator(posts_with_likes, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "user": user,
        "followers_count": followers_count,
        "following_count": following_count,
        "followers": followers,
        "following": following,
        "page_obj": page_obj,
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
        try:
            new_post = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)

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
    if request.method == "POST":
        updated_post = Post.objects.get(id=post_id)
        new_content = request.POST.get("content", "")
        print(new_content)
        updated_post.content = new_content
        updated_post.save()
        return HttpResponseRedirect(reverse("index"))


def follow(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        current_user = request.user
        try:
            current_user.following.get(id=user_id)
            current_user.following.remove(user)

            return HttpResponseRedirect(reverse("profile", args=(user_id,)))
        except User.DoesNotExist:
            current_user.following.add(user)
            return HttpResponseRedirect(reverse("profile", args=(user_id,)))


def unfollow(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        current_user = request.user
        try:
            current_user.following.get(id=user_id)
            current_user.following.remove(user)

            return HttpResponseRedirect(reverse("profile", args=(user_id,)))
        except User.DoesNotExist:
            print("User does not exist")
            return HttpResponseRedirect(reverse("profile", args=(user_id,)))


def get_posts_with_likes(posts, request):
    posts_with_likes = []

    for current_post in posts:
        post_likes = current_post.like_set.count()
        is_liked_by_user = False

        if request.user.is_authenticated:
            is_liked_by_user = Like.objects.filter(user=request.user, post=current_post).exists()

        post_data = {
            "data": current_post,
            "likes": post_likes,
            "is_liked_by_user": is_liked_by_user
        }
        posts_with_likes.append(post_data)

    return posts_with_likes


def following(request):
    user = request.user
    following = user.following.all()
    posts = Post.objects.filter(user__in=following).order_by("-created_at")

    posts_with_likes = get_posts_with_likes(posts, request)

    paginator = Paginator(posts_with_likes, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })