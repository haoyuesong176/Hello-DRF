from django.urls import path, include
from course import views

urlpatterns = [
    path('api/field-data/', views.FieldDictView.as_view(), name='field-data'),
    path('api/field-book/', views.BookFieldRecordsView.as_view(), name='book'),
    path('api/field-matching/', views.MatchFieldRecordsView.as_view(), name='matching'),
    path('api/field-matched/', views.ConfirmMatchFieldRecordsView.as_view(), name='matched'),
    path('api/field-unbook/', views.UnbookFieldRecordsView.as_view(), name='unbook'),
    path('api/wx-login/', views.WXLoginView.as_view(), name='login-auth'),
    path('api/user-book-data/', views.UserBookedFieldRecordsView.as_view(), name='user-book-data'),
    path('api/user-matching-data/', views.UserMatchingFieldRecordsView.as_view(), name='user-matching-data'),
    path('api/user-today-schedule/', views.UserTodayScheduleView.as_view(), name='user-today-schedule'),
    path('api/user-profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('api/update-user-icon/', views.UpdateUserIconView.as_view(), name='user-icon-update'),
    path('fields/<int:field_id>/matching-user/', views.FieldMatchingUserInfoView.as_view(), name='field-matching-user'),
]

