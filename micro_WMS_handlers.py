import requests
import json

def Get_Orders_Data_To_Table(hashMap, _files=None, _data=None):
    # URL вашего PostgREST сервера
    postgrest_url = 'http://192.168.1.109:3000'

    # Путь к нужной таблице или представлению
    path = 'wms_orders_captions?and=(typeid.eq.1,done.is.null)&'

    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    # Параметры запроса (например, фильтрация данных)
    params = {
        'select': 'id:id,Поставщик:contractor,Номер:doc_number'
    }

    try:
        # Логирование перед отправкой запроса
        print(f'Отправка запроса к {url} с параметрами {params}')
        
        # Отправка GET-запроса
        response = requests.get(url, params=params)

        # Логирование кода состояния ответа
        print(f'Ответ от сервера: {response.status_code}')

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            print(f'Полученные данные: {json.dumps(data, indent=4, ensure_ascii=False)}')
            hashMap.put("table", data)
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            print(f'Ошибка запроса: {response.status_code} - {response.text}')
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        print(f'Исключение: {str(e)}')

