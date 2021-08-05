from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MyUser
class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ['username','email','password','phn_num','locality','is_tutor','is_student']

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = ['username','email','password','phn_num','locality','is_tutor','is_student']