from django.urls import path
from schoolapp import views

urlpatterns = [
    path('', views.all_entities, name='main-page'),

    path('classes/', views.class_list, name='class_list'),
    path('edit-class/<int:pk>/', views.edit_class, name='edit_class'),
    path('delete-class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('add-class/', views.add_class, name='add_class'),
    path('delete-classes/', views.delete_classes, name='delete_classes'),
    path('restore-classes/', views.restore_classes, name='restore_classes'),
    path('raise-number/', views.raise_number, name='raise_number'),
    path('archive-classes/',views.archive_classes, name='archive_classes'),
    path('not-linked-classes/',views.not_linked_classes,name='not-linked-classes'),
    path('unlink-classes/',views.unlink_classes,name = 'unlink-classes'),
    path('link-classes/<int:teacher_id>/',views.link_classes,name='link-classes'),

    path('restore-pupils/', views.restore_pupils, name='restore_pupils'),
    path('delete-pupils/', views.delete_pupils, name='delete_pupils'),
    path('unlink-pupils/', views.unlink_pupils, name='unlink_pupils'),
    path('link-pupils/<int:class_id>/', views.link_pupils, name='link-pupils'),
    path('not-linked-pupils/', views.not_linked_pupils, name='not-linked-pupils'),
    path('link-child/<int:parent_id>/',views.link_childs,name='link-childs'),

    path('add-pupil/', views.add_pupil, name='add_pupil'),
    path('pupils/', views.pupil_list, name='pupils-list'),
    path('edit-pupil/<int:pk>/', views.edit_pupils, name='edit_pupils'),
    path('delete-pupils/', views.delete_pupils_list, name='delete-pupils-list'),
    path('restore-pupils', views.restore_pupils_list, name='restore-pupils-list'),
    path('not-linked-child/<int:parent_id>/',views.not_linked_child,name='not-linked-child'),
    path('unlink-childs/<int:parent_id>/',views.unlink_childs,name='unlink-childs'),

    path('parents/', views.parent_list, name='parent-list'),
    path('edit-parent/<int:pk>/',views.edit_parents,name='edit_parent'),
    path('add-parent/', views.add_parent, name='add_parent'),
    path('delete-parents/', views.delete_parents_list, name='delete-parents-list'),
    path('restore-parents/', views.restore_parents_list, name='restore-parents-list'),
    path('not-linked-parents/<int:child_id>/',views.not_linked_parent,name='not-linked-parents'),
    path('link-parents/<int:child_id>/',views.link_parents,name='link-parents'),
    path('unlink-parents/<int:child_id>/',views.unlink_parents,name='unlink-parents'),

    path('teachers/', views.teachers_list, name='parent-list'),
    path('edit-teacher/<int:pk>/',views.edit_teachers,name='edit_teacher'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('delete-teachers/', views.delete_teachers_list, name='delete_teachers_list'),
    path('restore-teachers/', views.restore_teachers_list, name='restore_teachers_list'),





]
