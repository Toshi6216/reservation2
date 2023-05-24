from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser  
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        
        if not email:
            raise ValueError('emailアドレスを入力してください')
        
        user = self.model(
            email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email=None, password=None, **extra_fields):
        user = self.create_user(
            email,
            password=password,
            )

        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        user = self.create_user(
            email,
            password=password,
            )

        user.is_staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
        )
    
    first_name = models.CharField('名', max_length=150)
    last_name = models.CharField('姓', max_length=150)
    nickname = models.CharField('ニックネーム', max_length=150,  null=True, blank=True)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=False) #staffかどうか
    admin = models.BooleanField('admin', default=False) 

    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def __str__(self):             
        return self.email

    def has_perm(self, perm, obj=None):
        return self.admin

    def has_module_perms(self, app_label):
        return self.admin




    class Meta(AbstractBaseUser.Meta):
        db_table = 'custom_user'


class StaffUser(models.Model):
    user = models.OneToOneField(
        CustomUser,
        unique=True,
        db_index=True,
        related_name='staff_user',
        on_delete=models.CASCADE
    )


    def __str__(self):
        user = CustomUser.objects.get(pk=self.user_id)
        return f'{user.id} - {user.email} - {user.first_name} - {user.last_name} - {user.nickname} - {self.id}'
    #    return f'{user.id} - {user.email} - {user.nickname} - {self.id}'


class MemberUser(models.Model):
    user = models.OneToOneField(
        CustomUser,
        unique=True,
        db_index=True,
        related_name='member_user',
        on_delete=models.CASCADE
    )

    def __str__(self):
        user = CustomUser.objects.get(pk=self.user_id)
        return f'{user.id} - {user.email} - {user.first_name} - {user.last_name} - {user.nickname} - {self.id}'
    #    return f'{user.id} - {user.email} - {user.nickname} - {self.id}'

#*********************************************************************
#class UserType(models.Model):
#    """ユーザー種別"""
#    typename = models.CharField(
#        verbose_name = 'ユーザー種別', 
#        max_length = 150
#        )
#    
#    def __str__(self):
#        return f'{self.id} - {self.typename}'
#
#USERTYPE_STAFF = 100
#USERTYPE_MEMBER = 200
#USERTYPE_DEFAULT = USERTYPE_MEMBER #デフォルトはmember

#class UserManager(UserManager):
#
#    def _create_user(self, email, password, **extra_fields):
#        if not email:
#            raise ValueError('The given email must be set')
#        email = self.normalize_email(email)
#        user = self.model(email=email, **extra_fields)
#        user.set_password(password)
#        user.save(using=self._db)
#        return user
#
#    def create_user(self, email, password=None, **extra_fields):
#        extra_fields.setdefault('is_staff', False)
#        extra_fields.setdefault('is_superuser', False)
#        return self._create_user(email, password, **extra_fields)
#
#    def create_superuser(self, email, password, **extra_fields):
#        extra_fields.setdefault('is_staff', True)
#        extra_fields.setdefault('is_superuser', True)
#        if extra_fields.get('is_staff') is not True:
#            raise ValueError('Superuser must have is_staff=True.')
#        if extra_fields.get('is_superuser') is not True:
#            raise ValueError('Superuser must have is_superuser=True.')
#        return self._create_user(email, password, **extra_fields)


#class CustomUser(AbstractBaseUser):
#class CustomUser(AbstractBaseUser, PermissionsMixin):
#class CustomUser(AbstractUser):
#        
#    class Meta(object):
#    #    verbose_name = ('user')
#    #    verbose_name_plural = ('users')
#        db_table = 'custom_user'
#
#    objects = UserManager()
#
#    email = models.EmailField('メールアドレス', unique=True)
##    first_name = models.CharField('姓', max_length=150, null=False, blank=False)
##    last_name = models.CharField('名', max_length=150, null=False, blank=False)
#    nickname = models.CharField('ニックネーム', max_length=150,  null=True, blank=True)
#  #  event = models.ManyToManyField(Event, related_name='event', null=True, blank=True)
#  #  group = models.ManyToManyField(Group, related_name='group', null=True, blank=True)
#
#    """
#    追加したい項目を入れる
#    """
#
#
#    userType = models.ForeignKey(
#        UserType, 
#        verbose_name='ユーザー種別',
#        null=True,
#        blank=True,
#        on_delete=models.PROTECT
#    )
#
#
#    EMAIL_FIELD = 'email'
#    USERNAME_FIELD = 'email'
#    REQUIRED_FIELDS = []
#
#    
#
# #   def clean(self):
# #       super().clean()
# #       self.email = self.__class__.objects.normalize_email(self.email)
#
#    def __str__(self):
#        return self.email
