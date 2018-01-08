from django.shortcuts import (render, render_to_response)
from django.http import (
	HttpResponse,
	HttpResponseRedirect,
	JsonResponse,
	Http404
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from olt_web import models
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.core.cache import cache
from olt_web.helpers import context_helper
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers
from django.core import serializers
import json
from highcharts.views import *
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six, timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from olt.settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
from string import ascii_letters, digits
from datetime import datetime, timedelta
import hashlib
import random

# Create your views here.


def index(request):

	"""
	This view redirects user to home if logged in else it redirects user
	to login page.
	"""

	if request.user.is_authenticated:
		return HttpResponseRedirect('home')
	return HttpResponseRedirect('login')


def login_view(request):

	"""
	Login view imported from templates.
	"""

	if request.user.is_authenticated():
		return HttpResponseRedirect('/home')
	next_url = request.GET.get('next', '/home')
	if request.method == "POST":
		print("1")
		username = request.POST.get('username')
		password = request.POST.get('password')
		print("2")
		if username and password:
			user = authenticate(request, username=username, password=password)
			if user:
				login(request, user)
				return HttpResponseRedirect(next_url)
			return render(
				request, 'loginPage.html',
				{'message': 'Invalid login details'}
			)
	return render(request, "loginPage.html", {})


def logout_view(request):

	"""
	Log out user to the login page.
	"""

	logout(request)
	return HttpResponseRedirect('login')


@login_required
def home(request):
	
	"""
	This renders the home page.
	"""

	context_dict = {}
	employee = models.Teacher.objects.filter(
		user=request.user
	).first()
	# context_dict = {
	#     context_helper.get_emp_info(employee)
	# }
	# print (context_dict)
	context_dict.update(context_helper.get_emp_info(employee))
	return render(request, "home.html", context_dict)


#for Teachers
@login_required
def change_password(request):

	"""
	Change password form for teachers
	"""

	emp = models.Teacher.objects.get(user=request.user)
	context_dict = {}
	if request.method == 'POST':
		form = AdminPasswordChangeForm(user=request.user, data=request.POST)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			context_dict["message"] = "Password changed successfully"
			history = models.History(
				user=emp,
				activity="",
				activity_type="Changed password"
			)
			history.save()
		else:
			context_dict["message"] = "Password not changed"
	return render(request, "changePassword.html", context_dict)


#for Teachers
def password_reset(request):

	"""
	View to take email and mail the link to
	reset password.
	"""

	context_dict = {}
	if request.method == 'POST':
		email = request.POST.get('email')
		if email:
			user = models.Teacher.objects.get(
				soft_delete=False, user__email=email
			)
			if not user:
				context_dict["message"] = "Email ID does'nt exist, Enter Correct details"
			mail = {
				'email': email,
				'domain': request.META['HTTP_HOST'],
				'site_name': 'Placement Portal',
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'user': user,
				'token': ''.join([random.choice(ascii_letters+digits) for i in range (128)]),
				'protocol': 'http',
			}
			try:
				reset_token = models.PasswordReset(
					user=user,
					token=mail['token'],
					token_consumed=False,
				)
				reset_token.save()
			except Exception as e:
				print (e)
			subject_template_name = 'password_reset_email_subject.txt'
			email_template_name = 'password_reset_email.html'
			subject = loader.render_to_string(subject_template_name, mail)
			subject = ''.join(subject.splitlines())
			email_data = loader.render_to_string(email_template_name, mail)
			send_mail(subject, email_data, DEFAULT_FROM_EMAIL, [email], fail_silently=False)
			context_dict["message"] = "Email has been sent to your registered Email ID with instructions."
	return render(request, "password_reset_form.html", context_dict)


def password_resetenter(request, uidb64=None, token=None):

	"""
	Enter new password for reset password.
	"""

	context_dict = {}
	if request.method == 'POST':
		assert uidb64 is not None and token is not None
		uid = urlsafe_base64_decode(uidb64)
		user = models.Teacher.objects.get(
			soft_delete=False, pk=uid
		)
		db_user = user.user
		reset_token = models.PasswordReset.objects.get(
			token=token, user=user
		)
		token_check = models.PasswordReset.objects.filter(
			user=user, soft_delete=False, token_consumed=False,
		).exclude(token=token).first()
		update_fields = []
		token_check.token_consumed = True
		update_fields.append('token_consumed')
		token_check.soft_delete = True
		update_fields.append('soft_delete')
		token_check.save(update_fields=update_fields)
		time_threshold = timezone.now() - reset_token.password_request_created_at
		if time_threshold > timedelta(minutes=30):
			try:
				update_fields = []
				reset_token.token_consumed = True
				update_fields.append('token_consumed')
				reset_token.soft_delete = True
				update_fields.append('soft_delete')
				reset_token.save(update_fields=update_fields)
			except Exception as e:
				print (e)
		if reset_token.user == user and reset_token.token == token:
			if reset_token.token_consumed  == False and reset_token.soft_delete  == False:
				try:
					update_fields = []
					reset_token.token_consumed = True
					update_fields.append('token_consumed')
					reset_token.soft_delete = True
					update_fields.append('soft_delete')
					reset_token.save(update_fields=update_fields)
				except Exception as e:
					print (e)
				form = AdminPasswordChangeForm(user=db_user, data=request.POST)
				if form.is_valid():
					form.save()
					history = models.History(
						user=user,
						activity = "",
						activity_type = "Reset Password"
					)
					history.save()
					context_dict["message"] = "Password changed successfully"
				else:
					context_dict["message"] = "Password not changed"
			else:
				context_dict["message"] = "Link is no longer valid"
	return render(request, "reset.html", context_dict)


#for Teachers only
@login_required
def addStudent(request):
	
	"""
	Add Students details to the portal.
	"""
	emp = models.Teacher.objects.get(user=request.user)
	if not emp.student_permit:
		raise Http404
	context_dict = {
		"all_courses": context_helper.course_helper(),
		"blood_groups": context_helper.blood_group_helper(),
		"guardian_types": context_helper.guardian_type_helper(),
		"gender_type": context_helper.gender_helper(),
	}
	if request.method == 'POST':
		sname = request.POST.get('sname')
		roll = request.POST.get('rno')
		dob = request.POST.get('dob')
		gender = request.POST.get('gender_picker')
		bgroup = request.POST.get('blood_group_picker')
		if bgroup == 'Choose option':
			bgroup = None
		phone = request.POST.get('phone')
		curradd = request.POST.get('curradd')
		permadd = request.POST.get('permadd')
		gname = request.POST.get('gname')
		course = request.POST.get('course_picker')
		batch = request.POST.get('batch')
		gtype = request.POST.get('guardian_type_picker')
		gphone = request.POST.get('gphone')
		email = request.POST.get('email')
		duplicate_student = models.Student.objects.filter(
			name=sname, dob=dob, guardian_name=gname,
			guardian_type=gtype, phone=phone, email=email
		).first()
		if duplicate_student:
			context_dict["message"] = 'Student already exist.'
			duplicate_student.soft_delete=False
			duplicate_student.save()
			return render(request, "AddStudent.html", context_dict)
		address_flag = request.POST.get('address_flag')
		address_flag = True if address_flag == 'on' else False
		if address_flag == True:
			permadd = curradd
		try:
			student = models.Student(
				name=sname,
				roll_no=roll,
				dob=dob,
				gender=gender,
				blood_group=bgroup,
				phone=phone,
				curr_address=curradd,
				perm_address=permadd,
				guardian_name=gname,
				guardian_type=gtype,
				guardian_phone=gphone,
				course=models.Course.objects.get(pk=course),
				batch=batch,
				email=email,
				address_flag=address_flag
			)
			if "profile-img" in request.FILES:
				student.photo = request.FILES["profile-img"]
			student.save()
			history = models.History(
				user=emp,
				activity='Added roll number' + str(roll) +'.\n',
				activity_type="add student"
			)
			history.save()
			context_dict["message"] = 'Successfully added new student.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	return render(
		request, "addStudent.html", context_dict
	)


#for Teachers only
@login_required
def addResultData(request):

	"""
	For adding Result Meta Data
	"""
	emp = models.Teacher.objects.get(user=request.user)
	if not emp.result_permit:
		raise Http404
	context_dict = {
		"result_type": context_helper.result_type_helper(),
		"all_subjects": context_helper.subject_helper(),
		"all_courses": context_helper.course_helper(),
		"all_exam_name": context_helper.exam_name_helper(),
	}
	if request.method == "POST":
		course = request.POST.get('course_picker')
		result_type = request.POST.get('result_type_picker')
		exam_name = request.POST.get('exam_name_picker')
		subject = request.POST.get('subject_picker')
		batch = request.POST.get('batch')
		duplicate_check = models.Result.objects.filter(
			course=course, result_type=result_type, exam_name=exam_name,
			subject=subject, batch=batch
		).first()
		if duplicate_check:
			context_dict["message"] = 'Result Data already exist.'
			duplicate_check.soft_delete=False
			duplicate_check.save()
			return render(request, "addResultData.html", context_dict)
		try:
			result_data = models.Result(
				course=models.Course.objects.get(pk=course),
				result_type=result_type, 
				exam_name=models.ExamName.objects.get(pk=course),
				subject=models.Subject.objects.get(pk=course), 
				batch=batch
			)
			result_data.save()
			history = models.History(
				user=emp,
				activity='Added result data' + str(course)+ str(result_type)+ 
					str(exam_name)+ str(subject)+ str(batch) +'.\n',
				activity_type="add result data"
			)
			history.save()
			context_dict["message"] = 'Successfully added new Result Data.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	return render(request, "addResultData.html", context_dict)


#for examination department only
@login_required
def addExamName(request):

	"""
	For adding Exam name like semester 1 or trimester 2.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.exam_permit:
		raise Http404
	context_dict = {}
	if request.method == "POST":
		name = request.POST.get('ename')
		duplicate_check = models.ExamName.objects.filter(
			name=name,
		).first()
		if duplicate_check:
			context_dict["message"] = "Exam Name already exists."
			duplicate_check.soft_delete=False
			duplicate_check.save()
			return render(request, "addExamName.html", context_dict)
		try:
			examName = models.ExamName(
				name=name
			)
			examName.save()
			history = models.History(
				user=emp,
				activity='Added Exam' + str(name) +'.\n',
				activity_type="add exam."
			)
			history.save()
			context_dict["message"] = 'Successfully added new Exam Type.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	return render(request, "addExamName.html", context_dict)


#can be exclusive for exam department 
@login_required
def addSubject(request):

	"""
	For adding subjects
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.subject_permit:
		raise Http404
	context_dict = {
		"all_courses": context_helper.course_helper(),
		"subject_types": context_helper.subject_type_helper(),
	}
	if request.method == "POST":
		course = request.POST.get('course_picker')
		name = request.POST.get('sname')
		sid = request.POST.get('sid')
		stype = request.POST.get('subject_picker')
		maxmarks = request.POST.get('marks')
		duplicate_check = models.Subject.objects.filter(
			course=course, name=name, s_id=sid,
			s_type=stype, max_marks=maxmarks,
		).first()
		if duplicate_check:
			context_dict["message"] = "Subject already exists."
			duplicate_check.soft_delete=False
			duplicate_check.save()
			return render(request, "addSubject.html", context_dict)
		try:
			subject = models.Subject(
				course=models.Course.objects.get(pk=course),
				name=name,
				s_id=sid,
				s_type=stype,
				max_marks=maxmarks,
			)
			subject.save()
			history = models.History(
				user=emp,
				activity='Added Subjetc ' + str(name)+ str(sid) +'.\n',
				activity_type="add result data"
			)
			history.save()
			context_dict["message"] = 'Successfully added new subject.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	return render(request, "addSubject.html", context_dict)


@login_required
def edit_student(request, student_id):

	"""
	View to edit the already existing student in database by taking student_id.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.student_permit:
		raise Http404
	student = models.Student.objects.filter(
		pk=student_id, soft_delete=False
	).first()
	if not student:
		raise Http404
	context_dict = {
		"all_courses": context_helper.course_helper(),
		"blood_groups": context_helper.blood_group_helper(),
		"guardian_types": context_helper.guardian_type_helper(),
		"gender_types": context_helper.gender_helper(),
		'student_id': student_id
	}
	if request.method == 'POST':
		update_fields = []
		activity = ''
		sname = request.POST.get('sname')
		roll = request.POST.get('rno')
		dob = request.POST.get('dob')
		gender = request.POST.get('gender_picker')
		bgroup = request.POST.get('blood_group_picker')
		if bgroup == 'Choose option':
			bgroup = None
		phone = request.POST.get('phone')
		curradd = request.POST.get('curradd')
		permadd = request.POST.get('permadd')
		gname = request.POST.get('gname')
		course = request.POST.get('course_picker')
		batch = request.POST.get('batch')
		gtype = request.POST.get('guardian_type_picker')
		gphone = request.POST.get('gphone')
		email = request.POST.get('email')
		address_flag = request.POST.get('address_flag')
		print (address_flag)
		address_flag = True if address_flag == 'on' else False
		if address_flag == True:
			permadd = curradd
		try:
			if "profile-img" in request.FILES:
				student.photo = request.FILES["profile-img"]
				update_fields.append('photo')
				activity += 'Changed photo.\n'
			if student.name != sname:
				student.name = sname
				update_fields.append('name')
				activity += 'Changed name to '+ str(sname) +'.\n'
			if student.roll_no != roll:
				student.roll_no = roll
				update_fields.append('roll_no')
				activity += 'Changed roll number to '+ str(roll) +'.\n'
			if str(student.dob) != str(dob):
				student.dob = dob
				update_fields.append('dob')
				activity += 'Changed DOB to ' + str(dob) + '.\n'
			if student.gender != gender:
				student.gender = gender
				update_fields.append('gender')
				activity += 'Changed gender to ' + str(gender) + '.\n'
			if student.blood_group != bgroup:
				student.blood_group = bgroup
				update_fields.append('blood_group')
				activity += 'Changed blood group to ' + str(bgroup) + '.\n'
			if student.phone != phone:
				student.phone = phone
				update_fields.append('phone')
				activity += 'Changed phone number to ' + str(phone) + '.\n'
			if student.curr_address != curradd:
				student.curr_address = curradd
				update_fields.append('curr_address')
				activity += 'Changed current address to ' + str(curradd) + '.\n'
			if student.perm_address != permadd:
				student.perm_address = permadd
				update_fields.append('perm_address')
				activity += 'Changed permanent address to ' + str(permadd) + '.\n'
			if student.curr_address != curradd:
				student.curr_address = curradd
				update_fields.append('curr_address')
				activity += 'Changed current address to ' + str(curradd) + '.\n'
			if student.guardian_name != gname:
				student.guardian_name = gname
				update_fields.append('guardian_name')
				activity += 'Changed current address to ' + str(gname) + '.\n'
			if student.guardian_phone != gphone:
				student.guardian_phone = gphone
				update_fields.append('guardian_phone')
				activity += 'Changed guardian phone to ' + str(gphone) + '.\n'
			if student.guardian_type != gtype:
				student.guardian_type = gtype
				update_fields.append('guardian_type')
				activity += 'Changed current address to ' + str(gtype) + '.\n'
			if str(student.course.pk) != str(course):
				student.course = models.Course.objects.get(pk=course)
				update_fields.append('course')
				activity += 'Changed course to ' + str(course) + '.\n'
			if student.batch != batch:
				student.batch = batch
				update_fields.append('batch')
				activity += 'Changed batch to' + str(batch) + '.\n'
			if student.email != email:
				student.email = email
				update_fields.append('email')
				activity += 'Changed email to ' + str(email) + '.\n'
			if student.address_flag != address_flag:
				student.address_flag = address_flag
				update_fields.append('address_flag')
				activity += 'Changed address flag.'
			student.save(update_fields=update_fields)
			history = models.History(
				user=emp,
				activity=activity,
				activity_type="edit student"
			)
			history.save()
			context_dict["message"] = 'Successfully updated student.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	context_dict.update(context_helper.get_student_info(student))
	if type(context_dict['dob']) == str:
		context_dict['dob'] = datetime.strptime(context_dict['dob'], '%Y-%m-%d')
	for i in context_dict['course']:
		try: del context_dict['all_courses'][i]
		except: pass
	for i in context_dict['blood_group']:
		try: context_dict['blood_groups'].remove(i)
		except: pass
	for i in context_dict['guardian_type']:
		try: context_dict['guardian_types'].remove(i)
		except: pass
	for i in context_dict['gender_type']:
		try: context_dict['gender_types'].remove(i)
		except: pass
	if context_dict.get('success', False):
		return HttpResponseRedirect('/view-students')
	return render(
		request, "editStudent.html", context_dict
	)


@login_required
def edit_exam_name(request, exam_id):

	"""
	Edit Exam Detail.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.exam_permit:
		raise Http404
	exam = models.ExamName.objects.filter(
		pk=exam_id, soft_delete=False
	).first()
	if not exam:
		raise Http404
	context_dict = {
		'exam_id': exam_id
	}
	if request.method == 'POST':
		update_fields = []
		activity = ''
		name = request.POST.get('name')
		try:
			if exam.name != name:
				exam.name = name
				update_fields.append('name')
				activity += 'Changed Exam name to '+ str(name) +'.\n'
			exam.save(update_fields=update_fields)
			history = models.History(
				user=emp,
				activity=activity,
				activity_type="edit exam name"
			)
			history.save()
			context_dict["message"] = 'Successfully updated Exam.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	context_dict.update(context_helper.get_exam_info(exam))
	if context_dict.get('success', False):
		return HttpResponseRedirect('/view-exams')
	return render(request, "editExamName.html", context_dict)


@login_required
def edit_result_data(request, rdata_id):

	"""
	Edit Result Data.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.result_permit:
		raise Http404
	result_data = models.Result.objects.filter(
		pk=rdata_id, soft_delete=False
	).first()
	if not result_data:
		raise Http404
	context_dict = {
		"result_types": context_helper.result_type_helper(),
		"all_subjects": context_helper.subject_helper(),
		"all_courses": context_helper.course_helper(),
		"all_exam_name": context_helper.exam_name_helper(),
		'rdata_id': rdata_id,
	}
	if request.method == 'POST':
		update_fields = []
		activity = ''
		course = request.POST.get('course_picker')
		result_type = request.POST.get('result_type_picker')
		exam_name = request.POST.get('exam_name_picker')
		subject = request.POST.get('subject_picker')
		batch = request.POST.get('batch')
		try:
			if result_data.result_type != result_type:
				result_data.result_type = result_type
				update_fields.append('result_type')
				activity += 'Changed result type to ' + str(result_type) + '.\n'
			if str(result_data.course.pk) != str(course):
				result_data.course = models.Course.objects.get(pk=course)
				update_fields.append('course')
				activity += 'Changed course to ' + str(course) + '.\n'
			if str(result_data.exam_name.pk) != str(exam_name):
				result_data.exam_name = models.ExamName.objects.get(pk=exam_name)
				update_fields.append('exam_name')
				activity += 'Changed Exam name to ' + str(exam_name) + '.\n'
			if str(result_data.subject.pk) != str(subject):
				result_data.subject = models.Subject.objects.get(pk=subject)
				update_fields.append('subject')
				activity += 'Changed subject to ' + str(subject) + '.\n'
			if result_data.batch != batch:
				result_data.batch = batch
				update_fields.append('batch')
				activity += 'Changed batch to' + str(batch) + '.\n'
			result_data.save(update_fields=update_fields)
			history = models.History(
				user=emp,
				activity=activity,
				activity_type="edit result data"
			)
			history.save()
			context_dict["message"] = 'Successfully updated Result Data.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	context_dict.update(context_helper.get_result_info(result_data))
	for i in context_dict['courses']:
		#use this for dynamic
		try: del context_dict['all_courses'][i]
		except: pass
	for i in context_dict['result_type']:
		#use this for static 
		try: context_dict['result_types'].remove(i)
		except: pass
	for i in context_dict['exams']:
		try: del context_dict['all_exam_name'][i]
		except: pass
	for i in context_dict['subjects']:
		try: del context_dict['all_subjects'][i]
		except: pass
	if context_dict.get('success', False):
		return HttpResponseRedirect('/view-results')
	return render(
		request, "editResultData.html", context_dict
	)


@login_required
def edit_subject(request,subject_id):

	"""
	Edit details related to the subject / Meta data of subject.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.subject_permit:
		raise Http404
	subject = models.Subject.objects.filter(
		pk=subject_id, soft_delete=False
	).first()
	if not subject:
		raise Http404
	context_dict = {
		"all_courses": context_helper.course_helper(),
		"subject_types": context_helper.subject_type_helper(),
		'subject_id': subject_id,
	}
	if request.method == 'POST':
		update_fields = []
		activity = ''
		course = request.POST.get('course_picker')
		name = request.POST.get('sname')
		sid = request.POST.get('sid')
		stype = request.POST.get('subject_picker')
		maxmarks = request.POST.get('marks')
		try:
			if str(subject.course.pk) != str(course):
				subject.course = models.Course.objects.get(pk=course)
				update_fields.append('course')
				activity += 'Changed course to ' + str(course) + '.\n'
			if subject.s_type != stype:
				subject.s_type = stype
				update_fields.append('s_type')
				activity += 'Changed subject type to ' + str(stype) + '.\n'
			if subject.name != name:
				subject.name = name
				update_fields.append('name')
				activity += 'Changed subject name to' + str(name) + '.\n'
			if subject.s_id != sid:
				subject.s_id = sid
				update_fields.append('s_id')
				activity += 'Changed subject ID to' + str(sid) + '.\n'
			if subject.max_marks != maxmarks:
				subject.max_marks = maxmarks
				update_fields.append('max_marks')
				activity += 'Changed maximum marks to' + str(maxmarks) + '.\n'
			subject.save(update_fields=update_fields)
			history = models.History(
				user=emp,
				activity=activity,
				activity_type="edit subject"
			)
			history.save()
			context_dict["message"] = 'Successfully updated Result Data.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	context_dict.update(context_helper.get_subject_info(subject))
	for i in context_dict['courses']:
		try: del context_dict['all_courses'][i]
		except: pass
	for i in context_dict['subject_type']:
		try: context_dict['subject_types'].remove(i)
		except: pass
	if context_dict.get('success', False):
		return HttpResponseRedirect('/view-subjects')
	return render(
		request, "editSubject.html", context_dict
	)


@login_required
def view_test(request):

	"""
	View students in data tables.
	"""

	context_dict = {
		'title': 'All Students'
	}
	return render(
		request,
		'viewTest.html',
		context_dict
	)


@login_required
def view_students(request):

	"""
	View students using data tables.
	"""

	context_dict = {
		'title': 'All Students',
	}
	return render(request, "viewStudent.html", context_dict)


@login_required
def view_exams(request):

	"""
	View all exams.
	"""
	context_dict = {
		'title': 'All Exams',
	}
	return render(request, "viewExam.html", context_dict)


@login_required
def view_subjects(request):

	"""
	View all subjects.
	"""

	context_dict = {
		'title': 'All Subjects',
	}
	return render(request, "viewSubject.html", context_dict)


@login_required
def view_results(request):

	"""
	View all subjects.
	"""

	context_dict = {
		'title': 'All Results',
	}
	return render(request, "viewResult.html", context_dict)


@login_required
def delete_student(request, student_id):

	"""
	Delete student from data tables.
	"""

	emp = models.Employee.objects.get(user=request.user)
	if not emp.student_permit:
		raise Http404
	student = models.Student.objects.filter(
		pk=student_id, soft_delete=False
	).first()
	if not student:
		raise Http404
	student.soft_delete = True
	activity = 'Deleted student' + str(student) + '.\n'
	student.save(update_fields=['soft_delete'])
	history = models.History(
				user=emp,
				activity=activity,
				activity_type="delete student"
			)
	history.save()
	return HttpResponseRedirect('/view-students')


@login_required
def delete_exam(request, exam_id):

	"""
	Delete student from data tables.
	"""

	emp = models.Employee.objects.get(user=request.user)
	if not emp.exam_permit:
		raise Http404
	exam = models.ExamName.objects.filter(
		pk=exam_id, soft_delete=False
	).first()
	if not exam:
		raise Http404
	exam.soft_delete = True
	activity = 'Deleted Exam' + str(exam) + '.\n'
	exam.save(update_fields=['soft_delete'])
	history = models.History(
				user=emp,
				activity=activity,
				activity_type="delete exam"
			)
	history.save()
	return HttpResponseRedirect('/view-exams')


@login_required
def delete_subject(request, subject_id):

	"""
	Delete student from data tables.
	"""

	emp = models.Employee.objects.get(user=request.user)
	if not emp.subject_permit:
		raise Http404
	subject = models.Subject.objects.filter(
		pk=subject_id, soft_delete=False
	).first()
	if not subject:
		raise Http404
	subject.soft_delete = True
	activity = 'Deleted subject' + str(subject) + '.\n'
	subject.save(update_fields=['soft_delete'])
	history = models.History(
				user=emp,
				activity=activity,
				activity_type="delete subject"
			)
	history.save()
	return HttpResponseRedirect('/view-subjects')


@login_required
def delete_result(request, result_id):

	"""
	Delete student from data tables.
	"""

	emp = models.Employee.objects.get(user=request.user)
	if not emp.result_permit:
		raise Http404
	result = models.Result.objects.filter(
		pk=result_id, soft_delete=False
	).first()
	if not result:
		raise Http404
	result.soft_delete = True
	activity = 'Deleted result' + str(result) + '.\n'
	result.save(update_fields=['soft_delete'])
	history = models.History(
				user=emp,
				activity=activity,
				activity_type="delete result"
			)
	history.save()
	return HttpResponseRedirect('/view-results')


#INSTEAD OF THIS USE BATCH_AJAX_TEST  
#This is just the prototype
def addResult(request):
	print("1")
	batch = models.Student.objects.values('batch').distinct()
	print(batch)

	new_dict = {}
	for item in batch:
		batch = item['batch']
		new_dict[batch] = item
	print(new_dict)
	print("1.1")
	if request.method == "POST":
		print("2")
		print(request.POST)
		context_dict = {}
		batch = request.POST.get('batch')
		print(batch)
		students = models.Student.objects.filter(batch=batch).values(
			'name', 'roll_no'
		).distinct()
		print(students)
		x = [i['name'] for i in students]
		print (x)
		for stdnt in students.iterator():
			print(stdnt)
		context_dict.update(students.iterator())

		# name = [li['name'] for li in students]
		# print(name)
		# context_dict.update([name])
		# roll_no = [li['roll_no'] for li in students]
		# print(roll_no)
		# context_dict.update([roll_no])
		# print(context_dict)
		#context_dict.update(context_helper.get_student_info_result(students))
		#if 'csrfmiddlewaretoken' not in request.POST:
		return render(request, "addResult.html", context_dict)
		#context_dict.update(context_helper.get_student_info_result(students))
	return render(request, 'addResult.html', {'batch': new_dict})


#using static/js/resultAjax.js
#has substitute addResultAjax.html combined file 
def batch_ajax_test(request):
	print("1")
	batch = models.Student.objects.values('batch').distinct()
	print(batch)
	if request.method == "POST":
		print("2")
		year = request.POST.get("batch")
		print(year)
		students = models.Student.objects.filter(batch=year).values(
			'roll_no',
		).distinct()
		# roll = request.POST.get('roll')
		# name = models.Student.objects.filter(roll_no=roll).first()
		# print(name)
		print("3")
		print(students)
		# return HttpResponse(simplejson.dumps(students))
		return render(request, "test.html", {'students': students, 'batch':batch})
	return render(request, "test.html", {'batch': batch})


#for multiple drop downs dependent on one another
def test(request):
	if request.method == 'POST':
		student_form = RegStudentResult(data=request.POST)
		print("1")
		if student_form.is_valid():
			print("2")
			roll = student_form.cleaned_data.get
			roll_selected = Student.objects.filter(roll_no=roll('roll_select'))
			print(roll)
			print(roll_selected)
		else:
			print("Invalid")
	else:
		student_form = RegStudentResult()
	return render(request, 'test1.html', {'student_form':student_form})


@login_required
def addResultMain(request):

	"""
	To add results of students /
	link results and students
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.result_permit:
		raise Http404
	context_dict = {
		"result_type": context_helper.result_type_helper(),
		"all_subjects": context_helper.subject_helper(),
		"all_exam_name": context_helper.exam_name_helper(),
	}
	if request.method == 'POST':
		roll = request.POST.get('rno')
		result_type = request.POST.get('result_type_picker')
		exam = request.POST.get('exam_name_picker')
		subject = request.POST.get('subject_picker')
		marks = request.POST.get('marks')
		student = models.Student.objects.filter(
			roll_no=roll
		).first()
		result_data_check = models.Result.objects.filter(
			result_type=result_type, batch=student.batch,
			exam_name=exam, subject=subject
		).first()
		if not result_data_check:
			context_dict["message"] = "Result Data does not exist, first create data for result"
			return render(request, 'addResultMain.html', context_dict)
		duplicate_check = models.ResultMain.objects.filter(
			student=models.Student.objects.filter(roll_no=student).first(), result=result_data_check,
		).first()
		if duplicate_check:
			context_dict["message"]= 'Result already exist.'
			duplicate_check.soft_delete=False
			duplicate_check.save()
			return render(request, "addResultMain.html", context_dict)
		try:
			result = models.ResultMain(
				student=student,
				result=result_data_check, 
				marks_obtained=marks,
			)
			result.save()
			history = models.History(
				user=emp,
				activity='Added result ' + str(result) + 
					'-' + str(marks) +'.\n',
				activity_type="add result "
			)
			history.save()
			context_dict["message"] = 'Successfully added new result.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	return render(request, 'addResultMain.html', context_dict)


@login_required
def editResultMain(request, resultMain_id):

	"""
	Edit Mains Result.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.result_permit:
		raise Http404
	result_main = models.ResultMain.objects.filter(
		pk=resultMain_id, soft_delete=False
	).first()
	print(result_main.result)
	print("1")
	if not result_main:
		raise Http404
	context_dict = {
		"result_types": context_helper.result_type_helper(),
		"all_subjects": context_helper.subject_helper(),
		"all_exam_name": context_helper.exam_name_helper(),
		'resultMain_id': resultMain_id,
	}
	if request.method == 'POST':
		update_fields = []
		activity = ''
		roll = request.POST.get('rno')
		result_type = request.POST.get('result_type_picker')
		exam = request.POST.get('exam_name_picker')
		subject = request.POST.get('subject_picker')
		marks = request.POST.get('marks')
		student = models.Student.objects.filter(
			roll_no=roll
		).first()
		result_data_check = models.Result.objects.filter(
			result_type=result_type, batch=student.batch,
			exam_name=exam, subject=subject
		).first()
		print(result_data_check)
		print("2")
		if not result_data_check:
			context_dict["message"] = "Result Data does not exist, first create data for result"
			return render(request, 'addResultMain.html', context_dict)
		try:
			if result_main.student != student:
				result_main.student = student
				update_fields.append('student')
				activity += 'Changed student to ' + str(student) + '.\n'
			# result_main.student = student
			# update_fields.append('student')
			if result_main.result != result_data_check:
				result_main.result = result_data_check
				update_fields.append('result')
				activity += 'Changed student to ' + str(result) + '.\n'
			# result_main.result = result_data_check
			# update_fields.append('result')
			if result_main.marks_obtained != marks:
				result_main.marks_obtained = marks
				update_fields.append('marks_obtained')
				activity += 'Changed marks to ' + str(marks) + '.\n'
			# result_main.marks_obtained = marks
			# update_fields.append('marks_obtained')
			activity += 'Edited Result Main of student' + str(student) + '.\n'
			result_main.save(update_fields=update_fields)
			history = models.History(
				user=emp,
				activity=activity,
				activity_type='Edit Result Main'
			)
			history.save()
			context_dict["message"] = 'Successfully updated Result Main.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	context_dict.update(context_helper.get_resultMain_info(result_main))
	for i in context_dict['exams']:
		#use this for dynamic
		try: del context_dict['all_exam_name'][i]
		except: pass
	for i in context_dict['subjects']:
		#use this for dynamic
		try: del context_dict['all_subjects'][i]
		except: pass
	for i in context_dict['result_type']:
		#use this for static 
		try: context_dict['result_types'].remove(i)
		except: pass
	if context_dict.get('success', False):
		return HttpResponseRedirect('/view-result-main')
	return render(
		request, "editResultMain.html", context_dict
	)


@login_required
def view_result_main(request):

	"""
	View Main results of students.
	"""

	context_dict = {
		'title': 'All Results Main',
	}
	return render(request, "viewResultMain.html", context_dict)


@login_required
def delete_result_main(request, resultMain_id):

	"""
	Delete Result Main.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.result_permit:
		raise Http404
	result_main = models.ResultMain.objects.filter(
		pk=resultMain_id, soft_delete=False
	).first()
	if not result_main:
		raise Http404
	result_main.soft_delete = True
	activity = 'Deleted result' + str(result_main) + '.\n'
	result_main.save(update_fields=['soft_delete'])
	history = models.History(
				user=emp,
				activity=activity,
				activity_type="delete result"
			)
	history.save()
	return HttpResponseRedirect('/view-result-main')


@login_required
def add_attendance(request):

	"""
	Add result of attendance to the particular subject.
	Can also use this by taking subject ID not giving drop down for subjects.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.student_permit:
		raise Http404
	context_dict = {
		"all_subjects": context_helper.subject_helper(),
	}
	if request.method == "POST":
		roll = request.POST.get('roll')
		subject = request.POST.get('subject_picker')
		attendance = request.POST.get('attendance')
		total = request.POST.get('total')
		student = models.Student.objects.filter(
			roll_no=roll
		).first()
		duplicate_check = models.Attendance.objects.filter(
			student=student, subject=subject,
		).first()
		if duplicate_check:
			context_dict["message"] = 'Attendance already exist.'
			duplicate_check.soft_delete=False
			duplicate_check.save()
			return render(request, "addAttendance.html", context_dict)
		try:
			attendance_data = models.Attendance(
				student=student,
				subject=models.Subject.objects.get(pk=subject),
				total_attendance=total,
				obtained_attendance=attendance
			)
			attendance_data.save()
			history = models.History(
				user=emp,
				activity='Added attendance of ' + str(student) + 
					str(subject) +'.\n',
				activity_type="add attendance"
			)
			history.save()
			context_dict["message"] = 'Successfully added Attendance.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	return render(request, "addAttendance.html", context_dict)


@login_required
def edit_attendance(request, attendance_id):

	"""
	Edit attendance of students subject wise.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.student_permit:
		raise Http404
	attendance = models.Attendance.objects.filter(
		pk=attendance_id, soft_delete=False
	).first()
	print("1")
	context_dict = {
		"all_subjects": context_helper.subject_helper(),
		'attendance_id': attendance_id,
	}
	if request.method == 'POST':
		update_fields = []
		activity = ''
		roll = request.POST.get('roll')
		subject = request.POST.get('subject_picker')
		obtained = request.POST.get('attendance')
		total = request.POST.get('total')
		student = models.Student.objects.filter(
			roll_no=roll
		).first()
		if not student:
			context_dict["message"] = 'Student at does not exist / Roll number has not been alloted.'
			return render(request, "editAttendance.html", context_dict)
		try:
			if attendance.student != student:
				attendance.student = student
				update_fields.append('student')
				activity += 'Changed student to ' + str(student) + '.\n'
			if attendance.total_attendance != total:
				attendance.total_attendance = total
				update_fields.append('total_attendance')
				activity += 'Changed total attendance to ' + str(total) + '.\n'
			if attendance.obtained_attendance != obtained:
				attendance.obtained_attendance = obtained
				update_fields.append('obtained_attendance')
				activity += 'Changed obtained attendance to' + str(obtained) + '.\n'
			if str(attendance.subject.pk) != str(subject):
				attendance.subject = models.Subject.objects.get(pk=subject)
				update_fields.append('subject')
				activity += 'Changed subject to ' + str(subject) + '.\n'
			attendance.save(update_fields=update_fields)
			history = models.History(
				user=emp,
				activity=activity,
				activity_type="edit attendance"
			)
			history.save()
			context_dict["message"] = 'Successfully updated Attendance.'
			context_dict["success"] = True
		except Exception as e:
			context_dict["message"] = str(e)
			context_dict["success"] = False
			print(e)
	context_dict.update(context_helper.get_attendance_info(attendance))
	for i in context_dict['subjects']:
		# use for dynamic
		try: del context_dict['all_subjects'][i]
		except: pass
	if context_dict.get('success', False):
		return HttpResponseRedirect('/view-attendance')
	return render(
		request, "editAttendance.html", context_dict
	)


@login_required
def view_attendance(request):

	"""
	View attendance of students.
	"""

	context_dict = {
		'title': 'All Attendance',
	}
	return render(request, "viewAttendance.html", context_dict)


@login_required
def delete_attendance(request, attendance_id):

	"""
	Delete Result Main.
	"""

	emp = models.Teacher.objects.get(user=request.user)
	if not emp.student_permit:
		raise Http404
	attendance = models.Attendance.objects.filter(
		pk=attendance_id, soft_delete=False
	).first()
	if not attendance:
		raise Http404
	attendance.soft_delete = True
	activity = 'Deleted Attendance' + str(attendance) + '.\n'
	attendance.save(update_fields=['soft_delete'])
	history = models.History(
				user=emp,
				activity=activity,
				activity_type="delete attendance"
			)
	history.save()
	return HttpResponseRedirect('/view-attendance')
