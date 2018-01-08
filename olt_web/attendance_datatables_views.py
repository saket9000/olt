from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from olt_web import models
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.utils import timezone
import pytz
import datetime
from django.conf import settings


class AttendanceListDatatable(BaseDatatableView):
    model = models.Attendance

    columns = [
        'id', 'student.name', 'student.roll_no,', 'subject.name', 
        'total_attendance', 'obtained_attendance',
    ]
    order_columns = [
        'id', 'student.name', 'student.roll_no,', 'subject.name', 
        'total_attendance', 'obtained_attendance',
    ]

    max_display_length = 500

    def get_initial_queryset(self):
        return models.Attendance.objects.filter(soft_delete=False).order_by('-id')

    # def filter_queryset(self, qs):
    #     search = self.request.GET.get(u'search[value]', None)
    #     if search:
    #         qs = qs.filter(
    #             Q(name__icontains=search) | Q(email__icontains=search) | 
    #                 Q(phone__icontains=search) | Q(course__name__icontains=search) | 
    #                 Q(batch__icontains=search)  |Q(roll_no__icontains=search) |
    #                 Q(gender__icontains=search)
    #         )
    #     return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                item.id,
                item.student.name,
                item.student.roll_no,
                item.subject.name,
                item.total_attendance,
                item.obtained_attendance,
                '/edit-attendance/'+str(item.pk),
                '/delete-attendance/'+str(item.pk),
            ])
        return data
