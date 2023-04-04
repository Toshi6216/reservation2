from django.shortcuts import render
from django.views.generic import TemplateView, View, UpdateView, CreateView
from .models import Group, Event, ApprovedMember, ApprovedStaff, ApplyingMember, ApplyingStaff
from .forms import EventForm, GroupForm
from accounts.models import CustomUser
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
import time
import json
from django.middleware.csrf import get_token
from django.views import generic
from . import mixins
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.signals import post_save 
from django.dispatch import receiver
from django.urls import reverse
from django.core.exceptions import ValidationError

# from dateutil.relativedelta import relativedelta 

#homeページ
class IndexView(TemplateView):
    template_name = 'reservation/index.html'
    
#イベント一覧
class EventView(View):
    #このviewがコールされたら最初にget関数が呼ばれる
    def get(self, request, *args, **kwargs):
        event_data = Event.objects.order_by('-id') #新しいものから順番に並べる
        return render(request, 'reservation/event_index.html',{
            'event_data': event_data
        })
                # 'is_group_staff':is_group_staff
    

#グループ一覧
class GroupView(View):
    #このviewがコールされたら最初にget関数が呼ばれる
    def get(self, request, *args, **kwargs):
        group_data = Group.objects.order_by('-id') #新しいものから順番に並べる
        # approved_check_m = ApprovedMember.objects.filter(member=self.request.user, approved = True)
        # approved_check_s = ApprovedStaff.objects.filter(staff=self.request.user, approved = True)

        user_data = CustomUser.objects.get(email=self.request.user)
        # for group in approved_check_m:
        #     print(group.group, group.approved)
            # print(group.approved)
            # print(ap_chk_m.)

        return render(request, 'reservation/group_index.html',{
            'group_data': group_data,
            # 'approved_check_m': approved_check_m,
            # 'approved_check_s': approved_check_s,

            'user_data': user_data,
        })

    # def get(self, request, *args, **kwargs):
    #     # group_data = Group.objects.order_by('-id') #新しいものから順番に並べる
    #     approved_check_m = ApprovedMember.objects.filter(member=self.request.user, approved = True)
    #     approved_check_s = ApprovedStaff.objects.filter(staff=self.request.user, approved = True)
    #     print(approved_check_m)
    #     print(approved_check_s)
    #     chk_m=[ap_chk_m.group for ap_chk_m in approved_check_m]
    #     chk_s=[ap_chk_s.group for ap_chk_s in approved_check_s]
    #     print(chk_m)
    #     print(chk_s)
    #     group_data = Group.objects.filter(Q(group_name__in=chk_m)|Q(group_name__in=chk_s))
    #     print(group_data)
    #     return render(request, 'reservation/group_index.html',{
    #         'group_data': group_data

    #     })

#イベント編集
class EventEditView(UpdateView):
    model = Event
    template_name = 'reservation/event_form.html'
    form_class = EventForm
    success_url = reverse_lazy('group_detail')

    def get(self, request, **kwargs):
        event_data = Event.objects.get(id=self.kwargs['pk'])
        staff_data = ApprovedStaff.objects.filter(
            group = event_data.group, approved=True)

        names = [data.staff for data in staff_data] 
        #スタッフユーザーで無ければHTMLを返す　遷移させる
        if not request.user in names:
            return HttpResponse('<h1>%sさんは%sの編集権限がありません</h1>' % (request.user.nickname, event_data.group ))
        return super().get(request)
    
    def get_success_url(self):
        pk = self.object.group.pk
        return reverse('group_detail', kwargs={'pk':pk})


#グループ内容編集
class GroupEditView(UpdateView):
    model = Group
    template_name = 'reservation/group_form.html'
    form_class = GroupForm
    success_url = reverse_lazy('group')

    def get(self, request, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        staff_data = ApprovedStaff.objects.filter(
            group = group_data, approved = True)

        names = [data.staff for data in staff_data] 
        #スタッフユーザーで無ければHTMLを返す　遷移させる
        if not request.user in names:
            return HttpResponse('<h1>%sさんは%sの編集権限がありません</h1>' % (request.user.nickname, group_data.group_name ))
        return super().get(request)

#グループ詳細
class GroupDetailView(View):
    def get(self, request, *args, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        event_data = Event.objects.filter(group=group_data)
        member_data = ApprovedMember.objects.filter( #memberデータ取得
            group = group_data, approved = True)
        print("--member--")
        for n in member_data:
            print(n.member)
        print("------")
        staff_data = ApprovedStaff.objects.filter( #staffデータ取得
            group = group_data, approved = True)
        print("--staff--")
        for n in staff_data:
            print(n.staff)
        print("-------")

        member_names = {m_data.member for m_data in member_data}
        staff_names = {s_data.staff for s_data in staff_data}
        """グループ加入の承認済みデータのリストに名前があり、かつapprovedでないと別ページにリダイレクトされる"""
        is_group_staff = self.request.user in staff_names
        print("is_group_staff:",is_group_staff)
        print(f"member_names:{member_names}")
        print(request.user in member_names)
        print(f"staff_names:{staff_names}")
        print(request.user in staff_names)

        if (request.user in staff_names) or  (request.user in member_names):
            return render(request, 'reservation/group_detail.html',{
                'group_data':group_data,
                'member_data':member_data,
                'member_names':member_names,
                'staff_names':staff_names,
                'event_data':event_data,
                'is_group_staff':is_group_staff
            })
        else:
            return HttpResponse('<h1>%sさんは%sの詳細は見られません</h1>' % (request.user.nickname, group_data.group_name ))


#カレンダーと全てのイベントを表示
class EventCalView(mixins.MonthCalendarMixin, generic.TemplateView):
    template_name = 'reservation/event_cal.html'
    model = Event
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        event_data = Event.objects.order_by('-id') #イベントのデータを読み出し
        context.update(calendar_context)
        context['event_data'] = event_data #イベントのデータをコンテキストで渡す
        
        return context

from django.db.models import Q
#カレンダーと所属しているグループのイベントを表示
class GpEventCalView(mixins.MonthCalendarMixin, generic.TemplateView):
    template_name = 'reservation/group_event_cal.html'
    model = Event
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()

        approved_check_m = ApprovedMember.objects.filter(member=self.request.user, approved = True)
        approved_check_s = ApprovedStaff.objects.filter(staff=self.request.user, approved = True)

        chk_m=[ap_chk_m.group for ap_chk_m in approved_check_m]
        chk_s=[ap_chk_s.group for ap_chk_s in approved_check_s]
        
        event_data = Event.objects.filter(Q(group__in=chk_m)|Q(group__in=chk_s)).order_by('event_date')#所属しているグループのイベントでフィルター
        days={event_days.event_date for event_days in event_data }

        context.update(calendar_context)
        context['event_data'] = event_data #イベントのデータをコンテキストで渡す
        context['days'] = days
        context['approved_check_s'] = approved_check_s
        print(approved_check_s)

        return context
    
#イベント登録
class EventCreateView(LoginRequiredMixin, CreateView):
    #グループに所属していないとイベントは作れない
    model = Event
    template_name = 'reservation/event_form.html'
    form_class = EventForm
    success_url = reverse_lazy('group_detail')


    def get(self, request, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        print(group_data)
        staff_data = ApprovedStaff.objects.filter(
            group = group_data, approved=True)

        names = [data.staff for data in staff_data] 
        #スタッフユーザーで無ければHTMLを返す　遷移させる
        if not request.user in names:
            return HttpResponse('<h1>%sさんは%sの編集権限がありません</h1>' % (request.user.nickname, group_data.group_name ))
        return super().get(request)
    
    def get_success_url(self):
        pk = self.object.group.pk
        return reverse('group_detail', kwargs={'pk':pk})
    
    def form_valid(self, form):
        start_time = form.cleaned_data["start_time"]
        end_time = form.cleaned_data["end_time"]
        if start_time and end_time and start_time >= end_time: #開始時刻と終了時刻のバリデーション
            form.add_error('start_time', "開始時刻と終了時刻を確認してください")
            return self.form_invalid(form)
        obj = form.save(commit=False)
        obj.group = Group.objects.get(id=self.kwargs['pk'])
        
        obj.save()
        return super().form_valid(form)
    

#グループ登録
class GroupCreateView(LoginRequiredMixin, CreateView):
    #誰でもグループを作れる
    #グループを作った本人は自動的にstaff権限付与

    model = Group
    template_name = 'reservation/group_form.html'
    form_class = GroupForm
    success_url = reverse_lazy('group')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.group_owner = self.request.user
        obj.save()
        return super().form_valid(form)
    
@receiver(post_save, sender=Group) #グループ登録時、同時にApprovedStaffにも登録される
def groupSignal(sender, instance, created, **kwargs):
    if created:
        user = instance.group_owner
        ApprovedStaff.objects.create(staff=user, group=instance, approved=True)
   


#１つのグループが行うイベントカレンダー イベント参加ボタン
class GroupCalendar(GpEventCalView):
    pass

#イベント詳細
class EventDetailView():
    pass