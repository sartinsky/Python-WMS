def Get_Orders_Data_To_Table(hashMap, _files=None, _data=None):
    # URL вашего PostgREST сервера
    postgrest_url = 'http://192.168.1.109:3000'

    # Путь к нужной таблице или представлению
    path = 'wms_orders_table'

    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    # Параметры запроса (например, фильтрация данных)
    params = {
        'select': 'Товар:nom,Артикул:code,План:plan,Факт:fact',
        'order_id': 'eq.~id~'
    }

    try:
        # Отправка GET-запроса
        response = requests.get(url, params=params)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            hashMap.put("table", data)
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')