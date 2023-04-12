from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView

from .models import Group, Event, ApprovedMember, ApprovedStaff, ApplyingMember, ApplyingStaff
from .forms import EventForm, GroupForm
from accounts.models import CustomUser
from django.urls import reverse_lazy
from django.http import HttpResponse,HttpResponseRedirect
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
from django.contrib import messages
from django.db import transaction

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
        for g in group_data:
            print(g.group_owner.nickname)
        user_data = CustomUser.objects.get(email=self.request.user)
        member_data = ApprovedMember.objects.filter(member=request.user, 
            group__in = group_data, approved = True)#memberデータ取得
        
        approvedmember_grouplist=[]
        for m_data in member_data:
            print(m_data.member,m_data.group, m_data.approved)
            approvedmember_grouplist.append(m_data.group.group_name)

        print("*****")
        applyingmember_grouplist=[]
        for apl_m_data in ApplyingMember.objects.filter(member=request.user,group__in=group_data, applying=True):
            print(apl_m_data.member,apl_m_data.group, apl_m_data.applying)
            applyingmember_grouplist.append(apl_m_data.group.group_name)

        return render(request, 'reservation/group_index.html',{
            'group_data': group_data,
            'user_data': user_data,
            'approvedmember_grouplist': approvedmember_grouplist,
            'applyingmember_grouplist': applyingmember_grouplist,

        })


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
class GroupDetailView(DetailView):

    model=Group
    template_name = 'reservation/group_detail.html'

    def get(self, request, *args, **kwargs):
        print("getメソッド")
        group_data = Group.objects.get(id=self.kwargs['pk'])
        event_data = Event.objects.filter(group=group_data)
        member_data = ApprovedMember.objects.filter( #memberデータ取得
            group = group_data, approved = True)

        staff_data = ApprovedStaff.objects.filter( #staffデータ取得
            group = group_data, approved = True)

        applying_staffs=ApplyingStaff.objects.filter(group=group_data, applying=True)
        applying_members=ApplyingMember.objects.filter(group=group_data, applying=True)


        member_names = {m_data.member for m_data in member_data}
        print("member_names:",member_names)
        staff_names = {s_data.staff for s_data in staff_data}
        """グループ加入の承認済みデータのリストに名前があり、かつapprovedでないと別ページにリダイレクトされる"""
        is_group_staff = self.request.user in staff_names
   
        ctx={
                'group_data':group_data,
                'member_data':member_data,
                'member_names':member_names,
                'staff_names':staff_names,
                'event_data':event_data,
                'is_group_staff':is_group_staff,
                'applying_staffs':applying_staffs,
                'applying_members':applying_members,

            }

        if (request.user in staff_names) or  (request.user in member_names):
            return render(request, 'reservation/group_detail.html', ctx)
        else:
            return HttpResponse('<h1>%sさんは%sの詳細は見られません</h1>' % (request.user.nickname, group_data.group_name ))

    def get_object(self):
        return get_object_or_404(Group, pk=self.kwargs.get('pk'))
    

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        pk= group.pk

        print(request.POST)
        if 'applying_staff' in request.POST:#スタッフの加入許可の処理
            applying_staff_pks = request.POST.getlist('applying_staff')
            # print(applying_staff_pks, applying_member_pks)

            if not applying_staff_pks:
                messages.error(request, '選択されたスタッフが存在しません。')
                return redirect('group_detail', pk=pk)
            
            # print(applying_staff_pks)
            applying_staff = ApplyingStaff.objects.filter(pk__in=applying_staff_pks, group=group, applying=True)

            # print("applying_staff****")
            # for s in applying_staff:
            #     print(s)

            if applying_staff.count() != len(applying_staff_pks):
                messages.error(request, '不正なスタッフが含まれています。')
                return redirect('group_detail', pk=pk)
            else:
                print("applying_staff count ok")
            
            staff_pks = applying_staff.values_list('staff', flat=True)

            # print("staff_pks:", staff_pks)
            # if 'applying_staff' in request.POST:
            print('applying_staff')
            try:
                with transaction.atomic():
                    
                    # ApprovedStaffを更新/作成
                    approved_staff_list = []#一括で登録処理するためにリストを準備
                    for staff_pk in staff_pks:
                        approved_staff, created = ApprovedStaff.objects.get_or_create(staff_id=staff_pk, group=group)#ApprovedStaffに申請許可するユーザーがいるか確認、いなければ作成
                        approved_staff.approved = True
                        approved_staff_list.append(approved_staff)

                    ApprovedStaff.objects.bulk_update(approved_staff_list, ['approved'])#一括で登録処理
    
                    applying_staff.delete()#加入申請のデータを削除

                messages.success(request, 'スタッフを承認しました。')
            except Exception as e:
                messages.error(request, 'スタッフの承認に失敗しました。')
                print(e)

            return HttpResponseRedirect( reverse_lazy('group_detail', kwargs={'pk':pk}))

            return redirect('group_detail', pk=pk)
        
        elif 'applying_member' in request.POST:#メンバーの加入許可の処理
            applying_member_pks = request.POST.getlist('applying_member')

            if not applying_member_pks:
                messages.error(request, '選択されたメンバーが存在しません。')
                return redirect('group_detail', pk=pk)
            
            # print(applying_member_pks)
            applying_member = ApplyingMember.objects.filter(pk__in=applying_member_pks, group=group, applying=True)

            # print("applying_member****")
            # for s in applying_member:
            #     print(s)

            if applying_member.count() != len(applying_member_pks):
                messages.error(request, '不正なメンバーが含まれています。')
                return redirect('group_detail', pk=pk)
            else:
                print("applying_member count ok")


            member_pks = applying_member.values_list('member', flat=True)

            print('applying_member')
            try:
                with transaction.atomic():
                    
                    # ApprovedMemberを更新/作成
                    approved_member_list = []
                    for member_pk in member_pks:
                        approved_member, created = ApprovedMember.objects.get_or_create(member_id=member_pk, group=group)
                        approved_member.approved = True
                        approved_member_list.append(approved_member)

                    ApprovedMember.objects.bulk_update(approved_member_list, ['approved'])

                    applying_member.delete()

                messages.success(request, 'スタッフを承認しました。')
            except Exception as e:
                messages.error(request, 'スタッフの承認に失敗しました。')
                print(e)

            return HttpResponseRedirect( reverse_lazy('group_detail', kwargs={'pk':pk}))

            return redirect('group_detail', pk=pk)
        
#グループ詳細
# from django.views.generic.detail import DetailView

# class GroupDetailView(DetailView):
#     model = Group
#     template_name = 'reservation/group_detail.html'
#     context_object_name = 'group_data'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         group_data = context['group_data']
#         event_data = Event.objects.filter(group=group_data)

#         member_data = group_data.approvedmember_set.filter(approved=True)
#         staff_data = group_data.approvedstaff_set.filter(approved=True)

#         member_names = {m.member for m in member_data}
#         staff_names = {s.staff for s in staff_data}

#         context['event_data'] = event_data
#         context['member_data'] = member_data
#         context['member_names'] = member_names
#         context['staff_names'] = staff_names
#         context['is_group_staff'] = self.request.user in staff_names

#         if self.request.user not in staff_names and self.request.user not in member_names:
#             context['error_message'] = f'{self.request.user.nickname}さんは{group_data.group_name}の詳細を閲覧できません。'

#         return context


#カレンダーと全てのイベントを表示(使用しない)
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
    
#イベント削除
class EventDeleteView(View):

    def get(self, request, *args, **kwargs):
        event_data = Event.objects.get(id=self.kwargs['pk'])
        return render(request, 'reservation/event_delete.html',{
            'event_data': event_data
        })

    def post(self, request, *args, **kwargs):
        event_data = Event.objects.get(id=self.kwargs['pk'])
        pk = event_data.group.pk
        print(pk)
        event_data.delete()
        #削除したイベントのグループページに遷移
        return HttpResponseRedirect( reverse_lazy('group_detail', kwargs={'pk':pk}))

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

class GroupJoinView(View):
    model=Group
    def get(self, request, *args, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        return render(request, 'reservation/group_join.html',{
            'group_data': group_data
        })

    def post(self, request, *args, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        user_data = CustomUser.objects.get(email=self.request.user)
        user_data.applyingmember_set.create(member=self.request.user, group=group_data, applying=True)
        pk=user_data.pk
        print(pk)
        #グループページに遷移
        # return HttpResponseRedirect( reverse_lazy('group'))
        return HttpResponseRedirect( reverse_lazy('userprofile', kwargs={'pk':pk}))




