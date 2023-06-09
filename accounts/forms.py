from django.core.validators import validate_email
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from jsonschema import ValidationError
from .models import Profile


User = get_user_model()


class SignupForm(UserCreationForm):
    phone_or_email = forms.CharField(max_length=100, required=True)
    bio = forms.CharField(max_length=500, required=False)
    profile_img = forms.ImageField(required=False)
    location = forms.CharField(max_length=100, required=False)
    fullname = forms.CharField(max_length=100, required=True)
    email = None
    phone = None
    first_name = None
    last_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password2')

    class Meta:
        model = User
        fields = ('username', 'password1', 'email', 'first_name', 'last_name')

    # identify if phone number or email
    def clean_phone_or_email(self):
        phone_or_email = self.cleaned_data.get('phone_or_email')
        if not phone_or_email:
            raise forms.ValidationError('Phone or email is required')
        elif phone_or_email.isdigit():
            pattern = r'^\d{10}$'
            match = re.match(pattern, phone_or_email)
            if not match:
                raise forms.ValidationError('Invalid phone number')
            if Profile.objects.filter(phone=phone_or_email).exists():
                raise forms.ValidationError('Phone number already exists')
            self.phone = phone_or_email
        else:
            try:
                validate_email(phone_or_email)
                if User.objects.filter(email=phone_or_email).exists():
                    raise forms.ValidationError('Email address already exists')
                self.email = phone_or_email
            except ValidationError as e:
                print("\ninvalid", e.message)
                raise forms.ValidationError('Invalid email address')
        return phone_or_email

    # seperate first_name and last_name
    def clean_fullname(self):
        fullname = self.cleaned_data.get('fullname')
        if len(fullname) > 100:
            raise forms.ValidationError(
                'Full name must be less than 100 characters')
        if " " in fullname:
            self.first_name = fullname[:fullname.index(" ")]
            self.last_name = fullname[fullname.index(" ")+1:]
        else:
            self.first_name = fullname
            self.last_name = ""
        return fullname

    # saving user profile info
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.email:
            user.email = self.email
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.save()
        profile = Profile.objects.create(user=user)
        if self.phone:
            profile.phone = self.phone
        if self.cleaned_data.get('bio'):
            profile.bio = self.cleaned_data['bio']
        if self.cleaned_data.get('profile_img'):
            profile.profile_img = self.cleaned_data['profile_img']
        if self.cleaned_data.get('location'):
            profile.location = self.cleaned_data['location']
        try:
            profile.save()
        except Exception as e:
            user.delete()
            raise forms.ValidationError('Error saving profile : ' + str(e))
        return user
