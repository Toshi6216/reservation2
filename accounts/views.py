from django.shortcuts import render, redirect
from django.views import View
from allauth.account import views  
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from reservation.models import *
from django.http import HttpResponse

from accounts.models import CustomUser
from .forms import ProfileForm

#user確認用view
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # 今ログインしてるユーザーのpkと、そのユーザー情報ページのpkが同じか、又はスーパーユーザーなら許可
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser

#Profile内容確認用view
class ProfileView(OnlyYouMixin, DetailView):
    model = CustomUser
    template_name = 'account/profile.html'

    def get(self, request, *args, **kwargs):
        user_data = CustomUser.objects.get(email=self.request.user)
        group_data_m = ApprovedMember.objects.filter(member=user_data, approved=True)
        group_data_s = ApprovedStaff.objects.filter(staff=user_data, approved=True)
        # print(user_data.applyingmember_set.all())
        applyings_m = user_data.applyingmember_set.all()
        for applying_m in applyings_m:
            print(applying_m.group)
        return render(request, self.template_name,{
            'group_data_m':group_data_m,
            'group_data_s':group_data_s,
            'user_data':user_data,
        })


class ProfileEditView(OnlyYouMixin, UpdateView):
    model = CustomUser
    template_name = 'account/profile_form.html'
    form_class = ProfileForm
    
    def get_success_url(self):
        return reverse("profile", kwargs={"pk": self.kwargs["pk"]})

