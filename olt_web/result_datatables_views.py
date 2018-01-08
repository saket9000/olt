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


class ResultListDatatable(BaseDatatableView):
    model = models.Result

    columns = [
        'id', 'course', 'exam_name', 'subject', 'batch', 'result_type',
    ]
    order_columns = [
        'id', 'course', 'exam_name', 'subject', 'batch', 'result_type',
    ]

    max_display_length = 500

    def get_initial_queryset(self):
        return models.Result.objects.filter(soft_delete=False).order_by('-id')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(
                Q(subject__name__icontains=search) | Q(batch__icontains=search) | 
                    Q(result_type__icontains=search) | Q(course__name__icontains=search) | 
                    Q(exam_name__name__icontains=search)
            )
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                item.id,
                item.course.name,
                item.exam_name.name,
                item.subject.name,
                item.batch,
                item.result_type,
                '/edit-result-data/'+str(item.pk),
                '/delete-result-data/'+str(item.pk),
            ])
        return data
