from django.urls import path, include
from .views import (all_entities, class_list,
                    edit_class, add_class,
                    delete_classes, restore_classes,
                    raise_number, archive_classes, delete_class,
                    restore_pupils, delete_pupils, unlink_pupils,
                    pupil_list, delete_pupils_list, restore_pupils_list,
                    parent_list, delete_parents_list, restore_parents_list,
                    teachers_list, delete_teachers_list, restore_teachers_list,
                    payment_list, delete_payment_list, restore_payment_list,
                    gender_list, restore_gender_list, delete_gender_list,
                    not_linked_pupils, link_pupils
                    )

urlpatterns = [
    path('', all_entities, name='main-page'),

    path('classes/', class_list, name='class_list'),
    path('edit-class/<int:pk>/', edit_class, name='edit_class'),
    path('delete-class/<int:class_id>/', delete_class, name='delete_class'),
    path('add-class/', add_class, name='add_class'),
    path('delete-classes/', delete_classes, name='delete_classes'),
    path('restore-classes/', restore_classes, name='restore_classes'),
    path('raise-number/', raise_number, name='raise_number'),
    path('archive-classes/', archive_classes, name='archive_classes'),

    path('restore-pupils/', restore_pupils, name='restore_pupils'),
    path('delete-pupils/', delete_pupils, name='delete_pupils'),
    path('unlink-pupils/', unlink_pupils, name='unlink_pupils'),
    path('link-pupils/', link_pupils, name='link-pupils'),
    path('not-linked-pupils/', not_linked_pupils, name='not-linked-pupils'),

    path('pupils/', pupil_list, name='pupils-list'),
    path('delete-pupils', delete_pupils_list, name='delete-pupils-list'),
    path('restore-pupils', restore_pupils_list, name='restore-pupils-list'),

    path('parents/', parent_list, name='parent-list'),
    path('delete-parents/', delete_parents_list, name='delete-parents-list'),
    path('restore-parents/', restore_parents_list, name='restore-parents-list'),

    path('teachers/', teachers_list, name='parent-list'),
    path('delete-teachers/', delete_teachers_list, name='delete_teachers_list'),
    path('restore-teachers/', restore_teachers_list, name='restore_teachers_list'),

    path('payment-type/', payment_list, name='payment-list'),
    path('restore-payment/', delete_payment_list, name='delete_payment-list'),
    path('delete-payment/', restore_payment_list, name='restore-payment-list'),

    path('gender/', gender_list, name='gender-list'),
    path('restore-gender/', restore_gender_list, name='restore_gender_list'),
    path('delete-gender/', delete_gender_list, name='delete-gender-list'),

]
