from django.urls import path, include
from course import views

urlpatterns = [
    # path("fbv/list", views.course_list, name="fbv-list"),
    # path("fbv/detail/<int:pk>", views.course_detail, name="fbv-detail"),
    # path("cbv/list", views.CourseList.as_view(), name="cbv-list"),
    path("cbv/list", views.FieldRecordList.as_view(), name="record-list"),
    path("cbv/detail/<int:pk>", views.FieldRecordDetail.as_view(), name="cbv-detail"),
    path('api/field-data/', views.FieldDictView.as_view(), name='field-data'),
    # path("gcbv/list", views.GCourseList.as_view(), name="gcbv-list"),
    # path("gcbv/detail/<int:pk>", views.GCourseDetail.as_view(), name="gcbv-detail")
]