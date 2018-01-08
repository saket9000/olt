from django.conf.urls import *
from olt_web import views
from django.contrib.auth.views import *
from django.contrib.auth.decorators import login_required
from olt_web import test_dt_views
from olt_web import student_datatables_views
from olt_web import exam_datatables_views
from olt_web import subject_datatables_views
from olt_web import result_datatables_views
from olt_web import result_main_datatables_views
from olt_web import attendance_datatables_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^accounts/login', views.login_view, name = 'login_view'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^home$', views.home, name='home'),
    url(r'^change-password$', views.change_password, name='change-password'),
    url(r'^password_reset$', views.password_reset, name='password_reset'),
    url(r'^reset-password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$', views.password_resetenter, 
        name='password_resetenter'),
    url(r'^add-result$', views.addResult, name='add-result'),
    url(r'^add-student$', views.addStudent, name='add-student'),
    url(r'^add-result-data$', views.addResultData, name='add-result-data'),
    url(r'^add-exam-name$', views.addExamName, name='add-exam-name'),
    url(r'^add-subject$', views.addSubject, name='add-subject'),
    url(r'^view-students/$', views.view_students, name='view-students'),
    url(r'^view-students-dt/$', (student_datatables_views.StudentListDatatable.as_view()), 
        name='view-students-dt'),
    url(r'^view-exams/$', views.view_exams, name='view-exams'),
    url(r'^view-exams-dt/$', (exam_datatables_views.ExamListDatatable.as_view()), 
        name='view-exams-dt'),
    url(r'^view-subjects/$', views.view_subjects, name='view-subjects'),
    url(r'^view-subjects-dt/$', (subject_datatables_views.SubjectListDatatable.as_view()), 
        name='view-subjects-dt'),
    url(r'^view-results/$', views.view_results, name='view-results'),
    url(r'^view-results-dt/$', (result_datatables_views.ResultListDatatable.as_view()), 
        name='view-results-dt'),
    url(r'^edit-student/(?P<student_id>[0-9]+)$', views.edit_student, name = 'edit-student'),
    url(r'^edit-exam-name/(?P<exam_id>[0-9]+)$', views.edit_exam_name, name = 'edit-exam-name'),
    url(r'^edit-result-data/(?P<rdata_id>[0-9]+)$', views.edit_result_data, name = 'edit-result-data'),
    url(r'^edit-subject/(?P<subject_id>[0-9]+)$', views.edit_subject, name='edit-subject'),
    url(r'^delete-student/(?P<student_id>[0-9]+)$', views.delete_student, name='delete-student'),
    url(r'^delete-exam/(?P<exam_id>[0-9]+)$', views.delete_exam, name='delete-exam'),
    url(r'^delete-subject/(?P<subject_id>[0-9]+)$', views.delete_subject, name='delete-subject'),
    url(r'^delete-result/(?P<result_id>[0-9]+)$', views.delete_result, name='delete-result'),
    url(r'^add-result-main$', views.addResultMain, name='add-result-main'),
    url(r'^edit-result-main/(?P<resultMain_id>[0-9]+)$', views.editResultMain, name = 'edit-result-main'),
    url(r'^view-result-main/$', views.view_result_main, name='view-result-main'),
    url(r'^view-result-main-dt/$', (result_main_datatables_views.ResultMainListDatatable.as_view()), 
        name='view-results-main-dt'),
    url(r'^delete-result-main/(?P<resultMain_id>[0-9]+)$', views.delete_result_main, name='delete-result-main'),
    url(r'^add-attendance$', views.add_attendance, name='add-attendance'),
    url(r'^edit-attendance/(?P<attendance_id>[0-9]+)$', views.edit_attendance, name='edit-attendance'),
    url(r'^view-attendance/$', views.view_attendance, name='view-attendance'),
    url(r'^view-attendance-dt/$', (attendance_datatables_views.AttendanceListDatatable.as_view()), 
        name='view-attendance-dt'),
    url(r'^delete-attendance/(?P<attendance_id>[0-9]+)$', views.delete_attendance, name='delete-attendance'),
]