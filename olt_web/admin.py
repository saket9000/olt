from django.contrib import admin
from olt_web.models import *

# Register your models here.

class DeleteNotAllowedAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class TeacherAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "e_id", "user", "name", "dob", "phone", "blood_group",
        "student_permit", "result_permit", "subject_permit", 
        "exam_permit", "soft_delete", "photo",
    ]
    list_filter = [
        "student_permit", "result_permit", "subject_permit",
        "exam_permit", "soft_delete",
    ]


class StudentAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "roll_no", "name", "dob", "phone", "blood_group",
        "guardian_name", "guardian_phone", "batch",
        "email", "course", "soft_delete"
    ]
    list_filter = [
        "course", "batch", "soft_delete"
    ]


class CourseAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "name", "abbr", "duration", "soft_delete",
    ]
    list_filter = [
        "duration", "soft_delete"
    ]


class SubjectAdmin(DeleteNotAllowedAdmin):
	list_display = [
		"course", "name", "s_id", "s_type",
		 "max_marks", "soft_delete",
	]
	list_filter = [
		"course", "name", "soft_delete"
	]


class ResultAdmin(DeleteNotAllowedAdmin):
	list_display = [
		"result_type", "exam_name", "course", "subject", "batch",
		"soft_delete"
	]
	list_filter = [
		"result_type", "exam_name", "course", "subject", "batch",
		"soft_delete"
	]


class ResultMainAdmin(DeleteNotAllowedAdmin):
	list_display = [
		"student", "result", "marks_obtained", "soft_delete"
	]
	list_filter = [
		"student", "result", "soft_delete"
	]


class AttendanceAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "student", "subject", "total_attendance",
        "obtained_attendance", "soft_delete"
    ]
    list_filter = [
        "student", "subject", "soft_delete"
    ]


class HistoryAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "user", "activity_type", "activity"
    ]
    list_filter = [
        "user", "activity_type"
    ]
    readonly_fields = [
        "user", "activity", "activity_type", "soft_delete"
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permissions(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(HistoryAdmin, self).save_model(request, obj, form, change)


class PasswordResetAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "user", "password_request_created_at", "token_consumed"
    ]
    list_filter = [
        "password_request_created_at", "token_consumed"
    ]
    readonly_fields = [
        "user", "password_request_created_at", "token",
        "token_consumed", "soft_delete",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permissions(self, request, obj=None):
        return False


class ExamNameAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "name"
    ]

        
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(ResultMain, ResultMainAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(PasswordReset, PasswordResetAdmin)
admin.site.register(ExamName, ExamNameAdmin)
admin.site.disable_action("delete_selected")
