from django.urls import path
from reservation import views


urlpatterns = [
    path('',views.IndexView.as_view(), name="home"), #top画面
    path('event/',views.EventView.as_view(), name="event"), #イベント一覧
    path('group/',views.GroupView.as_view(), name="group"), #グループ一覧
    path('event_edit/<int:pk>/',views.EventEditView.as_view(), name="event_edit"), #イベント編集
    path('event_delete/<int:pk>/',views.EventDeleteView.as_view(), name="event_delete"), #イベント削除
    path('group_edit/<int:pk>/',views.GroupEditView.as_view(), name="group_edit"), #グループ編集
    path('group_detail/<int:pk>/',views.GroupDetailView.as_view(), name="group_detail"), #グループ詳細
    # path('event_cal/',views.EventCalView.as_view(), name="event_cal"), #イベントカレンダー
    # path('event_cal/<int:year>/<int:month>/',views.EventCalView.as_view(), name="event_cal"), #イベントカレンダー
    path('gp_event_cal/<int:year>/<int:month>/',views.GpEventCalView.as_view(), name="gp_event_cal"), #イベントカレンダー(所属しているグループのイベント表示)
    path('gp_event_cal/',views.GpEventCalView.as_view(), name="gp_event_cal"), #イベントカレンダー(所属しているグループのイベント表示)
    path('group_detail/<int:pk>/event_new/', views.EventCreateView.as_view(), name='event_new'), #イベント作成
    path('group/new/', views.GroupCreateView.as_view(), name='group_new'), #グループ作成
    path('group/signal/', views.groupSignal, name='group_signal'), #グループシグナル(#グループ登録時、同時にApprovedStaffにも登録される)
    path('group_join/<int:pk>/', views.GroupJoinView.as_view(), name='group_join'), #グループ加入申請


]
