import requests
import json

 # URL вашего PostgREST сервера
postgrest_url = 'http://192.168.1.109:3000'

def Get_Orders_Data_To_Table(hashMap, _files=None, _data=None):
    
    # Путь к нужной таблице или представлению
    path = 'wms_orders_captions?and=(typeid.eq.1,done.is.null)&'
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    # Параметры запроса (например, фильтрация данных)
    params = {
        'select': 'id:id,Поставщик:contractor,Номер:doc_number'
    }

    try:
        # Отправка GET-запроса
        response = requests.get(url, params=params)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            hashMap.put("orders_table", json.dumps(data))
        else:
            hashMap.put("toast", f'Error: {response.status_code}')        
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')        

    return hashMap    

def units_input(hashMap,_files=None,_data=None):
    
    #jrecord = json.loads(hashMap.get("selected_line"))
    #unit_id = str(jrecord['id'])
    unit_id = '85'

    # Путь к нужной таблице или представлению
    path = 'wms_orders_captions?id=eq.{unit_id}'.format(unit_id=unit_id)
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'
    
    try:
        # Отправка GET-запроса
        response = requests.get(url)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            jrecord = data[0]
            hashMap.put("order", jrecord['caption'])
            hashMap.put("orderRef", unit_id)
            Get_OrderGoods_Data_To_Table(hashMap)            
        else:
           hashMap.put("toast", f'Error: {response.status_code}')
           #print(f'Ошибка запроса: {response.status_code} - {response.text}')
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap  

def Get_OrderGoods_Data_To_Table(hashMap, _files=None, _data=None):

    #unit_id = hashMap.get("orderRef") 
    unit_id = 85
    # Путь к нужной таблице или представлению
    path = 'wms_orders_table?select=Товар:nom,Артикул:code,План:plan,Факт:fact&order_id=eq.{unit_id}'.format(unit_id=unit_id)
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        # Логирование перед отправкой запроса
        
        # Отправка GET-запроса
        #response = requests.get(url, params=params)
        response = requests.get(url)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            hashMap.put("table", json.dumps(data))
            #hashMap.put("ShowDialog", "wms.Ввод товара по заказу")
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            print(f'Ошибка запроса: {response.status_code} - {response.text}')
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        print(f'Исключение: {str(e)}')

    return hashMap

# #Пример использования функции
# class MockHashMap:
#     def __init__(self):
#         self.store = {}

#     def put(self, key, value):
#         self.store[key] = value

# #Тестирование функции
# if __name__ == "__main__":
#     hashMap = MockHashMap()
#     Get_Orders_Data_To_Table(hashMap)
#     units_input(hashMap)
#     Get_OrderGoods_Data_To_Table(hashMap)
#     print('Содержимое hashMap:', hashMap.store)