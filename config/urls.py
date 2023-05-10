
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservation.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include("allauth.urls")),
    path('cldr/', include('sch_calendar.urls')),
    path('fcal/', include('full_calendar.urls')),

]
