from django import forms
from .models import Post
import re
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

# ---------- POST FORM ----------

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Post title",
                "class": "form-control"
            }),
            "content": forms.Textarea(attrs={
                "placeholder": "Write your post here...",
                "rows": 5,
                "class": "form-control"
            }),
        }

