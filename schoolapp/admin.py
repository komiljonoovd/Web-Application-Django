from django.contrib import admin
from .models import (
    Classes, Gender,
    Payment, Parents, Pupils, Teachers, ParentPupil)


@admin.register(Classes)
class ClassDepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'letter', 'isactive', 'teacher', 'createdon', 'modifiedon', 'createdby',
                    'modifiedby',
                    'isdeleted']

    # list_display_links = ['id', 'number', 'letter', 'teacher', 'createdby', 'modifiedby']
    # search_fields = ['id', 'number', 'letter', ]
    # list_per_page = 5
    ordering = ['id']


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'createdon',
                    'modifiedon', 'createdby', 'modifiedby','isdeleted']

    # list_display_links = ['id', 'type']
    # search_fields = ['id', 'type']
    ordering = ['id']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'createdon',
                    'modifiedon', 'createdby', 'modifiedby','isdeleted']
    # list_display_links = ['id', 'cardname']
    # search_fields = ['id', 'cardname']
    # list_per_page = 5
    ordering = ['id']


@admin.register(Parents)
class ParentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'surname', 'phone',

                    'createdon', 'modifiedon',
                    'createdby',
                    'modifiedby', 'isdeleted', 'note']
    # list_display_links = ['id','first_name']
    # search_fields = ['id', 'cardname']
    ordering = ['id']


@admin.register(Pupils)
class PupilAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'surname','classes', 'gender', 'birthday',
                    'createdon',
                    'modifiedon', 'createdby', 'modifiedby', 'isdeleted', 'note']

    ordering = ['id']


@admin.register(Teachers)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'surname', 'createdon',
                    'modifiedon', 'createdby', 'modifiedby', 'isdeleted']

    ordering = ['id']


@admin.register(ParentPupil)
class ParentPupilAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'pupil']

    ordering = ['id']

