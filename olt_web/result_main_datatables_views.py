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


class ResultMainListDatatable(BaseDatatableView):
    model = models.ResultMain

    columns = [
        'id', 'student.roll_no', 'student.name', 'result.subject.name', 'result.result_type',
         'student.batch', 'marks_obtained'
    ]
    order_columns = [
        'id', 'student.roll_no', 'student.name', 'result.subject.name', 'result.result_type',
         'student.batch', 'marks_obtained'
    ]

    max_display_length = 500

    def get_initial_queryset(self):
        return models.ResultMain.objects.filter(soft_delete=False).order_by('-id')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(
                Q(student__roll_no__icontains=search) | Q(student__name__icontains=search) | 
                    Q(result__result_type__icontains=search) | Q(result__subject__name__icontains=search) | 
                    Q(marks_obtained__icontains=search) | Q(student__batch__icontains=search)
            )
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                item.id,
                item.student.roll_no,
                item.student.name,
                item.result.subject.name,
                item.result.result_type,
                item.student.batch,
                item.marks_obtained,
                '/edit-result-main/'+str(item.pk),
                '/delete-result-main/'+str(item.pk),
            ])
        return data
