from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.

class TimeStampModel(models.Model):

	""" 
	Abstract class for all models to store created, updated and
	deleted informarion (Time Manage).
	"""

	created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
	soft_delete = models.BooleanField(default=False)

	class Meta:
		abstract = True


class Person(TimeStampModel):

	"""
	Abstract class used for teachers and students basic information.
	"""

	BLOOD_TYPE = (
		('A+', 'A-Positive'),
		('A-', 'A-Negative'),
		('B+', 'B-Positive'),
		('B-', 'B-Negative'),
		('O+', 'O-Positive'),
		('O-', 'O-Negative'),
		('AB+', 'AB-Positive'),
		('AB-', 'AB-Negative'),
	)

	GENDER_TYPE = (
		('M', 'Male'),
		('F', 'Female'),
	)

	name = models.CharField(max_length=50, db_index=True)
	gender = models.CharField(max_length=2, null=False, choices=GENDER_TYPE, blank=True)
	dob = models.DateField(null=True, blank=True)
	phone = models.BigIntegerField()
	curr_address = models.TextField()
	perm_address = models.TextField(null=True)
	address_flag = models.BooleanField(default=False)
	photo = models.ImageField(upload_to='profile-images', null=True)
	blood_group = models.CharField(max_length=3, null=True, choices=BLOOD_TYPE, blank=True)

	class Meta:
		abstract = True


class Course(TimeStampModel):

	"""
	Course details.
	"""

	name = models.CharField(max_length=100, null=False, db_index=True, unique=True)
	abbr = models.CharField(max_length=20, db_index=True, unique=True)
	duration = models.IntegerField()

	def __str__(self):
		return str(self.name)

	def __unicode__(self):
		return unicode(self.name)


class ExamName(TimeStampModel):

	"""
	To define exam name like Semester or Trimester.
	"""

	name = models.CharField(max_length=20, null=False, unique=True)

	def __str__(self):
		return str(self.name)

	def __unicode__(self):
		return unicode(self.name)


class Student(Person):

	"""
	Student information model.
	"""

	GUARDIAN_TYPE = (
		('F', 'Father'),
		('M', 'Mother'),
		('G', 'Guradian')
	)

	roll_no = models.SlugField(unique=True)
	remarks = models.TextField(null = True)
	guardian_name = models.CharField(max_length=50)
	guardian_type = models.CharField(max_length=1, choices=GUARDIAN_TYPE)
	guardian_phone = models.CharField(max_length=15)
	course = models.ForeignKey(Course, db_index=True)
	batch = models.IntegerField()
	email = models.CharField(max_length=100, null=False, unique=True)

	def __str__(self):
		return str(str(self.roll_no) + '-' + self.name)

	def __unicode__(self):
		return unicode(str(self.roll_no) + '-' + self.name)


class Teacher(Person):

	"""
	Employee details and their rights to portal.
	"""

	user = models.ForeignKey(User)
	e_id = models.CharField(max_length=20, db_index=True, unique=True)
	student_permit = models.BooleanField(default=False)
	subject_permit = models.BooleanField(default=False)
	exam_permit = models.BooleanField(default=False)
	result_permit = models.BooleanField(default=False)

	def __str__(self):
		return str(self.e_id + '-' + self.name)

	def __unicode__(self):
		return unicode(self.e_id + '-' + self.name)


class Subject(TimeStampModel):

	"""
	Subjects Details.
	"""

	SUBJECT_TYPE = (
		('T', 'THEORY'),
		('P', 'PRACTICAL'),
	)
	course = models.ForeignKey(Course)
	name = models.CharField(max_length=50, blank=False)
	s_id = models.CharField(max_length=10, unique=True, blank=False)
	s_type = models.CharField(max_length=10,choices=SUBJECT_TYPE)
	max_marks = models.CharField(max_length=5)

	def __str__(self):
		return str(self.name + '-' + self.s_id)

	def __unicode__(self):
		return unicode(self.name + '-' + self.s_id)


class Result(TimeStampModel):

	"""
	Result Meta Data.
	"""

	RESULT_TYPE = (
		('I', 'INTERNAL'),
		('E', 'EXTERNAL'),
	)
	result_type = models.CharField(max_length=20, choices=RESULT_TYPE)
	batch = models.CharField(max_length=10)
	course = models.ForeignKey(Course)
	exam_name = models.ForeignKey(ExamName)
	subject = models.ForeignKey(Subject)

	def __str__(self):
		return str(self.result_type + '-' + self.batch + '-' + str(self.subject))

	def __unicode__(self):
		return unicode(self.result_type + '-' + self.batch + '-' + str(self.subject))


class ResultMain(TimeStampModel):

	"""
	Result set to be Displayed
	"""

	student = models.ForeignKey(Student)
	result = models.ForeignKey(Result)
	marks_obtained = models.IntegerField()

	def __str__(self):
		return str(str(self.student) + '-' + str(self.result))

	def __unicode__(self):
		return unicode(str(self.student) + '-' + str(self.result))

	class Meta:
		unique_together = ["student", "result",]


class Attendance(TimeStampModel):

	"""
	Attendance of students subject wise.
	"""

	student = models.ForeignKey(Student)
	subject = models.ForeignKey(Subject)
	total_attendance = models.IntegerField()
	obtained_attendance = models.IntegerField()

	def __str__(self):
		return str(str(self.student) + '-' + str(self.subject) + '-' + str(self.obtained_attendance))

	def __unicode__(self):
		return unicode(str(self.student) + '-' + str(self.subject) + '-' + str(self.obtained_attendance))

	class Meta:
		unique_together = ["student", "subject"]


class History(TimeStampModel):

	"""
	Record of changes that is made by the user.
	"""

	user = models.ForeignKey(Teacher)
	activity = models.TextField(null=True, blank=True)
	activity_type = models.CharField(max_length=50)

	def __str__(self):
		return str(str(self.user) + '-' + self.activity_type)

	def __unicode__(self):
		return unicode(str(self.user) + '-' + self.activity_type)


class PasswordReset(TimeStampModel):

	"""
	Password reset model.
	"""

	user = models.ForeignKey(Teacher)
	password_request_created_at = models.DateTimeField(auto_now_add=True)
	token = models.TextField()
	token_consumed = models.BooleanField(default=False)

	def __str__(self):
		return str(str(self.user) + '-' + str(self.token_consumed))

	def __unicode__(self):
		return str(str(self.user) + '-' + str(self.token_consumed))
