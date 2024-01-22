from django.shortcuts import render, redirect
import cx_Oracle
from django.http import JsonResponse, HttpResponse
from openpyxl import Workbook
import ast


def map_view(request):
    try:
        connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")

        sql = '''select NAME, MAP_LAT, MAP_LNG from NAU_TEST.FIRMS f
        left join (select f.id firmid, case when tc.isclosed = 1 then 7 else f.statusaptekaid end statusaptekaid
        from NAU_TEST.FIRMS f left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
        where st.STATUSAPTEKAID = 4'''

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        locations = []
        for row in rows:
            name, latitude, longitude = row
            locations.append({"name": name, "latitude": latitude, "longitude": longitude})
        cursor.close()
        connection.close()
    except cx_Oracle.Error as error:
        # Обработка ошибок подключения к базе данных
        print(f"Error connecting to Oracle Database: {error}")
        locations = []

    return render(request, 'mymap/map.html', {'locations': locations})


def maps_filter(request):
    if request.method == 'POST':
        aptid = request.POST['aptid']
        name = request.POST.get('name')
        city = request.POST.get('city')
        okpo = request.POST.get('okpo')

        filters = {}
        if aptid:
            filters['ID'] = aptid
        if name:
            filters['NAME'] = name
        if city:
            filters['CITY'] = city
        if okpo:
            filters['OKPO'] = okpo

        if filters:
            if name or city or aptid:
                conditions = []
                for key, value in filters.items():
                    if value:
                        conditions.append(f"upper({key}) like upper('%{value}%')")
                try:
                    connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")
                    cursor = connection.cursor()

                    qwr = f'''select NAME, MAP_LAT, MAP_LNG from NAU_TEST.FIRMS f
                    left join (select f.id firmid, case when tc.isclosed = 1 then 7 
                    else f.statusaptekaid end statusaptekaid
                    from NAU_TEST.FIRMS f 
                    left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                    where st.STATUSAPTEKAID = 4 and {' AND '.join(conditions)} '''
                    print(qwr)

                    cursor.execute(qwr)
                    results = cursor.fetchall()
                    locations = []
                    for result in results:
                        name, latitude, longitude = result
                        locations.append({"name": name, "latitude": latitude, "longitude": longitude})
                    cursor.close()
                    connection.close()
                    return render(request, 'mymap/map.html', {'locations': locations})
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=500)
            elif okpo:
                try:
                    connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")
                    cursor = connection.cursor()

                    qwr = f'''select NAME, MAP_LAT, MAP_LNG from NAU_TEST.FIRMS f
                    left join (select f.id firmid, case when tc.isclosed = 1 then 7 
                    else f.statusaptekaid end statusaptekaid
                    from NAU_TEST.FIRMS f 
                    left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                    where st.STATUSAPTEKAID = 4 and 
                    parentid in (select id from NAU_TEST.FIRMS f where upper(name) like upper('%{okpo}%') and 
                    COMMENTS = 'ю') '''
                    print(qwr)

                    cursor.execute(qwr)
                    results = cursor.fetchall()
                    locations = []
                    for result in results:
                        name, latitude, longitude = result
                        locations.append({"name": name, "latitude": latitude, "longitude": longitude})
                    cursor.close()
                    connection.close()
                    return render(request, 'mymap/map.html', {'locations': locations})
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=500)
        else:
            return redirect('map_view')


def changes_map(request):
    if request.method == 'POST':
        aptid = request.POST['aptid']
        name = request.POST.get('name')
        city = request.POST.get('city')
        okpo = request.POST.get('okpo')

        filters = {}
        if aptid:
            filters['ID'] = aptid
        if name:
            filters['NAME'] = name
        if city:
            filters['CITY'] = city
        if okpo:
            filters['OKPO'] = okpo

        if not filters:
            try:
                connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")
                cursor = connection.cursor()

                sql = '''select f.id, f.name, f.okpo, f.address2, f.city from NAU_TEST.FIRMS f
                        left join (select f.id firmid, case when tc.isclosed = 1 then 7 else f.statusaptekaid end statusaptekaid
                        from NAU_TEST.FIRMS f left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                        where st.STATUSAPTEKAID = 4'''
                cursor.execute(sql)
                results = cursor.fetchall()
                cursor.close()
                connection.close()
                return render(request, 'mymap/changes_map.html', {'results': results})

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        if name or city or aptid:
            conditions = []
            for key, value in filters.items():
                if value:
                    conditions.append(f"upper({key}) like upper('%{value}%')")
            try:
                connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")
                cursor = connection.cursor()

                sql = f'''select id, name, okpo, address2, city from NAU_TEST.FIRMS f
                            left join (select f.id firmid, case when tc.isclosed = 1 then 7 
                            else f.statusaptekaid end statusaptekaid
                            from NAU_TEST.FIRMS f 
                            left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                            where st.STATUSAPTEKAID = 4 and {' AND '.join(conditions)} '''
                print(sql)
                cursor.execute(sql)
                results = cursor.fetchall()
                # Закрытие курсора и соединения
                cursor.close()
                connection.close()
                # Выполните фильтрацию данных на основе введенных пользователем значений
                return render(request, 'mymap/changes_map.html', {'results': results})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        elif okpo:
            try:
                connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")
                cursor = connection.cursor()

                qwr = f'''select f.id, f.name, f.okpo, f.address2, f.city from NAU_TEST.FIRMS f
                left join (select f.id firmid, case when tc.isclosed = 1 then 7 
                else f.statusaptekaid end statusaptekaid
                from NAU_TEST.FIRMS f 
                left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                where st.STATUSAPTEKAID = 4 and 
                parentid in (select id from NAU_TEST.FIRMS f where upper(name) like upper('%{okpo}%') and 
                COMMENTS = 'ю') '''
                print(qwr)

                cursor.execute(qwr)
                results = cursor.fetchall()
                cursor.close()
                connection.close()
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

            # Создание HTTP-ответа с XLSX-файлом
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="filtered_data.xlsx"'
            workbook.save(response)

            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

