from django import forms
from .models import Review, Profile
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User

# class ReviewForm(forms.ModelForm):
#     class Meta:
#         model = Review
#         fields = ['service', 'topic', 'text', 'is_anonymous', 'rating']
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['service', 'topic', 'text', 'is_anonymous', 'rating', 'image', 'video']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class PasswordChangingForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')