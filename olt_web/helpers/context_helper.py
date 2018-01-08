import os
from olt_web import models
from django.conf import settings


def course_helper():
	courses = models.Course.objects.filter(soft_delete=False)
	return {i.pk: i.name for i in courses}


def exam_name_helper():
	exam_name = models.ExamName.objects.filter(soft_delete=False)
	return {i.pk: i.name for i in exam_name}


def subject_helper():
	subjects = models.Subject.objects.filter(soft_delete=False)
	return {i.pk: i.name for i in subjects}


def blood_group_helper():
	blood_groups = [
		('A+', 'A-Positive'),
		('A-', 'A-Negative'),
		('B+', 'B-Positive'),
		('B-', 'B-Negative'),
		('O+', 'O-Positive'),
		('O-', 'O-Negative'),
		('AB+', 'AB-Positive'),
		('AB-', 'AB-Negative'),
	]
	return blood_groups


def guardian_type_helper():
	guardian_type = [
		('F', 'Father'),
		('M', 'Mother'),
		('G', 'Guradian'),
	]
	return guardian_type


def result_type_helper():
	result_type = [
		('I', 'INTERNAL'),
		('E', 'EXTERNAL'),
	]
	return result_type


def subject_type_helper():
	subject_type = [
		('T', 'THEORY'),
		('P', 'PRACTICAL'),
	]
	return subject_type


def gender_helper():
	gender_type =[
		('M', 'Male'),
		('F', 'Female'),
	]
	return gender_type


def get_student_info(student):

	blood_groups = blood_group_helper()
	guardians = guardian_type_helper()
	genders = gender_helper()
	info = {
		'sname': student.name,
		'curradd': student.curr_address,
		'permadd': student.perm_address,
		'roll': student.roll_no,
		'gender_type': [i for i in genders if student.gender in i],
		'course': {student.course.pk: student.course.name},
		'phone': student.phone,
		'gname': student.guardian_name,
		'guardian_phone': student.guardian_phone,
		'batch': student.batch,
		'email': student.email,
		'blood_group': [i for i in blood_groups if student.blood_group in i],
		'dob': student.dob,
		'guardian_type': [i for i in guardians if student.guardian_type in i],
		'address_flag': student.address_flag,
		'photo': os.path.join(settings.MEDIA_URL, student.photo.name) if student.photo else None,
	}
	return info


#For editing Result Meta Data
def get_result_info(result_data):

	exam = exam_name_helper()
	result_type = result_type_helper()
	course = course_helper()
	subject = subject_helper()
	info = {
		'batch': result_data.batch,
		'courses': {result_data.course.pk: result_data.course.name},
		'exams': {result_data.exam_name.pk: result_data.exam_name.name},
		'result_type': [i for i in result_type if result_data.result_type in i],
		'subjects': {result_data.subject.pk: result_data.subject.name},
	}
	return info


def get_emp_info(employee):
	
	blood_groups = blood_group_helper()
	genders = gender_helper()
	info = {
		'ename': employee.name,
		'dob': employee.dob,
		'gender': [i for i in genders if employee.gender in i],
		'phone': employee.phone,
		'address': employee.curr_address,
		'emp_id': employee.e_id,
		'bgroup': [i for i in blood_groups if employee.blood_group in i],
		'photo': os.path.join(settings.MEDIA_URL, employee.photo.name) if employee.photo else None,
	}
	return info
	

def get_exam_info(exam):

	info = {
		'name': exam.name
	}
	return info


def get_subject_info(subject):

	course = course_helper()
	subject_type = subject_type_helper()
	info = {
		'courses': {subject.course.pk: subject.course.name},
		'subject_type': [i for i in subject_type if subject.s_type in i],
		'name': subject.name,
		'id': subject.s_id,
		'mmarks': subject.max_marks,
	}
	return info
	

def get_resultMain_info(result_main):

	result_types = result_type_helper()
	subject = subject_helper()
	exam = exam_name_helper()
	info = {
		'student': result_main.student.roll_no,
		'exams': {result_main.result.exam_name.pk: result_main.result.exam_name.name},
		'result_type': [i for i in result_types if result_main.result.result_type in i],
		'subjects': {result_main.result.subject.pk: result_main.result.subject.name},
		'marks_obtained': result_main.marks_obtained,
	}
	return info


def get_attendance_info(attendance):

	subject = subject_helper()
	info = {
		'student': attendance.student.roll_no,
		'subjects': {attendance.subject.pk: attendance.subject.name},
		'total': attendance.total_attendance,
		'obtained': attendance.obtained_attendance,
	}
	return info
