from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Post

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        User.objects.create_user(username=username, password=password)
        return redirect('login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Post.objects.create(author=request.user, content=content)
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})
