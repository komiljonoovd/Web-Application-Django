from django import forms
from .models import Classes


class ClassForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['number', 'letter', 'isactive', 'teacher', 'isdeleted']
