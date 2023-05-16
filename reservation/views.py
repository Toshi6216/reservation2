from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView

from .models import Group, Event, ApprovedMember, ApprovedStaff, ApplyingMember, ApplyingStaff, Join
from .forms import EventForm, GroupForm, SearchForm
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
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail


# from dateutil.relativedelta import relativedelta 

#homeページ
class IndexView(TemplateView):
    template_name = 'reservation/index.html'
    
#イベント一覧
class EventView(LoginRequiredMixin,View):
    #このviewがコールされたら最初にget関数が呼ばれる
    def get(self, request, *args, **kwargs):
        event_data = Event.objects.order_by('-id') #新しいものから順番に並べる
        return render(request, 'reservation/event_index.html',{
            'event_data': event_data
        })
    

#グループ一覧
class GroupView(LoginRequiredMixin,View):
    #このviewがコールされたら最初にget関数が呼ばれる
    def get(self, request, *args, **kwargs):
        group_data = Group.objects.order_by('-id') #新しいものから順番に並べる
        # for g in group_data:
        #     print(g.group_owner.nickname)
        user_data = CustomUser.objects.get(email=self.request.user)
        member_data = ApprovedMember.objects.filter(
            member=request.user, 
            group__in = group_data, 
            approved = True)#memberデータ取得
        staff_data = ApprovedStaff.objects.filter(
            staff=request.user, 
            group__in = group_data, 
            approved = True)#staffデータ取得
        #グループ検索機能
        searchForm = SearchForm(self.request.GET)
        # print("searchForm:", searchForm)
        #seachForm変数に正常なデータがあれば
        if searchForm.is_valid():
            keyword = searchForm.cleaned_data['keyword'] #keyword変数にフォームのキーワードを代入
            group_data = Group.objects.filter(group_name__contains=keyword) #キーワードを含むレコードをfilterメソッドで抽出
        else:
            keyword = SearchForm()
            group_data = Group.objects.order_by('-id') #新しいものから順番に並べる
            # print("if else")

        
        approvedmember_grouplist=[]
        for m_data in member_data:
            # print(m_data.member,m_data.group, m_data.approved)
            approvedmember_grouplist.append(m_data.group.group_name)

        approvedstaff_grouplist=[]
        for s_data in staff_data:
            approvedstaff_grouplist.append(s_data.group.group_name)

        # print("*****")
        applyingmember_grouplist=[]
        for apl_m_data in ApplyingMember.objects.filter(member=request.user,group__in=group_data, applying=True):
            # print(apl_m_data.member,apl_m_data.group, apl_m_data.applying)
            applyingmember_grouplist.append(apl_m_data.group.group_name)

        return render(request, 'reservation/group_index.html',{
            'group_data': group_data,
            'user_data': user_data,
            'approvedmember_grouplist': approvedmember_grouplist,
            'approvedstaff_grouplist': approvedstaff_grouplist,
            'applyingmember_grouplist': applyingmember_grouplist,
            'searchForm': searchForm,

        })


#イベント編集
class EventEditView(LoginRequiredMixin,UpdateView):
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
class GroupEditView(LoginRequiredMixin,UpdateView):
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
class GroupDetailView(LoginRequiredMixin,DetailView):

    model=Group
    template_name = 'reservation/group_detail.html'

    def get(self, request, *args, **kwargs):
        # print("getメソッド")
        group_data = Group.objects.get(id=self.kwargs['pk'])
        event_data = Event.objects.filter(group=group_data)
        member_data = ApprovedMember.objects.filter( #memberデータ取得
            group = group_data, approved = True)

        staff_data = ApprovedStaff.objects.filter( #staffデータ取得
            group = group_data, approved = True)

        applying_staffs=ApplyingStaff.objects.filter(group=group_data, applying=True)
        applying_members=ApplyingMember.objects.filter(group=group_data, applying=True)


        member_names = {m_data.member for m_data in member_data}
        # print("member_names:",member_names)
        staff_names = {s_data.staff for s_data in staff_data}
        """グループ加入の承認済みデータのリストに名前があり、かつapprovedでないと別ページにリダイレクトされる"""
        is_group_staff = self.request.user in staff_names
        is_group_member = self.request.user in member_names

        join_event_list=[]
        join_event=Join.objects.filter(join_name=self.request.user, join=True)
        for j_ev in join_event:
            join_event_list.append(j_ev.join_event.pk)
        # print(join_event_list)
   
        ctx={
                'group_data':group_data,
                'member_data':member_data,
                'member_names':member_names,
                'staff_names':staff_names,
                'event_data':event_data,
                'is_group_staff':is_group_staff,
                'is_group_member':is_group_member,
                'applying_staffs':applying_staffs,
                'applying_members':applying_members,
                'join_event_list': join_event_list,

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

        # print(request.POST)
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
            # print('applying_staff')
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

            # return redirect('group_detail', pk=pk)
        
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

class LoginMixinTemplateView(LoginRequiredMixin, generic.TemplateView):
    pass

#カレンダーと全てのイベントを表示(使用しない)
class EventCalView(mixins.MonthCalendarMixin, LoginMixinTemplateView):
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
class GpEventCalView(mixins.MonthCalendarMixin, LoginMixinTemplateView):
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
        # print(approved_check_s)

        return context
    
class LoginMixinDetailView(LoginRequiredMixin, DetailView):
    pass

from django.db.models import Q
#カレンダーと所属しているグループのイベントを表示
class GroupDetailCalView(mixins.MonthCalendarMixin, LoginMixinDetailView):
    template_name = 'reservation/group_detail_cal.html'
    model = Group
    def get(self, request, *args, **kwargs):
        # print("getメソッド")
        self.object=self.get_object()
        context = self.get_context_data(object=self.object)
        group_data = Group.objects.get(id=self.kwargs['pk'])
        event_data = Event.objects.filter(group=group_data).order_by('event_date')
        member_data = ApprovedMember.objects.filter( #memberデータ取得
            group = group_data, approved = True)

        staff_data = ApprovedStaff.objects.filter( #staffデータ取得
            group = group_data, approved = True)

        applying_staffs=ApplyingStaff.objects.filter(group=group_data, applying=True)
        applying_members=ApplyingMember.objects.filter(group=group_data, applying=True)


        member_names = {m_data.member for m_data in member_data}
        # print("member_names:",member_names)
        staff_names = {s_data.staff for s_data in staff_data}
        """グループ加入の承認済みデータのリストに名前があり、かつapprovedでないと別ページにリダイレクトされる"""
        is_group_staff = self.request.user in staff_names
        is_group_member = self.request.user in member_names

        context['group_data'] = group_data
        context['member_data']=member_data
        context['member_names']=member_names
        context['staff_names']=staff_names
        context['event_data']=event_data
        context['is_group_staff']=is_group_staff
        context['is_group_member']=is_group_member
        context['applying_staffs']=applying_staffs
        context['applying_members']=applying_members

        # if (request.user in staff_names) or  (request.user in member_names):
        if is_group_member or is_group_staff :

            return  self.render_to_response(context)

        else:
            return HttpResponse('<h1>%sさんは%sの詳細は見られません</h1>' % (request.user.nickname, group_data.group_name ))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        pk=self.object.pk

        approved_check_m = ApprovedMember.objects.filter(member=self.request.user, approved = True)
        approved_check_s = ApprovedStaff.objects.filter(staff=self.request.user, approved = True)

        chk_m=[ap_chk_m.group for ap_chk_m in approved_check_m]
        chk_s=[ap_chk_s.group for ap_chk_s in approved_check_s]
        
        event_data = Event.objects.filter(group=pk).order_by('event_date')#指定グループのイベントでフィルター
        days={event_days.event_date for event_days in event_data }

        group_data = Group.objects.get(id=self.kwargs['pk'])

        context.update(calendar_context)
        context['event_data'] = event_data #イベントのデータをコンテキストで渡す
        context['days'] = days
        context['approved_check_s'] = approved_check_s
        # print(approved_check_s)
        context['group_data']=group_data

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
        # print(group_data)
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

class LoginMixinView(LoginRequiredMixin, View):
    pass

#イベント削除
class EventDeleteView(LoginMixinView):

    def get(self, request, *args, **kwargs):
        event_data = Event.objects.get(id=self.kwargs['pk'])

        # print(event_data.group.id)
        group_data = Group.objects.get(id=event_data.group.id)
        print(group_data)

        staff_data = ApprovedStaff.objects.filter(
            group = group_data, approved=True)

        names = [data.staff for data in staff_data] 
        #スタッフユーザーで無ければHTMLを返す　遷移させる
        if not request.user in names:
            return HttpResponse('<h1>%sさんは%sの編集権限がありません</h1>' % (request.user.nickname, group_data.group_name ))

        return render(request, 'reservation/event_delete.html',{
            'event_data': event_data
        })

    def post(self, request, *args, **kwargs):
        event_data = Event.objects.get(id=self.kwargs['pk'])
        pk = event_data.group.pk
        # print(pk)
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
   

#イベント詳細
class EventDetailView(DetailView):
    template_name = 'reservation/event_detail.html'
    def get(self, request, *args, **kwargs):
        event = Event.objects.get(id=self.kwargs['pk'])
        
        is_join=False
        for join_event in event.join_set.all():
            # print(join_event.join_name)
            if self.request.user==join_event.join_name:
                is_join=True
       
        return render(request, self.template_name,{
            'event': event,
            'is_join': is_join,
        })

class GroupJoinView(LoginMixinView): #メンバー申請
    model=Group
    def get(self, request, *args, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        return render(request, 'reservation/group_join.html',{
            'group_data': group_data,
            'staff_or_member':'メンバー',
        })

    def post(self, request, *args, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        user_data = CustomUser.objects.get(email=self.request.user)
        # print(pk)
        #グループページに遷移
        # return HttpResponseRedirect( reverse_lazy('group'))

        #メール送信用データ生成######
        subject = "グループ加入申請(member)"
        message = "「{}」に、".format(group_data.group_name) + "{0}({1})がメンバー申請しました。\n".format(user_data, user_data.nickname) + settings.FRONTEND_URL + "group_detail/{}/".format(group_data.pk) 

        sender = settings.EMAIL_HOST_USER

        group_staff_query = group_data.approvedstaff_set.all()
        # print("group_staff_query:", group_staff_query)
        recipients = []
        for gp in group_staff_query:
            group_send_to = gp.staff.email
            recipients.append(group_send_to)
        # send_mail(subject, message, sender, recipients) #通知メール送信
        # print("send_mail:", subject, message, sender, recipients)
        #メール送信用データ生成(ここまで)######
        try:
            send_mail(subject, message, sender, recipients) #通知メール送信
            # print("send_mail:", subject, message, sender, recipients)
            
        except BadHeaderError:
            return HttpResponse('無効なヘッダーが見つかりました。')
       
        user_data.applyingmember_set.create(member=self.request.user, group=group_data, applying=True)
        pk=user_data.pk
        
    
        return HttpResponseRedirect( reverse_lazy('userprofile', kwargs={'pk':pk}))

class GroupJoinStaffView(LoginMixinView): #スタッフ申請
    model=Group
    def get(self, request, *args, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        return render(request, 'reservation/group_join.html',{
            'group_data': group_data,
            'staff_or_member':'スタッフ',
        })

    def post(self, request, *args, **kwargs):
        group_data = Group.objects.get(id=self.kwargs['pk'])
        user_data = CustomUser.objects.get(email=self.request.user)

        #メール送信用データ生成######
        subject = "グループ加入申請(staff)"
        message = "「{}」に、".format(group_data.group_name) + "{0}({1})がスタッフ申請しました。\n".format(user_data, user_data.nickname) + settings.FRONTEND_URL + "group_detail/{}/".format(group_data.pk) 

        sender = settings.EMAIL_HOST_USER

        group_staff_query = group_data.approvedstaff_set.all()
        # print("group_staff_query:", group_staff_query)
        recipients = []
        for gp in group_staff_query:
            group_send_to = gp.staff.email
            recipients.append(group_send_to)
        # send_mail(subject, message, sender, recipients) #通知メール送信
        # print("send_mail:", subject, message, sender, recipients)
        #メール送信用データ生成(ここまで)######
        try:
            send_mail(subject, message, sender, recipients) #通知メール送信
            # print("send_mail:", subject, message, sender, recipients)
            
        except BadHeaderError:
            return HttpResponse('無効なヘッダーが見つかりました。')

        user_data.applyingstaff_set.create(staff=self.request.user, group=group_data, applying=True)
        pk=user_data.pk

        return HttpResponseRedirect( reverse_lazy('userprofile', kwargs={'pk':pk}))

class EventJoinView(LoginMixinView): #イベント予約
    model=Event
    def get(self, request, *args, **kwargs):
        event = Event.objects.get(id=self.kwargs['pk'])
        group_data = Group.objects.get(id=event.group.id)

        staff_data = ApprovedStaff.objects.filter(
            group = group_data, approved=True)

        names = [data.staff for data in staff_data] 
        #スタッフユーザーで無ければHTMLを返す　遷移させる
        if not request.user in names:
            return HttpResponse('<h1>%sさんは%sの編集権限がありません</h1>' % (request.user.nickname, group_data.group_name ))
        
        return render(request, 'reservation/event_join.html',{
            'event': event,
            
        })

    def post(self, request, *args, **kwargs):
        event = Event.objects.get(id=self.kwargs['pk'])
        user_data = CustomUser.objects.get(email=self.request.user)
        user_data.join_set.create(join_name=self.request.user, join_event=event, join=True)
        # pk=user_data.pk
        pk=event.group.pk
        # print(pk)
        
        # return HttpResponseRedirect( reverse_lazy('userprofile', kwargs={'pk':pk}))
        return HttpResponseRedirect( reverse_lazy('group_detail', kwargs={'pk':pk}))
 

#以下お試し
from .forms import ContactForm # 追加

""" お問い合わせフォーム画面"""
def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = settings.EMAIL_HOST_USER
            send_to = form.cleaned_data['send_to']
            myself = form.cleaned_data['myself']
            recipients = []
            recipients.append(send_to)
           
            if myself:
                recipients.append(sender)
            try:
                send_mail(subject, message, sender, recipients)
                print("send_mail:", subject, message, sender, recipients)
                
                
            except BadHeaderError:
                return HttpResponse('無効なヘッダーが見つかりました。')
            return redirect('complete')

    else:
        form = ContactForm()
    return render(request, 'contact/contact_form.html', {'form': form})


""" 送信完了画面"""
def complete(request):
    return render(request, 'contact/complete.html')