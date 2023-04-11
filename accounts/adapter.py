from allauth.account.adapter import DefaultAccountAdapter

from .models import *
#
#class AccountAdapter(DefaultAccountAdapter):
#    def save_user(self, request, user, form, commit=True):
#        """
#        This is called when saving user via allauth registration.
#        We override this to set additional data on user object.
#        """
#        #オーバーライド前の状態で内容を保持するためcommit=Falseにしておく
#        #その後、追加する項目を保存
#        user = super(AccountAdapter, self).save_user(request, user, form, commit=False)
#
#        user.userType = UserType(request.POST['userType'])
#
#        if not user.userType:
#            user.userType = UserType(USERTYPE_DEFAULT) #デフォルト(member)のユーザー種別##設定
#
#        #ユーザーIDを取得するために一旦保存
#        user.save()
#
#        if int(user.userType.id) == USERTYPE_STAFF:
#            #STAFFユーザー
#            staff_user = StaffUser()
#            staff_user.user_id = user.id
#            staff_user.save()
#
#        else:
#            #それ以外はmemberユーザー
#            user.userType = UserType(USERTYPE_MEMBER)
#            member = MemberUser()
#            member.user_id = user.id
#            member.save()

class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        #オーバーライド前の状態で内容を保持するためcommit=Falseにしておく
        #その後、追加する項目を保存
        user = super(AccountAdapter, self).save_user(request, user, form, commit=False)
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.nickname = form.cleaned_data.get('nickname')
        user.save()