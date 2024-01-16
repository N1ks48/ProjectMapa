from django.shortcuts import render
import cx_Oracle


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

    except cx_Oracle.Error as error:
        # Обработка ошибок подключения к базе данных
        print(f"Error connecting to Oracle Database: {error}")
        locations = []  # Используйте пустой список или другое значение по умолчанию
        # locations = [
        #     {"name": "Киев", "latitude": 50.4501, "longitude": 30.5234},
        #     {"name": "Львов", "latitude": 49.8429, "longitude": 24.0315},
        #     {"name": "Одесса", "latitude": 46.4694, "longitude": 30.7409},
        #     # Добавьте другие местоположения по мере необходимости
        # ]
    return render(request, 'mymap/map.html', {'locations': locations})
