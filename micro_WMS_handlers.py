import requests
import json

 # URL вашего PostgREST сервера
postgrest_url = 'http://192.168.1.114:3000'
timeout = 3

def init_on_start(hashMap,_files=None,_data=None):
    return hashMap

def Get_Orders_Data_To_Table(hashMap, _files=None, _data=None):
    
    # Путь к нужной таблице или представлению
    path = 'wms_orders_captions?and=(typeid.eq.1,done.neq.true)&'
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    # Параметры запроса (например, фильтрация данных)
    params = {
        'select': 'id:id,Поставщик:contractor,Номер:doc_number'
    }

    try:
        # Отправка GET-запроса
        response = requests.get(url, params=params, timeout=timeout)

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
    
    if hashMap.get("listener")=="barcode":
    
        barcode = hashMap.get("barcode")
        path = f'wms_goods?barcode=in.(%22{barcode}%22)'
         # Полный URL для запроса
        url = f'{postgrest_url}/{path}'

        try:
            # Отправка GET-запроса
            response = requests.get(url, timeout=timeout)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Парсинг JSON ответа
                data = response.json()
                if data:
                    jrecord = data[0]
                    hashMap.put("nom", jrecord['caption'])
                    hashMap.put("art", jrecord['code'])
                    hashMap.put("nom_id", jrecord['id'])
                    hashMap.put("unit", jrecord['unit_str'])
                    hashMap.put("ShowScreen", "wms.Ввод количества факт по заказу")                    
                else:    
                    hashMap.put("toast", f"Товар с штрихкодом {barcode} не найден")        
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
            
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')
    else:
        jrecord = json.loads(hashMap.get("selected_line"))
        unit_id = str(jrecord['id'])
        
        # Путь к нужной таблице или представлению
        path = f'wms_orders_captions?id=eq.{unit_id}'
        
        # Полный URL для запроса
        url = f'{postgrest_url}/{path}'
        
        try:
            # Отправка GET-запроса
            response = requests.get(url, timeout=timeout)

            # Проверка статуса ответа
            if response.status_code == 200:
                # Парсинг JSON ответа
                data = response.json()
                jrecord = data[0]
                hashMap.put("order", jrecord['caption'])
                hashMap.put("orderRef", unit_id)
                Get_OrderGoods_Data_To_Table(hashMap)
                hashMap.put("ShowScreen", "Приемка по заказу начало")
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
                #print(f'Ошибка запроса: {response.status_code} - {response.text}')
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap  

def Get_OrderGoods_Data_To_Table(hashMap, _files=None, _data=None):

    unit_id = hashMap.get("orderRef") 
    # Путь к нужной таблице или представлению
    path = 'wms_orders_table?select=Товар:nom,Артикул:code,План:plan,Факт:fact&order_id=eq.{unit_id}'.format(unit_id=unit_id)
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        # Логирование перед отправкой запроса
        
        # Отправка GET-запроса
        #response = requests.get(url, params=params)
        response = requests.get(url, timeout=timeout)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            hashMap.put("table", json.dumps(data))
            #hashMap.put("ShowScreen", "wms.Ввод товара по заказу")
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            print(f'Ошибка запроса: {response.status_code} - {response.text}')
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        print(f'Исключение: {str(e)}')

    return hashMap

def Set_Var(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")

    if CurScreen == "wms.Ввод товара по заказу":
        hashMap.put("noaddr", true)
    elif CurScreen=="wms.Ввод количества факт по заказу":
        hashMap.put("noaddr", true)
    return hashMap

def goods_record_input(hashMap,_files=None,_data=None):
    global nom_id

    return hashMap

def on_btn_done(hashMap,_files=None,_data=None):

    unit_id = hashMap.get("orderRef")
    path = f'wms_orders_captions?id=eq.{unit_id}'

    url = f'{postgrest_url}/{path}'

    # Данные для обновления в формате JSON
    data = {
        'done': 'true'
        }

    # Заголовки для запроса
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Отправка GET-запроса
        response = requests.patch(url,headers=headers,data = json.dumps(data))

        # Проверка статуса ответа
        if response.status_code in [200, 204]:
            hashMap.put("toast", 'Документ завершен')
            hashMap.put("FinishProcess","") 
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
                #print(f'Ошибка запроса: {response.status_code} - {response.text}')
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')

    return hashMap

#Пример использования функции
class MockHashMap:
    def __init__(self):
        self.store = {}

    def put(self, key, value):
        self.store[key] = value

    def get(self, key, default=None):
        return self.store.get(key, default)

#Тестирование функции
if __name__ == "__main__":
    hashMap = MockHashMap()
    hashMap.put("current_screen_name","wms.Ввод товара по заказу")
    #Get_Orders_Data_To_Table(hashMap)
    #units_input(hashMap)
    #Get_OrderGoods_Data_To_Table(hashMap)
    #print('Содержимое hashMap:', hashMap.store)
    Set_Var(hashMap)