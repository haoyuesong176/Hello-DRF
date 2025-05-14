from django.urls import path, include
from course import views

urlpatterns = [
    # path("cbv/detail/<int:pk>", views.FieldRecordDetail.as_view(), name="cbv-detail"),
    # path("cbv/list", views.FieldRecordList.as_view(), name="record-list"),
    path('api/field-data/', views.FieldDictView.as_view(), name='field-data'),
    path('api/field-book/', views.BookFieldRecordsView.as_view(), name='book'),
    path('api/field-unbook/', views.UnbookFieldRecordsView.as_view(), name='unbook'),
    path('api/wx-login/', views.WXLoginView.as_view(), name='login-auth'),
    path('api/user-book-data/', views.UserBookedFieldRecordsView.as_view(), name='user-book-data'),
    path('api/user-profile/', views.UserProfileView.as_view(), name='user-profile'),
]

