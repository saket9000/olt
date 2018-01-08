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


class SubjectListDatatable(BaseDatatableView):
    model = models.Subject

    columns = [
        'id', 'name', 'course,', 's_type', 's_id', 'max_marks',
    ]
    order_columns = [
        'id', 'name', 'course,', 's_type', 's_id', 'max_marks',
    ]

    max_display_length = 500

    def get_initial_queryset(self):
        return models.Subject.objects.filter(soft_delete=False).order_by('-id')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(s_type__icontains=search) | 
                    Q(max_marks__icontains=search) | Q(course__name__icontains=search) | 
                    Q(s_id__icontains=search)
            )
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                item.id,
                item.name,
                item.course.name,
                item.s_type,
                item.s_id,
                item.max_marks,
                '/edit-subject/'+str(item.pk),
                '/delete-subject/'+str(item.pk),
            ])
        return data
