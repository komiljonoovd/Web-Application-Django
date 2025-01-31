from django import forms
from .models import Classes, Pupils, Parents, Teachers


class ClassForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['number', 'letter', 'isactive', 'teacher', 'isdeleted']


class PupilForm(forms.ModelForm):
    class Meta:
        model = Pupils
        fields = ['first_name', 'last_name', 'surname', 'gender', 'birthday', 'classes', 'isdeleted', 'note']


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parents
        fields = ['first_name', 'last_name', 'surname', 'phone', 'isdeleted', 'note']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teachers
        fields = ['first_name', 'last_name', 'surname', 'isdeleted']
