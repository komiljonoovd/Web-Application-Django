from django.contrib import admin
from .models import (
    Classes, Parents, Pupils, Teachers, ParentPupil)


@admin.register(Classes)
class ClassDepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'letter', 'isactive', 'teacher', 'createdon', 'modifiedon', 'createdby',
                    'modifiedby',
                    'isdeleted']

    list_display_links = ['id', 'number', 'letter']
    list_per_page = 30
    ordering = ['id']

@admin.register(Parents)
class ParentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'surname', 'phone',
                    'createdon', 'modifiedon',
                    'createdby',
                    'modifiedby', 'isdeleted', 'note']
    list_display_links = ['id', 'first_name', 'last_name', 'surname']
    list_per_page = 30
    ordering = ['id']


@admin.register(Pupils)
class PupilAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'surname', 'classes', 'gender', 'birthday',
                    'createdon',
                    'modifiedon', 'createdby', 'modifiedby', 'isdeleted', 'note']
    list_display_links = ['id', 'first_name', 'last_name', 'surname']
    list_per_page = 30
    ordering = ['id']
    list_select_related = ['classes']



@admin.register(Teachers)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'surname', 'createdon',
                    'modifiedon', 'createdby', 'modifiedby', 'isdeleted']
    list_display_links = ['id', 'first_name', 'last_name', 'surname']
    ordering = ['id']
    list_per_page = 30


@admin.register(ParentPupil)
class ParentPupilAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'pupil']
    list_display_links = ['id', 'parent', 'pupil']
    list_per_page = 30
    ordering = ['id']
