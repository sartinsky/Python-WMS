import requests
import json

 # URL вашего PostgREST сервера
postgrest_url = 'http://192.168.1.105:3000'
timeout = 3

def init_on_start(hashMap,_files=None,_data=None):
    return hashMap

def Set_Var(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")

    if CurScreen == "wms.Ввод товара по заказу":
        hashMap.put("noaddr", 'true')
    elif CurScreen=="wms.Ввод количества факт по заказу":
        hashMap.put("noaddr", 'true')
    elif CurScreen=="wms.Ввод количества взять размещение":
        hashMap.put("noaddr", 'true')
    elif CurScreen=="wms.Ввод адреса размещение":
        hashMap.put("action_str", 'Сканируйте адрес')
    elif CurScreen=="wms.Ввод количества размещение":
        hashMap.put("noaddr", 'false')
    elif CurScreen=="wms.Ввод товара приемка факт":
        hashMap.put("noaddr", 'true')
    elif CurScreen=="wms.Ввод количества факт":
        hashMap.put("noaddr", 'true')    
    elif CurScreen=="wms.Ввод адреса":
        hashMap.put("action_str", 'Сканируйте адрес-отправитель')        
    elif CurScreen=="wms.Ввод товара перемещение":
        hashMap.put("noaddr", 'true')            
    elif CurScreen=="wms.Ввод адреса положить":
        hashMap.put("action_str", 'Сканируйте адрес-получатель')            
    elif CurScreen=="wms.Ввод товара положить":
        hashMap.put("noaddr", 'true')                
    elif CurScreen=="wms.Ввод адреса отбор":
        hashMap.put("action_str", 'Сканируйте адрес ячейки')    
        hashMap.put("NextAddr", 'Нет задания')    
    elif CurScreen=="wms.Ввод количества отбор":
        hashMap.put("noaddr", 'false')        
    return hashMap

def Get_Orders_Data_To_Table(hashMap, _files=None, _data=None):
    
    CurScreen = hashMap.get("current_screen_name")

    if CurScreen == 'wms.Выбор распоряжения':
        # Путь к нужной таблице или представлению
        path = 'wms_orders_captions?and=(typeid.eq.1,or(done.neq.true,done.is.null))&select=id:id,Поставщик:contractor,Номер:doc_number'
        
    elif CurScreen == 'wms.Выбор распоряжения отбор':
        
        # Путь к нужной таблице или представлению
        path = 'wms_orders_captions?and=(typeid.eq.2,done.is.null)&select=id:id,Покупатель:contractor,Номер:doc_number'

    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        # Отправка GET-запроса
        response = requests.get(url, timeout=timeout)

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

def Get_OrderGoods_Data_To_Table(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")
    order_id = hashMap.get("orderRef") 

    # Путь к нужной таблице или представлению
    if CurScreen == 'Приемка по заказу начало' or CurScreen == 'wms.Ввод количества факт по заказу':
        path = f'wms_orders_table?select=Товар:nom,Артикул:code,План:plan,Факт:fact&order_id=eq.{order_id}'
                
    elif CurScreen == 'wms.Ввод адреса отбор':
        path = f'rpc/get_picking?orderid={order_id}&select=id:sku_id,Товар:sku,Адрес:address,Кол-во:qty'
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        
        # Отправка GET-запроса
        response = requests.get(url, timeout=timeout)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data_with_ids = response.json()
            data = response.json()

            for item in data:
                if 'id' in item:
                    del item['id']
 
            hashMap.put("central_table", json.dumps(data))
            
            if CurScreen == 'Приемка по заказу начало':
                hashMap.put("table", json.dumps(data))                
            elif CurScreen == 'wms.Ввод адреса отбор':    
                hashMap.put("addr_table", json.dumps(data))
                hashMap.put("data_with_ids", json.dumps(data_with_ids))
                
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def Get_Picking(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")
    order_id = hashMap.get("orderRef") 

    if CurScreen == 'wms.Ввод адреса отбор':

        # Путь к нужной таблице или представлению
        path = f'rpc/get_picking?limit=1&orderid={order_id}'
        
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
                    hashMap.put("NextAddr", jrecord['address'])
                else:
                    hashMap.put("toast", 'Нет данных по пиккингу')    
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

def get_placement_orders(hashMap, _files=None, _data=None):

    user = hashMap.get("ANDROID_ID") 
    # Путь к нужной таблице или представлению
    path = f'rpc/get_placement_orders?user_id={user}&select=Товар:sku,Ячейка:address,Кол-во:qty'
            
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        
        # Отправка GET-запроса
        response = requests.get(url, timeout=timeout)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            hashMap.put("addr_table", json.dumps(data))            
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def get_goods_for_address_placement(hashMap, _files=None, _data=None):

    user = hashMap.get("ANDROID_ID") 
    address = hashMap.get("addr_id") 
    # Путь к нужной таблице или представлению
    path = f'rpc/get_goods_for_address_placement?user_id={user}&address_id={address}&select=Товар:sku,Кол-во:qty'
           
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        
        # Отправка GET-запроса
        response = requests.get(url, timeout=timeout)

        # Проверка статуса ответа
        if response.status_code == 200:
            # Парсинг JSON ответа
            data = response.json()
            hashMap.put("table_goods_for_addr", json.dumps(data))            
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def get_operators_moving(hashMap, _files=None, _data=None):

    user = hashMap.get("ANDROID_ID") 
    # Путь к нужной таблице или представлению
    path = f'rpc/get_operators_moving?user_id={user}&select=Товар:nom,Кол-во:qty'
            
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

def on_BACK_BUTTON(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")
    if CurScreen == "wms.Ввод товара размещение":
        hashMap.put("ShowScreen", "wms.Ввод адреса размещение")
    elif CurScreen == "wms.Ввод количества размещение":
        hashMap.put("ShowScreen", "wms.Ввод товара размещение")
    elif CurScreen == "wms.Ввод количества взять размещение":
        hashMap.put("ShowScreen", "wms.Ввод товара размещение взять")
    elif CurScreen == "wms.Ввод товара перемещение":
        hashMap.put("ShowScreen", "wms.Ввод адреса")    
    elif CurScreen == "wms.Ввод товара положить":
        hashMap.put("ShowScreen", "wms.Ввод адреса")        
    elif CurScreen == "wms.Ввод количества положить":
        hashMap.put("ShowScreen", "wms.Ввод товара положить")
    elif CurScreen == "wms.Ввод товара отбор":
        hashMap.put("ShowScreen", "wms.Ввод адреса отбор")
    elif CurScreen=="wms.Ввод количества отбор":
        hashMap.put("ShowScreen", "wms.Ввод товара отбор")                
    return hashMap 

def on_FORVARD_BUTTON(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")
    if CurScreen == "Приемка по заказу начало":
        hashMap.put("ShowScreen", "wms.Ввод товара по заказу")
    # elif CurScreen == "wms.Ввод количества размещение":
    #     hashMap.put("ShowScreen", "wms.Ввод товара размещение")
    # elif CurScreen == "wms.Ввод количества взять размещение":
    #     hashMap.put("ShowScreen", "wms.Ввод товара размещение взять")
    # elif CurScreen == "wms.Ввод товара перемещение":
    #     hashMap.put("ShowScreen", "wms.Ввод адреса")    
    # elif CurScreen == "wms.Ввод товара положить":
    #     hashMap.put("ShowScreen", "wms.Ввод адреса")        
    # elif CurScreen == "wms.Ввод количества положить":
    #     hashMap.put("ShowScreen", "wms.Ввод товара положить")
    # elif CurScreen == "wms.Ввод товара отбор":
    #     hashMap.put("ShowScreen", "wms.Ввод адреса отбор")
    # elif CurScreen=="wms.Ввод количества отбор":
    #     hashMap.put("ShowScreen", "wms.Ввод товара отбор")                
    return hashMap 

def on_btn_put(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")
    if CurScreen == "wms.Ввод адреса":
        hashMap.put("ShowScreen", "wms.Ввод адреса положить")
    
    return hashMap 

def on_btn_placing(hashMap,_files=None,_data=None):
    
    listener = hashMap.get("listener")
    CurScreen = hashMap.get("current_screen_name")
    
    if listener == "btn_placing":
        if CurScreen == "wms.Ввод товара размещение взять":
            hashMap.put("ShowScreen", "wms.Ввод адреса размещение")
        
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
                
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')

    return hashMap

def on_address_input(hashMap,_files=None,_data=None):
    
    CurScreen = hashMap.get("current_screen_name")
    listener = hashMap.get("listener")

    if listener == "barcode":
    
        barcode = hashMap.get("addr_barcode")
        
        path = f'wms_addresses?barcode=in.(%22{barcode}%22)'
                
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
                    hashMap.put("addr_id", str(jrecord['id']))
                    hashMap.put("addr", f"{jrecord['caption']} ({barcode})")
                    if CurScreen == 'wms.Ввод адреса размещение':
                        hashMap.put("ShowScreen", "wms.Ввод товара размещение")
                    elif CurScreen == 'wms.Ввод адреса':
                        hashMap.put("ShowScreen", "wms.Ввод товара перемещение")   
                    elif CurScreen == 'wms.Ввод адреса положить':
                        hashMap.put("ShowScreen", "wms.Ввод товара положить")
                    elif CurScreen == 'wms.Ввод адреса отбор':
                        hashMap.put("ShowScreen", "wms.Ввод товара отбор")
                else:    
                    hashMap.put("toast", f"Ячейка с штрихкодом {barcode} не найдена")        
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
            
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')
    
    return hashMap

def on_input_qtyfact(hashMap,_files=None,_data=None):

    listener = hashMap.get("listener")
    CurScreen = hashMap.get("current_screen_name")
    if CurScreen == "wms.Ввод количества факт по заказу":
        
        if listener is None:

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
            "qty": hashMap.get("qty"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": "К РАЗМЕЩЕНИЮ",
            "order_id": hashMap.get("orderRef")
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
        elif listener == "BACK_BUTTON":
            hashMap.put("ShowScreen", "wms.Ввод товара по заказу")

    elif CurScreen == "wms.Ввод количества взять размещение":

        if listener is None:
        
            hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))

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
            "qty": hashMap.get("qty_minus"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": "К РАЗМЕЩЕНИЮ",
            }

            try:
                # Отправка GET-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    
                    #Параметры запроса (например, фильтрация данных)
                    data = {
                    "qty": hashMap.get("qty"),
                    "sku_id": hashMap.get("nom_id"),
                    "user": hashMap.get("ANDROID_ID"),
                    "address_id": hashMap.get("ANDROID_ID"),
                    "to_operation": "1"
                    }
                    
                    try:
                        # Отправка GET-запроса
                        response = requests.post(url, json=data, timeout=timeout)

                        # Проверка статуса ответа
                        if response.status_code == 201:
                            hashMap.put("ShowScreen", "wms.Ввод товара размещение взять")
                        else:
                            hashMap.put("toast", f'Error: {response.status_code}')        
                    except Exception as e:
                        hashMap.put("toast", f'Exception occurred: {str(e)}')
                    
                else:
                    hashMap.put("toast", f'Error: {response.status_code}')        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')           

    elif CurScreen == "wms.Ввод количества размещение":

        if listener is None:
        
            hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))

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
            "qty": hashMap.get("qty_minus"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": hashMap.get("ANDROID_ID"),
            }

            try:
                # Отправка POST-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    
                    #Параметры запроса (например, фильтрация данных)
                    data = {
                    "qty": hashMap.get("qty"),
                    "sku_id": hashMap.get("nom_id"),
                    "user": hashMap.get("ANDROID_ID"),
                    "address_id": hashMap.get("addr_id")
                    }
                    
                    try:
                        # Отправка GET-запроса
                        response = requests.post(url, json=data, timeout=timeout)

                        # Проверка статуса ответа
                        if response.status_code == 201:
                            hashMap.put("ShowScreen", "wms.Ввод адреса размещение")
                        else:
                            hashMap.put("toast", f'Error: {response.status_code}')        
                    except Exception as e:
                        hashMap.put("toast", f'Exception occurred: {str(e)}')
                    
                else:
                    hashMap.put("toast", f'Error: {response.status_code}')        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')

    elif CurScreen == "wms.Ввод количества факт":

        if listener is None:
        
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
            "no_order": "true",
            "qty": hashMap.get("qty"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": "К РАЗМЕЩЕНИЮ",
            }

            try:
                # Отправка POST-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    hashMap.put("ShowScreen", "wms.Ввод товара приемка факт")
                    
                else:
                    hashMap.put("toast", f'Error: {response.status_code}')        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')                   

    elif CurScreen == "wms.Ввод количества взять":

        if listener is None:
        
            hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))

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
            "qty": hashMap.get("qty_minus"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": hashMap.get("addr_id"),
            }

            try:
                # Отправка POST-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    
                    #Параметры запроса (например, фильтрация данных)
                    data = {
                    "qty": hashMap.get("qty"),
                    "sku_id": hashMap.get("nom_id"),
                    "user": hashMap.get("ANDROID_ID"),
                    "address_id": hashMap.get("ANDROID_ID"),
                    "to_operation": "5",
                    }
                    
                    try:
                        # Отправка GET-запроса
                        response = requests.post(url, json=data, timeout=timeout)

                        # Проверка статуса ответа
                        if response.status_code == 201:
                            hashMap.put("ShowScreen", "wms.Ввод адреса")
                        else:
                            hashMap.put("toast", f'Error: {response.status_code}')        
                    except Exception as e:
                        hashMap.put("toast", f'Exception occurred: {str(e)}')
                    
                else:
                    hashMap.put("toast", f'Error: {response.status_code}')        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')

    elif CurScreen == "wms.Ввод количества положить":

        if listener is None:
        
            hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))

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
            "qty": hashMap.get("qty_minus"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": hashMap.get("ANDROID_ID"),
            "to_operation": "5"
            }

            try:
                # Отправка POST-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    
                    #Параметры запроса (например, фильтрация данных)
                    data = {
                    "qty": hashMap.get("qty"),
                    "sku_id": hashMap.get("nom_id"),
                    "user": hashMap.get("ANDROID_ID"),
                    "address_id": hashMap.get("addr_id")                    
                    }
                    
                    try:
                        # Отправка GET-запроса
                        response = requests.post(url, json=data, timeout=timeout)

                        # Проверка статуса ответа
                        if response.status_code == 201:
                            hashMap.put("ShowScreen", "wms.Ввод адреса положить")
                        else:
                            hashMap.put("toast", f'Error: {response.status_code}')        
                    except Exception as e:
                        hashMap.put("toast", f'Exception occurred: {str(e)}')
                    
                else:
                    hashMap.put("toast", f'Error: {response.status_code}')        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')            

    elif CurScreen == "wms.Ввод количества отбор":

        if listener is None:
        
            hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))

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
            "qty": hashMap.get("qty_minus"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": hashMap.get("addr_id")            
            }

            try:
                # Отправка POST-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    
                    #Параметры запроса (например, фильтрация данных)
                    data = {
                    "qty": hashMap.get("qty"),
                    "sku_id": hashMap.get("nom_id"),
                    "user": hashMap.get("ANDROID_ID"),
                    "address_id": "ОТБОР",
                    "order_id": hashMap.get("orderRef")
                    }
                    
                    try:
                        # Отправка GET-запроса
                        response = requests.post(url, json=data, timeout=timeout)

                        # Проверка статуса ответа
                        if response.status_code == 201:
                            hashMap.put("ShowScreen", "wms.Ввод адреса отбор")
                        else:
                            hashMap.put("toast", f'Error: {response.status_code}')        
                    except Exception as e:
                        hashMap.put("toast", f'Exception occurred: {str(e)}')
                    
                else:
                    hashMap.put("toast", f'Error: {response.status_code}')        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')


    return hashMap 

def on_units_input(hashMap,_files=None,_data=None):
    
    CurScreen = hashMap.get("current_screen_name")
    listener = hashMap.get("listener")

    if listener == "barcode":
    
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
                    elif CurScreen == "wms.Ввод товара размещение":
                        hashMap.put("ShowScreen", "wms.Ввод количества размещение")
                    elif CurScreen == "wms.Ввод товара приемка факт":
                        hashMap.put("ShowScreen", "wms.Ввод количества факт")    
                    elif CurScreen == "wms.Ввод товара перемещение":
                        hashMap.put("ShowScreen", "wms.Ввод количества взять")        
                    elif CurScreen == "wms.Ввод товара положить":
                        hashMap.put("ShowScreen", "wms.Ввод количества положить")
                    elif CurScreen == "wms.Ввод товара отбор":
                        
                        data_with_ids = json.loads(hashMap.get('data_with_ids'))
                        filtered_data = [item for item in data_with_ids if item.get('sku_id') == hashMap.get('nom_id')]  
                        if not filtered_data:
                            
                            hashMap.put("nom", '')
                            hashMap.put("art", '')
                            hashMap.put("nom_id", '')
                            hashMap.put("unit", '')
                            hashMap.put("toast", 'Указанный товар отсутствует в заказе на отбор') 
                            hashMap.put("ShowScreen", "wms.Ввод товара отбор")

                        else:
                            hashMap.put("ShowScreen", "wms.Ввод количества отбор")    
                else:    
                    hashMap.put("toast", f"Товар с штрихкодом {barcode} не найден")        
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
            
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap  

def on_TableClick(hashMap,_files=None,_data=None):
    
    CurScreen = hashMap.get("current_screen_name")
    listener = hashMap.get("listener")

    if listener == "TableClick":
            
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
                if CurScreen == 'wms.Выбор распоряжения отбор':
                    hashMap.put("ShowScreen", "wms.Ввод адреса отбор")        
                elif CurScreen == 'wms.Выбор распоряжения':    
                    hashMap.put("ShowScreen", "Приемка по заказу начало")
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
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
    hashMap.put("orderRef","86")
    hashMap.put("current_screen_name","wms.Ввод адреса отбор")
    Get_OrderGoods_Data_To_Table(hashMap)
    hashMap.put("barcode","X001OMTDSV")
    # hashMap.put("addr_barcode","1-1-1-1")
    # hashMap.put("current_screen_name","wms.Ввод адреса отбор")
    hashMap.put("listener","barcode")
    hashMap.put("current_screen_name","wms.Ввод товара отбор")
    #hashMap.put("qty","1")
    # hashMap.put("nom_id","86")
    # hashMap.put("ANDROID_ID","380eaecaff29d921")
    ##hashMap.put("addr", 'Полка 1')
    #hashMap.put("nom_id", '86')
    #hashMap.put("unit", "Пиво Оболонь светлое 0.5 л")
    # Get_Orders_Data_To_Table(hashMap)
    on_units_input(hashMap)    
    # print('Содержимое hashMap:', hashMap.store)
    # Set_Var(hashMap)
    #on_input_qtyfact(hashMap)
    # get_operators_placing(hashMap)
    # on_address_input(hashMap)
    #Get_Picking(hashMap)