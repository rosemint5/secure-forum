from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Post
import logging

security_logger = logging.getLogger("security")

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if len(username) < 3 or len(username) > 30:
            messages.error(request, "Username must be 3–30 characters long.")
            return render(request, "register.html", {"username": username})


        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, "register.html", {"username": username})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Invalid credentials.")
            return render(request, "register.html", {"username": username})

        try:
            validate_password(password)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, "register.html", {"username": username})

        User.objects.create_user(username=username, password=password)

        security_logger.info(
            "USER_REGISTER username=%s ip=%s ua=%s",
            username,
            get_client_ip(request),
            request.META.get("HTTP_USER_AGENT", "-"),
        )

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

            security_logger.info(
                "LOGIN_SUCCESS username=%s ip=%s ua=%s",
                username,
                get_client_ip(request),
                request.META.get("HTTP_USER_AGENT", "-"),
            )

            return redirect("home")

        security_logger.warning(
            "LOGIN_FAIL username=%s ip=%s ua=%s",
            username,
            get_client_ip(request),
            request.META.get("HTTP_USER_AGENT", "-"),
        )

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@require_http_methods(["POST"])
def logout_view(request):
    security_logger.info(
        "LOGOUT username=%s ip=%s ua=%s",
        getattr(request.user, "username", "-"),
        get_client_ip(request),
        request.META.get("HTTP_USER_AGENT", "-"),
    )

    logout(request)
    return redirect("login")


@login_required
@require_http_methods(["GET", "POST"])
def home_view(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(author=request.user, content=content)

            security_logger.info(
                "POST_CREATE username=%s ip=%s",
                request.user.username,
                get_client_ip(request),
            )

            messages.success(request, "Post added successfully.")
        else:
            messages.error(request, "Post content cannot be empty.")

    posts = Post.objects.all().order_by("-created_at")
    return render(request, "home.html", {"posts": posts})


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
