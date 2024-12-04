from django.template.loader import render_to_string
from django.utils import timezone

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
# Create your views here.


from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from schoolapp.models import Classes
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Classes, Pupils, Teachers, Gender, Payment, Parents
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from .forms import ClassForm


@login_required
def LoginView(request):
    return render(request, 'login.html')


def all_entities(request):
    return render(request, 'mainpage.html')


def class_list(request):
    search_query = request.GET.get('search', '')
    rows_per_page = request.GET.get('rows_per_page', '20')

    # Преобразование rows_per_page в число
    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 20
    except ValueError:
        rows_per_page = 20

    classes = Classes.objects.all().order_by('-number', 'letter')
    if search_query:
        classes = classes.filter(
            number__icontains=search_query.capitalize()
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


from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone


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
            if Classes.objects.filter(number=number, letter=letter).exclude(pk=pk).exists():
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

    pupils_list = Pupils.objects.filter(classes=class_instance).order_by('id')

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


def add_class(request, pk=None):
    if request.method == 'POST':
        letters_list = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й',
                        'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
                        'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']
        form = ClassForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data.get('number')
            letter = form.cleaned_data.get('letter')

            error_messages = []

            if Classes.objects.filter(number=number, letter=letter).exclude(pk=pk).exists():
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
        try:
            class_instance = Classes.objects.get(id=class_id)
            class_instance.isdeleted = True
            class_instance.save()
            return JsonResponse({'message': 'Класс успешно удалён.'})
        except Classes.DoesNotExist:
            return JsonResponse({'error': 'Класс не найден.'}, status=404)
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


def list_pupils_not_linked(request):
    pupils = Pupils.objects.filter(classes__isnull=False, isdeleted=False).values('id', 'first_name', 'last_name')
    return JsonResponse({'pupils': list(pupils)})


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
    pupils = Pupils.objects.all().order_by('isdeleted', 'first_name')
    if search_query:
        pupils = pupils.filter(
            first_name__icontains=search_query.capitalize()
        ) | pupils.filter(
            last_name__icontains=search_query.capitalize()
        ) | pupils.filter(
            surname__icontains=search_query.capitalize()
        ) | pupils.filter(
            gender__type__icontains=search_query.capitalize()
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
    return JsonResponse({'message': 'Ошибка при восстановлении учеников или учениц.'})


@csrf_exempt
def restore_parents_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Parents.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Успешно восстановлено.'})
    return JsonResponse({'message': 'Ошибка при восстановлении Родителей.'})


@csrf_exempt
def delete_parents_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Parents.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'message': 'Ошибка при удалении Родителей.'})


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


def payment_list(request):
    search_query = request.GET.get('search', '')
    rows_per_page = request.GET.get('rows_per_page', '20')

    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 20
    except ValueError:
        rows_per_page = 20

    payment = Payment.objects.all().order_by('type')
    if search_query:
        payment = payment.filter(type__icontains=search_query.capitalize())

    paginator = Paginator(payment, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'rows_per_page': rows_per_page,
    }
    return render(request, 'paymentpage.html', context)


@csrf_exempt
def restore_payment_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Payment.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Успешно восстановлено.'})
    return JsonResponse({'message': 'Ошибка при восстановлении Тип оплаты.'})


@csrf_exempt
def delete_payment_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Payment.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'message': 'Ошибка при удалении Тип оплаты.'})


def gender_list(request):
    search_query = request.GET.get('search', '')
    rows_per_page = request.GET.get('rows_per_page', '20')

    try:
        rows_per_page = int(rows_per_page)
        if rows_per_page <= 0:
            rows_per_page = 20
    except ValueError:
        rows_per_page = 20

    gender = Gender.objects.all().order_by('-type')
    if search_query:
        gender = gender.filter(type__icontains=search_query.capitalize())

    paginator = Paginator(gender, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'rows_per_page': rows_per_page,
    }
    return render(request, 'genderpage.html', context)


@csrf_exempt
def restore_gender_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Payment.objects.filter(id__in=ids).update(isdeleted=False)
        return JsonResponse({'message': 'Успешно восстановлено.'})
    return JsonResponse({'message': 'Ошибка при восстановлении Тип оплаты.'})


@csrf_exempt
def delete_gender_list(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        ids = [int(i) for i in ids[0].split(',')]
        Payment.objects.filter(id__in=ids).update(isdeleted=True)
        return JsonResponse({'message': 'Успешно удалено.'})
    return JsonResponse({'message': 'Ошибка при удалении Тип оплаты.'})


def not_linked_pupils(request):
    page = int(request.GET.get('page', 1))
    rows_per_page = int(request.GET.get('rows_per_page', 10))
    search_query = request.GET.get('search', '').strip()

    pupils = Pupils.objects.filter(classes__isnull=True, isdeleted=False)

    if search_query:
        pupils = pupils.filter(first_name__icontains=search_query.capitalize()
                                                     | pupils.filter(last_name__icontains=search_query.capitalize())
                                                     | pupils.filter(surname__icontains=search_query.capitalize())
                               )

    paginator = Paginator(pupils, rows_per_page)
    paginated_pupils = paginator.get_page(page)

    data = {
        'pupils': [
            {
                'id': pupil.id,
                'first_name': pupil.first_name,
                'last_name': pupil.last_name,
                'surname': pupil.surname,
                'gender': pupil.gender
            }
            for pupil in paginated_pupils
        ],
        'pagination': {
            'num_pages': paginator.num_pages,
            'current_page': paginated_pupils.number,
        }
    }

    return JsonResponse(data)


def link_pupils(request):
    if request.method == 'POST':
        pupil_ids = request.POST.getlist('ids[]')
        class_id = request.session.get('class_id')
        pupils = Pupils.objects.filter(id__in=pupil_ids).update(classes=class_id)
        return JsonResponse({'success': 'Привязано успешно.'})
    return JsonResponse({'success': 'Ошибка при привязании.'})