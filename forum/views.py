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
from .forms import PostForm
from .forms import PostForm
from django.core.mail import send_mail

security_logger = logging.getLogger("security")

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        # Basic validation
        if len(username) < 3 or len(username) > 30:
            messages.error(request, "Username must be 3–30 characters long.")
            return render(request, "register.html", {"username": username, "email": email})

        if not username or not email or not password1 or not password2:
            messages.error(request, "Please provide username, email, and both password fields.")
            return render(request, "register.html", {"username": username, "email": email})

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html", {"username": username, "email": email})

        # Uniqueness checks
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username already exists.")
            return render(request, "register.html", {"username": username, "email": email})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "register.html", {"username": username, "email": email})


        # Password policy (Django + your custom validator)
        try:
            validate_password(password1)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, "register.html", {"username": username, "email": email})

        # Create user (login stays by username; email is required for registration)
        User.objects.create_user(username=username, email=email, password=password1)


        send_mail(
            subject="Welcome to Secure Forum",
            message=(
                f"Hello {username},\n\n"
                "Your account has been successfully created on Secure Forum.\n"
                "You can now log in.\n\n"
                "Regards,\n"
                "Secure Forum Team"
            ),
            from_email=None,  # uses DEFAULT_FROM_EMAIL from settings
            recipient_list=[email],
            fail_silently=False,
        )


        security_logger.info(
            "USER_REGISTER username=%s email=%s ip=%s ua=%s",
            username,
            email,
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

@login_required
@require_http_methods(["GET", "POST"])
def create_post(request):
    if not request.user.is_authenticated:
        return redirect("login")

    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("home")

    return render(request, "create_post.html", {"form": form})

