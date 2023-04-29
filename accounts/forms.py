from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model

# from .models import CustomUser
CustomUser = get_user_model() #正式なユーザーデータ取得の仕方に変更

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("nickname", "first_name", "last_name")

#class UserCreationForm(forms.ModelForm):
#    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
#    password2 = forms.CharField(
#        label='Password confirmation', widget=forms.PasswordInput)
#
#    class Meta:
#        model = User
#        fields = ('email', 'date_of_birth')
#
#    def clean_password2(self):
#        password1 = self.cleaned_data.get("password1")
#        password2 = self.cleaned_data.get("password2")
#        if password1 and password2 and password1 != password2:
#            raise forms.ValidationError("Passwords don't match")
#        return password2
#
#    def save(self, commit=True):
#        user = super().save(commit=False)
#        user.set_password(self.cleaned_data["password1"])
#        if commit:
#            user.save()
#        return user

class SignupForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ['email','first_name', 'last_name', 'nickname']
        
   # def signup(self, request, user):
   #     user.first_name = self.cleaned_data['first_name']
   #     user.last_name = self.cleaned_data['last_name']
   #     user.save()
   #     return user

#    first_name = models.CharField('名', max_length=150)
#    last_name = models.CharField('姓', max_length=150)
#    nickname = models.CharField('ニックネーム', max_length=150,  null=True, blank=True)
#    active = models.BooleanField(default=True)
#    staff = models.BooleanField(default=False) #staffかどうか
#    admin = models.BooleanField(default=False) 