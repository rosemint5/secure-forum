from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Post


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, "register.html", {"username": username})

        if User.objects.filter(username=username).exists():
            messages.error(request, "This username already exists.")
            return render(request, "register.html", {"username": username})

        try:
            validate_password(password)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, "register.html", {"username": username})

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("login")

    return render(request, "register.html")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
@require_http_methods(["GET", "POST"])
def home_view(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(author=request.user, content=content)
            messages.success(request, "Post added successfully.")
        else:
            messages.error(request, "Post content cannot be empty.")
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "home.html", {"posts": posts})

