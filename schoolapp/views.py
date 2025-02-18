from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from schoolapp.models import Classes, ParentPupil
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Classes, Pupils, Teachers,Parents
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import ClassForm, PupilForm, ParentForm, TeacherForm


@login_required
def all_entities(request):
    return render(request, 'mainpage.html')


@login_required
def class_list(request):
    search_query = request.GET.get('search', '')
    rows_per_page = request.GET.get('rows_per_page', '20')

    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 20
    except ValueError:
        rows_per_page = 20

    classes = Classes.objects.all().order_by('-isactive', '-number', 'letter')
    if search_query:
        classes = classes.filter(
            number__iexact=search_query.capitalize()
        ) | classes.filter(
            letter__icontains=search_query.capitalize()
        ) | classes.filter(
            teacher__first_name__icontains=search_query.capitalize()
        ) | classes.filter(
            teacher__last_name__icontains=search_query.capitalize()
        ) | classes.filter(
            teacher__surname__icontains=search_query.capitalize()
        )
    # Пагинация
    paginator = Paginator(classes, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'rows_per_page': rows_per_page,
    }
    return render(request, 'classpage.html', context)


# @login_required
@csrf_exempt
def delete_classes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            if not ids:
                return JsonResponse({'status': 'error', 'message': 'No IDs provided'}, status=400)

            Classes.objects.filter(id__in=ids).delete()
            return JsonResponse({'status': 'success', 'message': 'Classes deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
def edit_class(request, pk):
    class_instance = get_object_or_404(Classes, id=pk)

    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_instance)

        if form.is_valid():
            number = form.cleaned_data['number']
            letter = form.cleaned_data['letter']
            error_messages = []

            if int(number) < 1 or int(number) > 11:
                error_messages.append('Классы существуют с 1-го до 11-го класса!')
            if Classes.objects.filter(number=number, letter=letter, isactive=True).exclude(pk=pk).exists():
                error_messages.append(f'Класс "{number}-{letter}" уже существует!')
            if letter not in ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й',
                              'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У',
                              'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э',
                              'Ю', 'Я']:
                error_messages.append('Буква должна быть написана в верхнем регистре кириллицы!')

            if error_messages:
                return JsonResponse({'success': False, 'errors': error_messages}, status=400)

            # Save changes if no errors
            class_instance = form.save(commit=False)
            class_instance.modifiedby = request.user.username
            class_instance.modifiedon = timezone.now()
            class_instance.save()
            return JsonResponse({'success': True, 'redirect_url': '/evika-school/classes/'})

        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = ClassForm(instance=class_instance)

    pupils_list = Pupils.objects.filter(classes=class_instance).order_by('first_name')

    page_number = request.GET.get('page', 1)
    rows_per_page = request.GET.get('rows_per_page', 10)
    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 10
    except ValueError:
        rows_per_page = 10

    paginator = Paginator(pupils_list, rows_per_page)
    page_obj = paginator.get_page(page_number)

    if not class_instance.modifiedby:
        modifiedby = 'Нет изменений'
        modifiedon = ''
    else:
        modifiedby = class_instance.modifiedby
        modifiedon = class_instance.modifiedon

    return render(request, 'classedit.html', {
        'form': form,
        'class_instance': class_instance,
        'created_by': class_instance.createdby,
        'created_on': class_instance.createdon,
        'modified_by': modifiedby,
        'modified_on': modifiedon,
        'pupils': page_obj,  # Pass paginated pupils to the template
        'page_obj': page_obj,  # Pass page object for pagination
        'rows_per_page': rows_per_page,  # Number of rows per page
    })


@login_required
def add_class(request):
    if request.method == 'POST':
        letters_list = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й',
                        'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
                        'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']
        form = ClassForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get('number')
            letter = form.cleaned_data.get('letter')

            error_messages = []

            if Classes.objects.filter(number=number, letter=letter, isactive=True).exists():
                error_messages.append(f'Класс "{number}-{letter}" уже существует! ')

            # Проверка на допустимый диапазон классов
            if int(number) < 1 or int(number) > 11:
                error_messages.append('Классы существуют с 1-го до 11-го класса! ')

            # Проверка на корректность буквы
            if letter not in letters_list:
                error_messages.append(f'Буква должна быть написана в верхнем регистре кириллицы!\n ')

            # Если есть ошибки, возвращаем их
            if error_messages:
                return JsonResponse({'success': False, 'errors': error_messages}, status=400)

            class_instance = form.save(commit=False)
            class_instance.createdby = request.user.username
            class_instance.save()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'errors': form.errors.as_text()}, status=400)

    form = ClassForm()
    return render(request, 'classadd.html', {'form': form})


@csrf_exempt
def delete_classes(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        getId = ids[0]
        ids.clear()
        for i in getId.split(','):
            ids.append(int(i))
        Classes.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Удаление прошло успешно.'})
    # return JsonResponse({'error': 'Нужно выбрать по одному.'}, status=400)


@csrf_exempt
def restore_classes(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            getId = ids[0]
            ids.clear()
            for i in getId.split(','):
                ids.append(int(i))
        except ValueError:
            return JsonResponse({'error': 'Некорректные идентификаторы классов.'}, status=400)

        Classes.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Восстановление прошло успешно.'})

    return JsonResponse({'error': 'Нужно выбрать хотя бы один класс.'}, status=400)


@csrf_exempt
def raise_number(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        getId = ids[0]
        ids.clear()
        for i in getId.split(','):
            ids.append(int(i))
        classes = Classes.objects.filter(id__in=ids)
        messages = []

        for cls in classes:
            if cls.number < 11:
                cls.number += 1
                cls.save()
                messages.append(f'Успешно поднят.')
            else:
                messages.append(f'Увеличить невозможно.')

        return JsonResponse({'messages': messages})

    return JsonResponse({'error': 'Неверный метод запроса.'}, status=400)


@csrf_exempt
def archive_classes(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        getId = ids[0]
        ids.clear()
        for i in getId.split(','):
            ids.append(int(i))
        Classes.objects.filter(id__in=ids).update(isactive=False)
        return JsonResponse({'message': 'Класс успешно архивирован.'})
    return JsonResponse({'error': 'Ошибка при архивировании классов.'}, status=400)


@csrf_exempt
def delete_class(request, class_id):
    if request.method == 'POST':
        Classes.objects.filter(id=class_id).update(isdeleted=True)
        return JsonResponse({'message': 'Класс успешно удалён.'})
    return JsonResponse({'error': 'Метод не разрешен.'}, status=405)


@csrf_exempt
def delete_pupils(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        print(ids)
        getId = ids[0]
        ids.clear()
        for i in getId.split(','):
            ids.append(int(i))
        Pupils.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'error': 'Ошибка при архивировании классов.'}, status=400)


@csrf_exempt
def restore_pupils(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        getId = ids[0]
        ids.clear()
        for i in getId.split(','):
            ids.append(int(i))
        Pupils.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Успешно восстановлено.'})
    return JsonResponse({'error': 'Ошибка при архивировании классов.'}, status=400)


@csrf_exempt
def unlink_pupils(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids]
        Pupils.objects.filter(id__in=ids).update(classes=None)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'error': 'Ошибка при архивировании классов.'}, status=400)


#
# def list_pupils_not_linked(request):
#     pupils = Pupils.objects.filter(classes__isnull=False, isdeleted=False).values('id', 'first_name', 'last_name',
#                                                                                   'surname')
#     return JsonResponse({'pupils': list(pupils)})


@login_required
def pupil_list(request):
    search_query = request.GET.get('search', '')
    rows_per_page = request.GET.get('rows_per_page', '20')

    # Преобразование rows_per_page в число
    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 20  # Возврат к значению по умолчанию, если введено некорректное значение
    except ValueError:
        rows_per_page = 20  # Если произошла ошибка, используем значение по умолчанию

    # Фильтрация классов по поисковому запросу
    pupils = Pupils.objects.select_related('classes').order_by('isdeleted', 'first_name')
    if search_query:
        pupils = pupils.filter(
            first_name__icontains=search_query.capitalize()
        ) | pupils.filter(
            last_name__icontains=search_query.capitalize()
        ) | pupils.filter(
            surname__icontains=search_query.capitalize()
        ) | pupils.filter(
            gender__icontains=search_query.capitalize()
        ) | pupils.filter(
            birthday__icontains=search_query
        ) | pupils.filter(
            classes__number__icontains=search_query
        ) | pupils.filter(
            classes__letter__icontains=search_query.capitalize()
        )

    paginator = Paginator(pupils, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'rows_per_page': rows_per_page,
    }
    return render(request, 'pupilpage.html', context)


@csrf_exempt
def delete_pupils_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Pupils.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'message': 'Ошибка при удалении учеников или учениц.'})


@csrf_exempt
def restore_pupils_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        Pupils.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Успешно восстановлено.'})
    return JsonResponse({'message': 'Ошибка при восстановлении.'})


@csrf_exempt
def restore_parents_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Parents.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Успешно восстановлено.'})
    return JsonResponse({'message': 'Ошибка при восстановлениий.'})


@csrf_exempt
def delete_parents_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Parents.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'message': 'Ошибка при удалении.'})


@login_required
def parent_list(request):
    search_query = request.GET.get('search', '')
    rows_per_page = request.GET.get('rows_per_page', '20')

    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 20
    except ValueError:
        rows_per_page = 20

    parents = Parents.objects.all().order_by('first_name')
    if search_query:
        parents = parents.filter(
            first_name__icontains=search_query.capitalize()
        ) | parents.filter(
            last_name__icontains=search_query.capitalize()
        ) | parents.filter(
            surname__icontains=search_query.capitalize()
        ) | parents.filter(
            phone__icontains=search_query.capitalize()
        )

    # Пагинация
    paginator = Paginator(parents, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'rows_per_page': rows_per_page,
    }
    return render(request, 'parentspage.html', context)


@login_required
def teachers_list(request):
    search_query = request.GET.get('search', '')
    rows_per_page = request.GET.get('rows_per_page', '20')

    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 20
    except ValueError:
        rows_per_page = 20

    teachers = Teachers.objects.all().order_by('first_name')
    if search_query:
        search_query = search_query.capitalize()
        teachers = teachers.filter(
            first_name__icontains=search_query
        ) | teachers.filter(
            last_name__icontains=search_query
        ) | teachers.filter(
            surname__icontains=search_query
        )

    paginator = Paginator(teachers, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'rows_per_page': rows_per_page,
    }
    return render(request, 'teacherspage.html', context)


@csrf_exempt
def restore_teachers_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Teachers.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Успешно восстановлено.'})
    return JsonResponse({'message': 'Ошибка при восстановлении Родителей.'})


@csrf_exempt
def delete_teachers_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Teachers.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'message': 'Ошибка при удалении Родителей.'})







@csrf_exempt
def not_linked_pupils(request):
    page = int(request.GET.get('page', 1))
    rows_per_page = int(request.GET.get('rows_per_page', 10))
    search_query = request.GET.get('search', '').strip()

    pupil = Pupils.objects.filter(classes__isnull=True, isdeleted=False).order_by('last_name')

    if search_query:
        pupil = pupil.filter(first_name__icontains=search_query.capitalize()
                                                | pupil.filter(last_name__icontains=search_query.capitalize())
                                                | pupil.filter(surname__icontains=search_query.capitalize())
                             )

    paginator = Paginator(pupil, rows_per_page)
    paginated_pupils = paginator.get_page(page)

    data = {
        'pupils': [
            {
                'id': pupil.id,
                'first_name': pupil.first_name,
                'last_name': pupil.last_name,
                'surname': pupil.surname,
            }
            for pupil in paginated_pupils
        ],
        'pagination': {
            'num_pages': paginator.num_pages,
            'current_page': paginated_pupils.number,
        }
    }

    return JsonResponse(data)


@csrf_exempt
def link_pupils(request, class_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        pupil_ids = data.get('ids', [])
        Pupils.objects.filter(id__in=pupil_ids).update(classes=class_id)
        print(pupil_ids)
        print(class_id)

        return JsonResponse({'success': 'Привязано успешно.'})
    return JsonResponse({'success': 'Ошибка при привязании.'})


def auth_check(request):
    is_authenticated = request.user.is_authenticated
    print(is_authenticated)
    return JsonResponse({'is_authenticated': is_authenticated})


@login_required
def add_pupil(request):
    if request.method == 'POST':
        print(request.method)
        form = PupilForm(request.POST)
        if form.is_valid():
            pupil = form.save(commit=False)
            pupil.createdby = request.user.username
            pupil.save()
            return JsonResponse({'message': 'Успешно добавлено !'}, status=200)
        # Возврат ошибок в формате ключ-значение
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

    # Используем только нужные поля для повышения производительности
    classes = Classes.objects.filter(isdeleted=False, isactive=True).only('id', 'number', 'letter', 'teacher')

    # Формируем список выбора для поля классов
    class_choices = [
        (
            cls.id,
            f"{cls.number}-{cls.letter}  {cls.teacher.last_name} {cls.teacher.first_name}"
            if cls.teacher else f"{cls.number}-{cls.letter}"
        )
        for cls in classes
    ]

    form = PupilForm()
    form.fields['classes'].choices = class_choices

    # Возвращаем форму для отображения на фронтенде
    return render(request, 'pupiladd.html', {'form': form})


@login_required
def add_parent(request):
    if request.method == 'POST':
        print(request.method)
        form = ParentForm(request.POST)
        if form.is_valid():
            parent = form.save(commit=False)
            parent.createdby = request.user.username
            parent.save()
            return JsonResponse({'message': 'Успешно добавлено !'}, status=200)
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

    form = ParentForm()
    return render(request, 'parentadd.html', {'form': form})


@login_required
def add_teacher(request):
    if request.method == 'POST':
        print(request.method)
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.createdby = request.user.username
            teacher.save()
            return JsonResponse({'message': 'Успешно добавлено !'}, status=200)
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

    form = TeacherForm()
    return render(request, 'teacheradd.html', {'form': form})


@login_required
def edit_pupils(request, pk):
    pupils = get_object_or_404(Pupils, id=pk)

    if request.method == 'POST':
        form = PupilForm(request.POST, instance=pupils)
        if form.is_valid():
            # Save changes if no errors
            pupils = form.save(commit=False)
            pupils.modifiedby = request.user.username
            pupils.modifiedon = timezone.now()
            pupils.save()
            return JsonResponse({'success': True, 'redirect_url': '/evika-school/pupils/'})

        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = PupilForm(instance=pupils)

    # Формирование списка классов для выбора
    classes = Classes.objects.filter(isdeleted=False, isactive=True).only('id', 'number', 'letter', 'teacher')
    class_choices = [
        (
            cls.id,
            f"{cls.number}-{cls.letter}  {cls.teacher.last_name} {cls.teacher.first_name}"
            if cls.teacher else f"{cls.number}-{cls.letter}"
        )
        for cls in classes
    ]
    form.fields['classes'].choices = class_choices

    # Пагинация списка родителей
    parent_list = ParentPupil.objects.filter(pupil=pk).values('parent__id', 'parent__first_name', 'parent__last_name',
                                                              'parent__surname', 'parent__phone').order_by('parent__last_name')

    page_number = request.GET.get('page', 1)
    rows_per_page = request.GET.get('rows_per_page', 10)
    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 10
    except ValueError:
        rows_per_page = 10

    paginator = Paginator(parent_list, rows_per_page)
    try:
        page_obj = paginator.get_page(page_number)
    except ValueError:
        page_obj = paginator.get_page(paginator.num_pages)

    # Формирование данных о последних изменениях
    if not pupils.modifiedby:
        modifiedby = 'Нет изменений'
        modifiedon = ''
    else:
        modifiedby = pupils.modifiedby
        modifiedon = pupils.modifiedon

    return render(request, 'pupiledit.html', {
        'form': form,
        'pupils_instance': pupils,
        'created_by': pupils.createdby,
        'created_on': pupils.createdon,
        'modified_by': modifiedby,
        'modified_on': modifiedon,
        'pupils': page_obj,
        'page_obj': page_obj,
        'rows_per_page': rows_per_page,
    })


#
@login_required
def edit_parents(request, pk):
    parents = get_object_or_404(Parents, id=pk)

    if request.method == 'POST':
        form = ParentForm(request.POST, instance=parents)
        print(form)

        if form.is_valid():
            # Save changes if no errors
            pupils = form.save(commit=False)
            pupils.modifiedby = request.user.username
            pupils.modifiedon = timezone.now()
            pupils.save()
            return JsonResponse({'success': True, 'redirect_url': '/evika-school/classes/'})

        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = ParentForm(instance=parents)

    pupil_list = ParentPupil.objects.filter(parent=pk).values(
        'pupil__id',
        'pupil__first_name',
        'pupil__last_name',
        'pupil__surname',
        'pupil__gender',
        'pupil__birthday',
        'pupil__classes__number',
        'pupil__classes__letter',
        'pupil__classes__teacher__first_name',
        'pupil__classes__teacher__last_name',
        'pupil__classes__teacher__surname'
    ).order_by('pupil__first_name')

    page_number = request.GET.get('page', 1)
    rows_per_page = request.GET.get('rows_per_page', 10)
    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 10
    except ValueError:
        rows_per_page = 10

    paginator = Paginator(pupil_list, rows_per_page)
    page_obj = paginator.get_page(page_number)

    if not parents.modifiedby:
        modifiedby = 'Нет изменений'
        modifiedon = ''
    else:
        modifiedby = parents.modifiedby
        modifiedon = parents.modifiedon

    # classes = Classes.objects.filter(isdeleted=False, isactive=True).only('id', 'number', 'letter', 'teacher')
    #
    # # Формируем список выбора для поля классов
    # class_choices = [
    #     (
    #         cls.id,
    #         f"{cls.number}-{cls.letter}  {cls.teacher.last_name} {cls.teacher.first_name}"
    #         if cls.teacher else f"{cls.number}-{cls.letter}"
    #     )
    #     for cls in classes
    # ]
    #
    # form = PupilForm()
    # form.fields['classes'].choices = class_choices

    return render(request, 'parentedit.html', {
        'form': form,
        'pupils_instance': parents,
        'created_by': parents.createdby,
        'created_on': parents.createdon,
        'modified_by': modifiedby,
        'modified_on': modifiedon,
        'pupils': page_obj,
        'page_obj': page_obj,
        'rows_per_page': rows_per_page,
    })


@login_required
def edit_teachers(request, pk):
    teacher = get_object_or_404(Teachers, id=pk)

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        print(form)

        if form.is_valid():
            pupils = form.save(commit=False)
            pupils.modifiedby = request.user.username
            pupils.modifiedon = timezone.now()
            pupils.save()
            return JsonResponse({'success': True, 'redirect_url': '/evika-school/classes/'})

        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = TeacherForm(instance=teacher)

    classes_list = Classes.objects.filter(teacher=pk).order_by('-number', '-isactive').values('id', 'number', 'letter',
                                                                                             'isactive').order_by('-number')

    page_number = request.GET.get('page', 1)
    rows_per_page = request.GET.get('rows_per_page', 10)
    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 10
    except ValueError:
        rows_per_page = 10

    paginator = Paginator(classes_list, rows_per_page)
    page_obj = paginator.get_page(page_number)

    if not teacher.modifiedby:
        modifiedby = 'Нет изменений'
        modifiedon = ''
    else:
        modifiedby = teacher.modifiedby
        modifiedon = teacher.modifiedon

    return render(request, 'teacheredit.html', {
        'form': form,
        'pupils_instance': teacher,
        'created_by': teacher.createdby,
        'created_on': teacher.createdon,
        'modified_by': modifiedby,
        'modified_on': modifiedon,
        'pupils': page_obj,
        'page_obj': page_obj,
        'rows_per_page': rows_per_page,
    })

#
# @csrf_exempt
# def not_linked_classes(request):
#     page = int(request.GET.get('page', 1))
#     rows_per_page = int(request.GET.get('rows_per_page', 10))
#     search_query = request.GET.get('search', '').strip()
#
#     cls = Classes.objects.filter(teacher__isnull=True,isactive=True,isdeleted=False).order_by('-number')
#
#     if search_query:
#         cls = Classes.filter(first_name__icontains=search_query.capitalize()
#                                                    | cls.filter(last_name__icontains=search_query.capitalize())
#                                                    | cls.filter(surname__icontains=search_query.capitalize())
#                              )
#
#     paginator = Paginator(cls, rows_per_page)
#     paginated_pupils = paginator.get_page(page)
#
#     data = {
#         'cls': [
#             {
#                 'id': cls.id,
#                 'number': cls.number,
#                 'letter': cls.letter,
#             }
#             for cls in paginated_pupils
#         ],
#         'pagination': {
#             'num_pages': paginator.num_pages,
#             'current_page': paginated_pupils.number,
#         }
#     }
#
#     return JsonResponse(data)

@csrf_exempt
def not_linked_classes(request):
    page = int(request.GET.get('page', 1))
    rows_per_page = int(request.GET.get('rows_per_page', 10))
    search_query = request.GET.get('search', '').strip()

    pupil = Classes.objects.filter(teacher__isnull=True,isactive=True,isdeleted=False).order_by('-number')

    if search_query:
        try:
            search_number = int(search_query)
            pupil = pupil.filter(number__iexact=search_number)
        except ValueError:
            pupil = pupil.filter(letter__iexact=search_query.capitalize())

    paginator = Paginator(pupil, rows_per_page)
    paginated_pupils = paginator.get_page(page)

    data = {
        'pupils': [
            {
                'id': pupil.id,
                'number': pupil.number,
                'letter': pupil.letter,
            }
            for pupil in paginated_pupils
        ],
        'pagination': {
            'num_pages': paginator.num_pages,
            'current_page': paginated_pupils.number,
        }
    }

    return JsonResponse(data)


@csrf_exempt
def unlink_classes(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids]
        Classes.objects.filter(id__in=ids).update(teacher=None)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'error': 'Ошибка при архивировании классов.'}, status=400)


@csrf_exempt
def link_classes(request,teacher_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        pupil_ids = data.get('ids', [])
        Classes.objects.filter(id__in=pupil_ids).update(teacher=teacher_id)
        print(pupil_ids)
        print(teacher_id)

        return JsonResponse({'success': 'Привязано успешно.'})
    return JsonResponse({'success': 'Ошибка при привязании.'})


@csrf_exempt
def not_linked_child(request,parent_id):
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        rows_per_page = int(request.GET.get('rows_per_page', 10))
        search_query = request.GET.get('search', '').strip()

        exclude_pupils=ParentPupil.objects.filter(parent=parent_id).values('pupil')
        not_linked = Pupils.objects.filter(isdeleted=False).exclude(id__in=exclude_pupils).order_by('last_name')

        if search_query:
            not_linked = not_linked.filter(first_name__icontains=search_query.capitalize()
                                                       | not_linked.filter(last_name__icontains=search_query.capitalize())
                                                       | not_linked.filter(surname__icontains=search_query.capitalize())
                                 )

        paginator = Paginator(not_linked, rows_per_page)
        paginated_pupils = paginator.get_page(page)

        data = {
            'pupils': [
                {
                    'id': pupil.id,
                    'first_name': pupil.first_name,
                    'last_name': pupil.last_name,
                    'surname': pupil.surname,
                }
                for pupil in paginated_pupils
            ],
            'pagination': {
                'num_pages': paginator.num_pages,
                'current_page': paginated_pupils.number,
            }
        }

        return JsonResponse(data)



@csrf_exempt
def not_linked_parent(request,child_id):
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        rows_per_page = int(request.GET.get('rows_per_page', 10))
        search_query = request.GET.get('search', '').strip()

        exclude_parents=ParentPupil.objects.filter(pupil=child_id).values('parent')
        not_linked = Parents.objects.filter(isdeleted=False).exclude(id__in=exclude_parents).order_by('first_name')

        if search_query:
            not_linked = not_linked.filter(first_name__icontains=search_query.capitalize()
                                                       | not_linked.filter(last_name__icontains=search_query.capitalize())
                                                       | not_linked.filter(surname__icontains=search_query.capitalize())

                                           )
        paginator = Paginator(not_linked, rows_per_page)
        paginated_pupils = paginator.get_page(page)

        data = {
            'pupils': [
                {
                    'id': pupil.id,
                    'first_name': pupil.first_name,
                    'last_name': pupil.last_name,
                    'surname': pupil.surname,
                }
                for pupil in paginated_pupils
            ],
            'pagination': {
                'num_pages': paginator.num_pages,
                'current_page': paginated_pupils.number,
            }
        }

        return JsonResponse(data)


@csrf_exempt
def link_parents(request,child_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        parent_ids = data.get('ids', [])
        parent_ids=[int(parent) for parent in parent_ids]
        print(parent_ids)

        child = Pupils.objects.get(pk=child_id)
        for parent in parent_ids:
            parent = Parents.objects.get(pk=parent)
            ParentPupil.objects.create(parent=parent,pupil=child)

        return JsonResponse({'success': 'Привязано успешно.'})
    return JsonResponse({'success': 'Ошибка при привязании.'})


@csrf_exempt
def link_childs(request, parent_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        child_ids = data.get('ids', [])
        child_ids=[int(childs) for childs in child_ids]

        parent = Parents.objects.get(id=parent_id)
        for child_id in child_ids:
            child = Pupils.objects.get(id=child_id)
            ParentPupil.objects.create(pupil=child, parent=parent)

        return JsonResponse({'success': 'Привязано успешно.'})
    return JsonResponse({'success': 'Ошибка при привязании.'})

@csrf_exempt
def unlink_childs(request, parent_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        child_ids = data.get('ids', [])
        child_ids = [int(childs) for childs in child_ids]

        parent = Parents.objects.get(id=parent_id)
        ParentPupil.objects.filter(parent=parent, pupil__in=child_ids).delete()

        return JsonResponse({'success': 'Успешно отвязано.'})
    return JsonResponse({'success': 'Ошибка при отвязывании.'})

@csrf_exempt
def unlink_parents(request, child_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        parent_ids = data.get('ids', [])
        parent_ids = [int(parent) for parent in parent_ids]

        child = Pupils.objects.get(id=child_id)
        ParentPupil.objects.filter(pupil=child, parent__in=parent_ids).delete()

        return JsonResponse({'success': 'Успешно отвязано.'})
    return JsonResponse({'success': 'Ошибка при отвязывании.'})


@csrf_exempt
def delete_pupil(request, pupil_id):
    if request.method == 'POST':
        Pupils.objects.filter(id=pupil_id).update(isdeleted=True)
        return JsonResponse({'message': 'Класс успешно удалён.'})
    return JsonResponse({'error': 'Метод не разрешен.'}, status=405)


@csrf_exempt
def delete_parent(request, parent_id):
    if request.method == 'POST':
        Parents.objects.filter(id=parent_id).update(isdeleted=True)
        return JsonResponse({'message': 'Класс успешно удалён.'})
    return JsonResponse({'error': 'Метод не разрешен.'}, status=405)


@csrf_exempt
def delete_teacher(request, teacher_id):
    if request.method == 'POST':
        Teachers.objects.filter(id=teacher_id).update(isdeleted=True)
        return JsonResponse({'message': 'Класс успешно удалён.'})
    return JsonResponse({'error': 'Метод не разрешен.'}, status=405)