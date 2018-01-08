import json
from django import forms
from .models import *

class RegStudentResult(forms.ModelForm):

	tbatch = {}
	list_roll = []
	for student in Student.objects.all():
		if student.batch in tbatch:
			tbatch[student.batch].append(student.roll_no)
		else:
			tbatch[student.batch] = [student.roll_no]
		list_roll.append((student.roll_no,student.roll_no))

	batches = [str(batch) for batch in Student.objects.all()]

	batch_select = forms.ChoiceField(choices=([(batch,batch) for batch in batches]))
	roll_select = forms.ChoiceField(choices=(list_roll))

	batches = json.dumps(batches)
	rolls = json.dumps(tbatch)

	class Meta:
		model = Student
		fields = ('name',)