from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'regno', 'location', 'college', 'city', 'email', 'mobile']

#manully added 
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    designation = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=15)
    sex = forms.ChoiceField(choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    aadhar_no = forms.CharField(max_length=12)
    age = forms.IntegerField(min_value=1)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "designation", "company_name", "mobile", "email", "sex", "aadhar_no", "age", "password1", "password2"]

    def clean_username(self):
        # Allow any username, skip built-in validators
        return self.cleaned_data.get('username')