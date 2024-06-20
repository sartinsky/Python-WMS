import requests
import json

 # URL вашего PostgREST сервера
postgrest_url = 'http://192.168.1.104:3000'
timeout = 3

def init_on_start(hashMap,_files=None,_data=None):
    return hashMap

def Get_Orders_Data_To_Table(hashMap, _files=None, _data=None):
    
    # Путь к нужной таблице или представлению
    path = 'wms_orders_captions?and=(typeid.eq.1,or(done.neq.true,done.is.null))&'
    
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
    
    CurScreen = hashMap.get("current_screen_name")
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
                    hashMap.put("nom_id", str(jrecord['id']))
                    hashMap.put("unit", jrecord['unit_str'])
                    if CurScreen == "wms.Ввод товара по заказу":
                        hashMap.put("ShowScreen", "wms.Ввод количества факт по заказу")
                    elif CurScreen == "wms.Ввод товара размещение взять":
                        hashMap.put("ShowScreen", "wms.Ввод количества взять размещение")
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
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def Set_Var(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")

    if CurScreen == "wms.Ввод товара по заказу":
        hashMap.put("noaddr", 'true')
    elif CurScreen=="wms.Ввод количества факт по заказу":
        hashMap.put("noaddr", 'true')
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
        # Отправка PATCH-запроса
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

def on_input_qtyfact(hashMap,_files=None,_data=None):

    CurScreen = hashMap.get("current_screen_name")
    if CurScreen == "wms.Ввод количества факт по заказу":
        
        # Путь к нужной таблице или представлению
        path = 'wms_operations'
        
        # Полный URL для запроса
        url = f'{postgrest_url}/{path}'

         # Заголовки для запроса
        headers = {
        'Content-Type': 'application/json'
        }
        
        #Параметры запроса (например, фильтрация данных)
        data = {
        "sku_id": hashMap.get("nom_id"),
        "qty": hashMap.get("qty"),
        "order_id": hashMap.get("orderRef"),
        "user": hashMap.get("ANDROID_ID"),
        "to_operation": "1",
        "address_id": "К РАЗМЕЩЕНИЮ"
        }

        try:
            # Отправка GET-запроса
            response = requests.post(url, json=data, timeout=timeout)

            # Проверка статуса ответа
            if response.status_code == 201:
                Get_OrderGoods_Data_To_Table(hashMap)
                hashMap.put("ShowScreen", "wms.Ввод товара по заказу")
            else:
                hashMap.put("toast", f'Error: {response.status_code}')        
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')        

        return hashMap 

def get_operators_placing(hashMap, _files=None, _data=None):

    user = hashMap.get("ANDROID_ID") 
    # Путь к нужной таблице или представлению
    path = f'rpc/get_operators_placing?user_id={user}&select=Товар:nom,Кол-во:qty'
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        # Логирование перед отправкой запроса
        
        # Отправка GET-запроса
        response = requests.get(url, timeout=timeout)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            hashMap.put("table", json.dumps(data))            
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def on_btn_placing(hashMap,_files=None,_data=None):
    
    listener = hashMap.get("listener")
    CurScreen = hashMap.get("current_screen_name")
    
    if listener=="btn_placing":
        if CurScreen == "wms.Ввод товара размещение взять":
            hashMap.put("ShowScreen", "wms.Ввод адреса размещение")
        
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
    hashMap.put("ANDROID_ID","380eaecaff29d921")
    #hashMap.put("barcode","X001OMTDSV")
    Get_Orders_Data_To_Table(hashMap)
    #units_input(hashMap)
    #Get_OrderGoods_Data_To_Table(hashMap)
    #print('Содержимое hashMap:', hashMap.store)
    #Set_Var(hashMap)
    #on_input_qtyfact(hashMap)
    #get_operators_placing(hashMap)