from django.shortcuts import render
import cx_Oracle
from django.http import JsonResponse, HttpResponse
from openpyxl import Workbook
import ast
from datetime import datetime


def execute_sql(sql, **kwargs):
    try:
        # Установка соединения с Oracle
        connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")
        # Создание курсора
        cursor = connection.cursor()
        # Выполнение SQL-запроса
        cursor.execute(sql, kwargs)
        # Получение результатов
        results = cursor.fetchall()
        # Фиксация изменений и закрытие соединения
        cursor.close()
        connection.close()
        # Возврат значения
        return results

    except Exception as e:
        # Обработка ошибок
        return f"Error: {str(e)}"


def get_option():
    try:
        qwerty = '''select okpo, name from NAU_TEST.FIRMS where comments = 'ю' '''

        # Получение результатов
        options = execute_sql(qwerty)
        # Фиксация изменений и закрытие соединения

        html_options = ""
        for key, name in options:
            html_options += f'<option value="{name}">{key}</option>'
        return html_options
    except cx_Oracle.Error as error:
        # Обработка ошибок подключения к базе данных
        print(f"Error connecting to Oracle Database: {error}")


def map_view(request):
    try:
        sql = '''select f.NAME, f.MAP_LAT, f.MAP_LNG, sa.NAME, f.CITY, ff.NAME from NAU_TEST.FIRMS f
                    left join nau_test.firms ff on ff.id = f.PARENTID
                    left join (select f.id firmid, case when tc.isclosed = 1 then 7 
                    else f.statusaptekaid end statusaptekaid
                    from NAU_TEST.FIRMS f 
                    left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                    left join nau_test.STATUSAPTEKA sa on sa.id = st.STATUSAPTEKAID
                    where f.MAP_LAT is not null and f.city is not null and st.STATUSAPTEKAID in (2, 3, 4, 7)
                    and not f.id = 501413'''

        rows = execute_sql(sql)
        html_options = get_option()

        locations = []
        for result in rows:
            name, latitude, longitude, status, city, okpo = result
            locations.append({"name": name, "latitude": latitude, "longitude": longitude, "status": status,
                              "city": city, "okpo": okpo})
        context = {'html_options': html_options, 'locations': locations}
    except cx_Oracle.Error as error:
        # Обработка ошибок подключения к базе данных
        print(f"Error connecting to Oracle Database: {error}")
        locations = []
        html_options = get_option()
        context = {'html_options': html_options, 'locations': locations}

    return render(request, 'mymap/map.html', context)


def maps_filter(request):
    if request.method == 'POST':
        aptid = request.POST.get('aptid')
        name = request.POST.get('name')
        city = request.POST.get('city')
        okpo = request.POST.get('okpo')

        filters = {}
        if aptid:
            filters['f.ID'] = aptid
        if name:
            filters['f.NAME'] = name
        if city:
            filters['f.CITY'] = city
        if okpo:
            filters['ff.NAME'] = okpo

        conditions = []
        for key, value in filters.items():
            if value:
                conditions.append(f"upper({key}) like upper('%{value}%')")

        qwr_base = '''select f.NAME, f.MAP_LAT, f.MAP_LNG, sa.NAME, f.CITY, ff.NAME from NAU_TEST.FIRMS f
                    left join nau_test.firms ff on ff.id = f.PARENTID
                    left join (select f.id firmid, case when tc.isclosed = 1 then 7 
                    else f.statusaptekaid end statusaptekaid
                    from NAU_TEST.FIRMS f 
                    left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                    left join nau_test.STATUSAPTEKA sa on sa.id = st.STATUSAPTEKAID
                    where f.MAP_LAT is not null and f.city is not null and st.STATUSAPTEKAID in (2, 3, 4, 7)
                    and not f.id = 501413'''

        qwr = qwr_base

        if conditions:
            qwr += f" and {' AND '.join(conditions)}"

        try:
            print(qwr)
            results = execute_sql(qwr)
            html_options = get_option()
            locations = []
            for result in results:
                name, latitude, longitude, status, city, okpo = result
                locations.append({"name": name, "latitude": latitude, "longitude": longitude, "status": status,
                                  "city": city, "okpo": okpo})
            context = {'html_options': html_options, 'locations': locations}
            return render(request, 'mymap/map.html', context)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def changes_map(request):
    if request.method == 'POST':
        aptid = request.POST.get('aptid')
        name = request.POST.get('name')
        city = request.POST.get('city')
        okpo = request.POST.get('okpo')

        filters = {}
        if aptid:
            filters['f.ID'] = aptid
        if name:
            filters['f.NAME'] = name
        if city:
            filters['f.CITY'] = city
        if okpo:
            filters['ff.NAME'] = okpo

        conditions = []
        for key, value in filters.items():
            if value:
                conditions.append(f"upper({key}) like upper('%{value}%')")

        if not filters:
            sql = '''select f.id, f.name, f.okpo, f.address2, f.city from NAU_TEST.FIRMS f
                        left join nau_test.firms ff on ff.id = f.PARENTID
                        left join (select f.id firmid, case when tc.isclosed = 1 then 7
                        else f.statusaptekaid end statusaptekaid
                        from NAU_TEST.FIRMS f 
                        left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                        where st.STATUSAPTEKAID = 4'''
        else:
            sql = f'''select  f.id, f.name, f.okpo, f.address2, f.city from NAU_TEST.FIRMS f
                        left join nau_test.firms ff on ff.id = f.PARENTID
                        left join (select f.id firmid, case when tc.isclosed = 1 then 7 
                        else f.statusaptekaid end statusaptekaid
                        from NAU_TEST.FIRMS f 
                        left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                        where st.STATUSAPTEKAID = 4 and {' AND '.join(conditions)} '''

        try:
            print(sql)
            results = execute_sql(sql)
            # Выполните фильтрацию данных на основе введенных пользователем значений
            return render(request, 'mymap/changes_map.html', {'results': results})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return render(request, 'mymap/changes_map.html')


def download_data(request):
    if request.method == 'POST':
        try:
            # Получение строки результатов из запроса
            raw_results_string = request.POST.getlist('results')

            # Разбивка строки на строки (по символу новой строки)
            rows = [row.strip() for row in raw_results_string]

            # Создание нового XLSX-файла
            workbook = Workbook()
            worksheet = workbook.active

            # Заголовки колонок
            headers = ['ID', 'Назва', 'ЕРДПОУ', 'Адреса', 'Місто']

            # Запись заголовков в первую строку
            for col_num, header in enumerate(headers, start=1):
                worksheet.cell(row=1, column=col_num, value=header)

            # Запись данных в соответствующие колонки
            for row_num, row_data in enumerate(rows, start=2):
                # Используем ast.literal_eval для безопасного преобразования строки в кортеж
                row_tuple = ast.literal_eval(row_data)
                # Запись данных в ячейки с учетом разных типов данных
                for col_num, value in enumerate(row_tuple, start=1):
                    worksheet.cell(row=row_num, column=col_num, value=value)

            current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            # Создание HTTP-ответа с XLSX-файлом
            filename = f"filtered_data_{current_datetime}.xlsx"
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            workbook.save(response)

            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
