from django.shortcuts import render, redirect
import cx_Oracle
from django.http import JsonResponse


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
        name = request.POST.get('name')
        city = request.POST.get('city')
        okpo = request.POST.get('okpo')

        filters = {}
        if name:
            filters['NAME'] = name
        if city:
            filters['CITY'] = city
        if okpo:
            filters['OKPO'] = okpo

        if filters:
            if name or city:
                conditions = []
                for key, value in filters.items():
                    if value:
                        conditions.append(f"upper({key}) like upper('%{value}%')")
                try:
                    connection = cx_Oracle.connect("NSAR", "L:FYUJAHB", "192.168.201.1:1521/Primus", encoding="UTF-8")
                    cursor = connection.cursor()

                    qwr = f'''select NAME, MAP_LAT, MAP_LNG from NAU_TEST.FIRMS f
                    left join (select f.id firmid, case when tc.isclosed = 1 then 7 else f.statusaptekaid end statusaptekaid
                    from NAU_TEST.FIRMS f left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
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
                    left join (select f.id firmid, case when tc.isclosed = 1 then 7 else f.statusaptekaid end statusaptekaid
                    from NAU_TEST.FIRMS f left join nau_test.firms_temprory_closed tc on tc.firmsid = f.id) st on st.firmid = f.id
                    where st.STATUSAPTEKAID = 4 and parentid in (SELECT id FROM NAU_TEST.FIRMS f where upper(name) like upper('%{okpo}%') and COMMENTS = 'ю') '''
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
