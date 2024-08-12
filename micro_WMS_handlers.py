from pony.orm.core import db_session
from pony import orm
from pony.orm import Database,Required,Set,Json,PrimaryKey,Optional,select,commit
import datetime

import requests
import json

 # URL вашего PostgREST сервера
#postgrest_url = 'http://176.102.48.128:3000'
postgrest_url = 'http://192.168.1.110:3000'
timeout = 3

def init_on_start(hashMap,_files=None,_data=None):
    init()
    user_locale = hashMap.get("USER_LOCALE")
    return hashMap

def settings_on_create(hashMap,_files=None,_data=None):
    if not hashMap.containsKey("_UserLocale"):
        hashMap.put("get_user_locale","_UserLocale") #get from NoSQL
    else:
        hashMap.put("lang",hashMap.get("_UserLocale")) #set defaul list value
    
    return hashMap 

db = Database()
db.bind(provider='sqlite', filename='//data/data/ru.travelfood.simple_ui/databases/SimpleWMS', create_db=True)

class Record(db.Entity):
        barcode =  Required(str)
        name =  Required(str)
        qty = Required(int)
        
def init():
    db.generate_mapping(create_tables=True)  


def settings_on_input(hashMap,_files=None,_data=None):
    if hashMap.get("listener")=="lang":
        hashMap.put("put_user_locale",hashMap.get("lang"))
        hashMap.put("_UserLocale",hashMap.get("lang")) 

        if hashMap.get("lang")=="Русский":
            hashMap.put("setLocale","ru")   
        elif hashMap.get("lang")=="Українська":
            hashMap.put("setLocale","ua")      
    
    return hashMap 

def get_Permit_On_qty(hashMap, user_locale):
    
    filtered_data = json.loads(hashMap.get('data_with_ids'))
    total_qty = int(hashMap.get("qty"))
    cur_sku_id = hashMap.get("nom_id")
    for row in filtered_data:
        if total_qty == 0:
            break
    
        if row['id'] == int(cur_sku_id):
            total_qty = total_qty - min(total_qty, row['qty'])
            #row['qty'] = row['qty'] - cur_qty            
            
                
    return False if total_qty > 0 else True

def Set_Var(hashMap, _files=None, _data=None):

    CurScreen = hashMap.get("current_screen_name")

    if CurScreen == "wms.Ввод товара по заказу" or CurScreen=="wms.Ввод товара приемка факт" or CurScreen=="wms.Ввод количества факт по заказу" or \
       CurScreen=="wms.Ввод количества взять размещение" or CurScreen=="wms.Ввод количества факт" or CurScreen=="wms.Ввод товара перемещение" or \
       CurScreen=="wms.Ввод товара положить" or CurScreen=="wms.Ввод товара отгрузка" or CurScreen=="wms.Ввод количества отгрузка" or CurScreen=="wms.Ввод товара инвентаризация":
    
        hashMap.put("noaddr", 'true')
    elif CurScreen=="wms.Ввод адреса размещение" or CurScreen=="wms.Ввод адреса инвентаризация" or CurScreen=="wms.Ввод адреса списание":
        hashMap.put("action_str", 'Сканируйте адрес ячейки')
    elif CurScreen=="wms.Ввод количества размещение" or CurScreen=="wms.Ввод количества отбор" or CurScreen == 'wms.Ввод количества списание':
        hashMap.put("noaddr", 'false')
    elif CurScreen=="wms.Ввод адреса":
        hashMap.put("action_str", 'Сканируйте адрес-отправитель')        
    elif CurScreen=="wms.Ввод адреса положить":
        hashMap.put("action_str", 'Сканируйте адрес-получатель')            
    elif CurScreen=="wms.Ввод адреса отбор":
        hashMap.put("action_str", 'Сканируйте адрес ячейки')    
        hashMap.put("NextAddr", 'Нет задания')
    return hashMap

def fill_central_table(data, CurScreen, user_locale):

    if (CurScreen == 'wms.Выбор распоряжения инвентаризация' or CurScreen == 'Приемка по заказу начало'
       or CurScreen == 'wms.Ввод количества факт по заказу' or CurScreen == 'wms.Ввод количества инвентаризация'
       or CurScreen == 'wms.Ввод товара приемка факт'):
        columns = [
        {"name": "nom", "header": "Товар", "weight": "2"},
        {"name": "qty_plan", "header": "План", "weight": "1", "gravity": "center"},
        {"name": "qty_fact", "header": "Факт", "weight": "1", "gravity": "center"}
        ]
        
        if user_locale == 'ru':
            columns.append({"name": "diff",     "header": "Разн.", "weight": "1", "gravity" : "center"})
        elif user_locale == 'ua':   
            columns.append({"name": "diff",     "header": "Різн.", "weight": "1", "gravity" : "center"})
        
        
    elif CurScreen == "wms.Ввод адреса отбор":
        columns = [
        {"name": "nom", "header": "Товар", "weight": "2"},
        ]

        if user_locale == 'ru':
            columns.append({"name": "diff",     "header": "Осталось отобрать", "weight": "1", "gravity" : "center"})
        elif user_locale == 'ua':   
            columns.append({"name": "diff",     "header": "Залишилось відібрати", "weight": "1", "gravity" : "center"})

    elif CurScreen == "wms.Ввод товара отгрузка":
        columns = [
        {"name": "nom", "header": "Товар", "weight": "2"},
        ]

        if user_locale == 'ru':
            columns.append({"name": "diff",     "header": "Осталось отгрузить", "weight": "1", "gravity" : "center"})
        elif user_locale == 'ua':   
            columns.append({"name": "diff",     "header": "Залишилось відвантажити", "weight": "1", "gravity" : "center"})

    j = {
    "type": "table",
    "textsize": "25",
    "hidecaption": "false",
    "hideinterline": "true",
    "borders": "true",
    "columns": columns,
    "rows": [],
    "colorcells": []
    }        

    # Перебор данных и инициализация таблицы j
    for index, row in enumerate(data):
        nom = row["Товар"]
        if (CurScreen == 'wms.Выбор распоряжения инвентаризация' or CurScreen == 'Приемка по заказу начало'
       or CurScreen == 'wms.Ввод количества факт по заказу' or CurScreen == 'wms.Ввод количества инвентаризация'
       or CurScreen == 'wms.Ввод товара приемка факт'):
            qty_plan = row["План"]
            qty_fact = row["Факт"]
            diff =   qty_plan - qty_fact
        elif CurScreen == 'wms.Ввод адреса отбор':
            diff = row["Кол-во"] if user_locale == 'ru' else row["Кіл-ть"]
        elif CurScreen == 'wms.Ввод товара отгрузка':    
            diff = row["Осталось отгрузить"] if user_locale == 'ru' else row["Залишилось відвантажити"]

        
        if (CurScreen == 'wms.Выбор распоряжения инвентаризация' or CurScreen == 'Приемка по заказу начало'
           or CurScreen == 'wms.Ввод количества факт по заказу' or CurScreen == 'wms.Ввод количества инвентаризация'
           or CurScreen == 'wms.Ввод товара приемка факт'):
            # Добавление строки в rows
            j["rows"].append({"nom": nom, "qty_plan": qty_plan, "qty_fact": qty_fact, "diff": diff})

            # Проверка условия для выделения красным цветом
            if diff < 0:
                j["colorcells"].append({"row": str(index), "column": "3", "color": "#d81b60"})
            elif diff > 0:
                j["colorcells"].append({"row": str(index), "column": "3", "color": "#ffff00"})    

        else:
             # Добавление строки в rows
            j["rows"].append({"nom": nom, "diff": diff})

    return j

def Get_Orders_Data_To_Table(hashMap, _files=None, _data=None):
    
    user_locale = hashMap.get("USER_LOCALE")
    CurScreen = hashMap.get("current_screen_name")

    # Путь к нужной таблице или представлению
    if CurScreen == 'wms.Выбор распоряжения':        
        if user_locale == 'ua':
            path = 'wms_orders_captions?and=(typeid.eq.1,or(done.neq.true,done.is.null),manual.neq.true)&select=id:id,Постачальник:contractor,Номер:doc_number'
        elif user_locale == 'ru':
            path = 'wms_orders_captions?and=(typeid.eq.1,or(done.neq.true,done.is.null),manual.neq.true)&select=id:id,Поставщик:contractor,Номер:doc_number'

    elif CurScreen == 'wms.Выбор распоряжения по факту':        
        if user_locale == 'ua':
            path = 'wms_orders_captions?and=(typeid.eq.1,or(done.neq.true,done.is.null),manual.eq.true)&select=id:id,Постачальник:contractor,Номер:doc_number'
        elif user_locale == 'ru':
            path = 'wms_orders_captions?and=(typeid.eq.1,or(done.neq.true,done.is.null),manual.eq.true)&select=id:id,Поставщик:contractor,Номер:doc_number'

    elif CurScreen == 'wms.Выбор распоряжения отбор':
        if user_locale == 'ua':
            path = 'wms_orders_captions?and=(typeid.eq.2,done.is.null,manual.neq.true)&select=id:id,Покупець:contractor,Номер:doc_number'
        elif user_locale == 'ru':
            path = 'wms_orders_captions?and=(typeid.eq.2,done.is.null,manual.neq.true)&select=id:id,Покупатель:contractor,Номер:doc_number'

    elif CurScreen == 'wms.Выбор распоряжения отгрузка':
        if user_locale == 'ua':
            path = 'wms_outgoing?select=id:id,Покупець:contractor,Номер:doc_number'
        elif user_locale == 'ru':
            path = 'wms_outgoing?select=id:id,Покупатель:contractor,Номер:doc_number'

    elif CurScreen == 'wms.Выбор распоряжения инвентаризация':
        path = 'wms_orders_captions?and=(typeid.eq.3,done.is.null)&select=id:id,Склад:contractor,Дата:doc_date_str'
    elif CurScreen == 'wms.Выбор ручного списания':
        path = 'wms_orders_captions?and=(typeid.eq.2,done.is.null,manual.eq.true)&select=id:id,Склад:contractor,Дата:doc_date_str,Номер:description'    

    else:
        hashMap.put("toast", "Ошибка: неизвестный экран")
        return hashMap

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
           Toast_txt_error(hashMap, response)
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')        

    return hashMap    

def Get_OrderGoods_Data_To_Table(hashMap, _files=None, _data=None):

    user_locale = hashMap.get("USER_LOCALE")
    CurScreen = hashMap.get("current_screen_name")
    order_id = hashMap.get("orderRef") 

    # Путь к нужной таблице или представлению
    if CurScreen == 'Приемка по заказу начало' or CurScreen == 'wms.Ввод количества факт по заказу' or CurScreen == 'wms.Ввод товара приемка факт':
        path = f'wms_orders_table?select=id:sku_id,Товар:nom,Артикул:code,План:plan,Факт:fact,manual:manual&order_id=eq.{order_id}'
                
    elif CurScreen == 'wms.Ввод адреса отбор':
        if user_locale == 'ua':
            path = f'rpc/get_picking?orderid={order_id}&select=id:sku_id,Товар:sku,Адреса:address,Кіл-ть:qty,qty:qty'
        elif user_locale == 'ru':
            path = f'rpc/get_picking?orderid={order_id}&select=id:sku_id,Товар:sku,Адрес:address,Кол-во:qty,qty:qty'

    elif CurScreen == 'wms.Ввод товара отгрузка':
        if user_locale == 'ua':
            path = f'wms_outgoing_table?select=id:sku_id,Товар:caption,Артикул:code,Залишилось відвантажити:qty,qty:qty&order_id=eq.{order_id}&qty=neq.0'
        elif user_locale == 'ru':
            path = f'wms_outgoing_table?select=id:sku_id,Товар:caption,Артикул:code,Осталось отгрузить:qty,qty:qty&order_id=eq.{order_id}&qty=neq.0'

    elif CurScreen == 'wms.Выбор распоряжения инвентаризация':
        path = f'rpc/get_inventory_list?orderid={order_id}&select=Товар:nom,План:qty_plan,Факт:qty_fact'

    elif CurScreen == 'wms.Ввод адреса списание':
        if user_locale == 'ua':
            path = f'rpc/get_operators_outgoing_manually?orderid={order_id}&select=id:sku_id,Товар:nom,Комірка:address,Кіл-ть:qty,qty:qty,manual:manual,План:qty,Факт:qty'
        elif user_locale == 'ru':
            path = f'rpc/get_operators_outgoing_manually?orderid={order_id}&select=id:sku_id,Товар:nom,Ячейка:address,Кол-во:qty,qty:qty,manual:manual,,План:qty,Факт:qty'

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
                if 'manual' in item:
                    del item['manual']
                if 'qty' in item:
                    del item['qty']    

            if not CurScreen == 'wms.Ввод адреса списание':
                hashMap.put("central_table", json.dumps(fill_central_table(data,CurScreen,user_locale)))
            
            hashMap.put("data_with_ids", json.dumps(data_with_ids))
            
            if CurScreen == 'Приемка по заказу начало' or CurScreen == 'wms.Ввод товара отгрузка' or CurScreen == 'wms.Ввод количества факт по заказу' or CurScreen == 'wms.Ввод товара приемка факт':
                hashMap.put("table", json.dumps(data))
            elif CurScreen == 'wms.Ввод адреса отбор'  or CurScreen == 'wms.Ввод адреса списание':    
                hashMap.put("addr_table", json.dumps(data))
            elif CurScreen == 'wms.Выбор распоряжения инвентаризация':    
                hashMap.put("table", json.dumps(data))
                hashMap.put("ShowScreen", "wms.Ввод адреса инвентаризация")
            elif CurScreen == 'wms.Ввод адреса списание':
                hashMap.put("addr_table", json.dumps(data))    
                
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def Get_Picking(hashMap, _files=None, _data=None):

    user_locale = hashMap.get("USER_LOCALE")
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
                    hashMap.put("toast", 'Нет данных по пиккингу' if user_locale == 'ru' else 'Нема даних по пікінгу')    
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
                
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def get_operators_placing(hashMap, _files=None, _data=None):

    user_locale = hashMap.get("USER_LOCALE")
    user = 'К РАЗМЕЩЕНИЮ' 
    # Путь к нужной таблице или представлению
    if user_locale == 'ua':
        path = f'rpc/get_operators_placing?user_id={user}&select=id:sku_id,Товар:nom,Кіл-ть:qty,order_id:id,qty:qty'
    elif user_locale == 'ru':
        path = f'rpc/get_operators_placing?user_id={user}&select=id:sku_id,Товар:nom,Кол-во:qty,order_id:id,qty:qty'
    
    # Полный URL для запроса
    url = f'{postgrest_url}/{path}'

    try:
        # Логирование перед отправкой запроса
        
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
                if 'order_id' in item:
                    del item['order_id']
                if 'qty' in item:
                    del item['qty']    
 
            hashMap.put("data_with_ids", json.dumps(data_with_ids))
            hashMap.put("table", json.dumps(data))

        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def get_placement_orders(hashMap, _files=None, _data=None):

    user_locale = hashMap.get("USER_LOCALE")
    user = hashMap.get("ANDROID_ID") 
    # Путь к нужной таблице или представлению
    if user_locale == 'ua':
        path = f'rpc/get_placement_orders?user_id={user}&select=Товар:sku,Комірка:address,Кіл-ть:qty,id:sku_id,order_id:order_id,qty:qty'
    elif user_locale == 'ru':
        path = f'rpc/get_placement_orders?user_id={user}&select=Товар:sku,Ячейка:address,Кол-во:qty,id:sku_idorder_id:order_id,qty:qty'
            
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
                if 'order_id' in item:
                    del item['order_id']
                if 'qty' in item:
                    del item['qty']    
            
            hashMap.put("data_with_ids", json.dumps(data_with_ids))            
            hashMap.put("table", json.dumps(data))
                        
            hashMap.put("addr_table", json.dumps(data))            
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
            
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

def get_goods_for_address_placement(hashMap, _files=None, _data=None):

    user_locale = hashMap.get("USER_LOCALE")
    user = hashMap.get("ANDROID_ID") 
    address = hashMap.get("addr_id") 
    # Путь к нужной таблице или представлению
    if user_locale == 'ua':
        path = f'rpc/get_goods_for_address_placement?user_id={user}&address_id={address}&select=Товар:sku,Кіл-ть:qty'
    elif user_locale == 'ru':
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

    user_locale = hashMap.get("USER_LOCALE")
    user = hashMap.get("ANDROID_ID") 
    # Путь к нужной таблице или представлению
    if user_locale == 'ua':
        path = f'rpc/get_operators_moving?user_id={user}&select=Товар:nom,Кіл-ть:qty'
    elif user_locale == 'ru':
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
    elif CurScreen == "wms.Ввод товара положить":
        hashMap.put("ShowScreen", "wms.Ввод адреса")        
    elif CurScreen == "wms.Ввод количества положить":
        hashMap.put("ShowScreen", "wms.Ввод товара положить")
    elif CurScreen == "wms.Ввод товара отбор":
        hashMap.put("ShowScreen", "wms.Ввод адреса отбор")
    elif CurScreen=="wms.Ввод количества отбор":
        hashMap.put("ShowScreen", "wms.Ввод товара отбор")
    elif CurScreen=="wms.Ввод товара отгрузка":
        hashMap.put("ShowScreen", "wms.Выбор распоряжения отгрузка")
    elif CurScreen=="wms.Ввод количества отгрузка":
        hashMap.put("ShowScreen", "wms.Ввод товара отгрузка")
    elif CurScreen=="wms.Ввод товара инвентаризация":
        hashMap.put("ShowScreen", "wms.Ввод адреса инвентаризация")
    elif CurScreen=="wms.Ввод товара списание":
        hashMap.put("ShowScreen", "wms.Ввод адреса списание")    
    elif CurScreen=="wms.Ввод количества списание":
        hashMap.put("ShowScreen", "wms.Ввод товара списание")    
    elif CurScreen=="Приемка по заказу начало":
        hashMap.put("ShowScreen", "wms.Выбор распоряжения")
    elif CurScreen=="wms.Ввод товара по заказу":
        hashMap.put("ShowScreen", "Приемка по заказу начало")    
    elif CurScreen=="wms.Ввод товара по заказу":
        hashMap.put("ShowScreen", "wms.Ввод количества факт по заказу")
    elif CurScreen=="wms.Данные приходной накладной":
        hashMap.put("ShowScreen", "wms.Выбор распоряжения по факту")
    elif CurScreen=="wms.Ввод товара приемка факт":
        hashMap.put("ShowScreen", "wms.Выбор распоряжения по факту")
    elif CurScreen=="wms.Ввод количества факт":
        hashMap.put("ShowScreen", "wms.Выбор распоряжения по факту")            

    elif CurScreen=="wms.Ввод товара перемещение":
        hashMap.put("ShowScreen", "wms.Ввод адреса")            
    elif CurScreen=="wms.Ввод количества факт":
        hashMap.put("ShowScreen", "wms.Выбор распоряжения по факту")            


    return hashMap 

def on_FORVARD_BUTTON(hashMap, _files=None, _data=None):

    listener = hashMap.get("listener")
    CurScreen = hashMap.get("current_screen_name")
    if CurScreen == "Приемка по заказу начало" and listener is None:
        hashMap.put("ShowScreen", "wms.Ввод товара по заказу")
    elif CurScreen == "wms.Ввод количества факт" and listener is None:
        on_input_qtyfact(hashMap)        
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

    CurScreen = hashMap.get("current_screen_name")
    user_locale = hashMap.get("USER_LOCALE")
    Doc_Updated = hashMap.get("Doc_Updated")
    
    if Doc_Updated == None or Doc_Updated == 'False':
        if user_locale == 'ua':
            hashMap.put("toast", 'Документ не оновлено у БУ базі. Спробуйте ще раз')
        elif user_locale == 'ru':
            hashMap.put("toast", 'Документ не обновлен в БУ базе. ПОпробуйте позже')
        return hashMap
    
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
            
            if CurScreen == 'wms.Ввод адреса инвентаризация':
                on_input_qtyfact(hashMap)            
            
            if user_locale == 'ua':
                hashMap.put("toast", 'Документ завершено')
            elif user_locale == 'ru':
                hashMap.put("toast", 'Документ завершен')
            hashMap.put("FinishProcess","")        
        else:
            hashMap.put("toast", f'Error: {response.status_code}')
                
    except Exception as e:
        hashMap.put("toast", f'Exception occurred: {str(e)}')
    
    return hashMap

def on_address_input(hashMap,_files=None,_data=None):
    
    user_locale = hashMap.get("USER_LOCALE")
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
                    elif CurScreen == 'wms.Ввод адреса инвентаризация':
                        hashMap.put("ShowScreen", "wms.Ввод товара инвентаризация")
                    elif CurScreen == 'wms.Ввод адреса списание':
                        hashMap.put("ShowScreen", "wms.Ввод товара списание")
                        
                else:    
                    if user_locale == 'ua':
                        hashMap.put("toast", f"Комірку з штрихкодом {barcode} не знайдено")
                    elif user_locale == 'ru':
                        hashMap.put("toast", f"Ячейка с штрихкодом {barcode} не найдена")
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
            
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')
    
    return hashMap

def on_input_qtyfact(hashMap,_files=None,_data=None):

    user_locale = hashMap.get("USER_LOCALE")
    no_order = not hashMap.get("orderRef")
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
            "no_order": str(no_order),
            "qty": hashMap.get("qty"),
            "sku_id": hashMap.get("nom_id"),
            "user": hashMap.get("ANDROID_ID"),
            "address_id": "К РАЗМЕЩЕНИЮ",
            "order_id": hashMap.get("orderRef"),
            "to_operation": "1"
            }

            try:
                # Отправка GET-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    Get_OrderGoods_Data_To_Table(hashMap)
                    hashMap.put("ShowScreen", "wms.Ввод товара по заказу")
                else:
                    Toast_txt_error(hashMap, response)       
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')
        elif listener == "BACK_BUTTON":
            hashMap.put("ShowScreen", "wms.Ввод товара по заказу")

    elif CurScreen == "wms.Ввод количества взять размещение":

        if listener is None:
            
            # Путь к нужной таблице или представлению
            path = 'wms_operations'
            
            # Полный URL для запроса
            url = f'{postgrest_url}/{path}'

            # Заголовки для запроса
            headers = {
            'Content-Type': 'application/json'
            }
            
            permit = get_Permit_On_qty(hashMap, user_locale)
            if permit:
                
                hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))
           
                #Параметры запроса (например, фильтрация данных)
                data = {
                "order_id": str(order_id),    
                "no_order": str(order_id is None),
                "qty": hashMap.get("qty_minus"),
                "sku_id": hashMap.get("nom_id"),
                "user": hashMap.get("ANDROID_ID"),
                "address_id": "К РАЗМЕЩЕНИЮ",
                "to_operation": "1"                
                }

                try:
                    # Отправка GET-запроса
                    response = requests.post(url, json=data, timeout=timeout)

                    # Проверка статуса ответа
                    if response.status_code == 201:
                        
                        #Параметры запроса (например, фильтрация данных)
                        data = {
                        "no_order": str(no_order),
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
                                Toast_txt_error(hashMap, response)       
                        except Exception as e:
                            hashMap.put("toast", f'Exception occurred: {str(e)}')
                        
                    else:
                        Toast_txt_error(hashMap, response)
                except Exception as e:
                    hashMap.put("toast", f'Exception occurred: {str(e)}')
            else:
                if user_locale == 'ua':
                    hashMap.put("toast", 'Не можна перевищувати кількість до відбору')
                elif user_locale == 'ru':
                    hashMap.put("toast", 'Нельзя превышать количество к отбору') 
            
    elif CurScreen == "wms.Ввод количества размещение":

        if listener is None:
        
            permit = get_Permit_On_qty(hashMap, user_locale)
            if permit:
                
                #hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))
                
                # Путь к нужной таблице или представлению
                path = 'wms_operations'
                
                # Полный URL для запроса
                url = f'{postgrest_url}/{path}'

                # Заголовки для запроса
                headers = {
                'Content-Type': 'application/json'
                }
                
                try:
                    
                    total_qty = int(hashMap.get("qty"))
                    nom_id = hashMap.get("nom_id")
                    data_with_ids = json.loads(hashMap.get('data_with_ids'))
                    for item in data_with_ids:
                        if total_qty == 0:
                            break
                        
                        if item['id'] == int(nom_id):
                            order_id = item['order_id']
                            no_order = not order_id
                            cur_qty = min(item['qty'],total_qty)
                            total_qty = total_qty - cur_qty

                            data = {
                            "order_id": str(order_id),
                            "no_order": str(no_order),
                            "qty": str(-cur_qty),
                            "sku_id": hashMap.get("nom_id"),
                            "user": hashMap.get("ANDROID_ID"),
                            "address_id": hashMap.get("ANDROID_ID"),
                            "to_operation": "1"
                            }
                                            
                            # Отправка POST-запроса
                            response = requests.post(url, json=data, timeout=timeout)

                            # Проверка статуса ответа
                            if not response.status_code == 201:
                                Toast_txt_error(hashMap, response)
                                return hashMap

                except Exception as e:
                    hashMap.put("toast", f'Exception occurred: {str(e)}')

                #Параметры запроса (например, фильтрация данных)
                data = {
                    "no_order": 'true',
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
                        Toast_txt_error(hashMap, response)       
                except Exception as e:
                    hashMap.put("toast", f'Exception occurred: {str(e)}')                                     
            else:
                if user_locale == 'ua':
                    hashMap.put("toast", 'Не можна перевищувати кількість до розміщення')
                elif user_locale == 'ru':
                    hashMap.put("toast", 'Нельзя превышать количество к размещению')    

    elif CurScreen == "wms.Ввод количества факт":

        if listener is None:
        
            order_id = int(hashMap.get("orderRef"))
            nom_id = int(hashMap.get("nom_id"))
            ANDROID_ID = hashMap.get("ANDROID_ID")

            # Заголовки для запроса
            headers = {
            'Content-Type': 'application/json'
            }           
            
            #----------------------wms_orders
            path = 'wms_orders'
            path_get = f'{path}?order_id=eq.{order_id}&sku_id=eq.{nom_id}&qty_fact=is.null'
                        
            url = f'{postgrest_url}/{path}'
            url_get = f'{postgrest_url}/{path_get}'
            
            #Параметры запроса (например, фильтрация данных)
            data = {
            "sku_id": hashMap.get("nom_id"),
            "qty_plan": hashMap.get("qty_plan"),
            "order_id": str(order_id)
            }

            try:
                # Проверка существования записи
                get_response = requests.get(url_get, headers=headers, timeout=timeout)
                
                if get_response.status_code == 200 and get_response.json():
                    
                    existing_record = get_response.json()[0]  # Предполагаем, что возвращается список
                    record_id = existing_record['id']
                    
                    # Запись существует, выполняем PATCH-запрос для обновления записи
                    patch_data = {
                        "qty_plan": hashMap.get("qty_plan")
                    }
                    patch_url = f'{postgrest_url}/{path}?order_id=eq.{order_id}&sku_id=eq.{nom_id}&id=eq.{record_id}'
                    response = requests.patch(patch_url, json=patch_data, headers=headers, timeout=timeout)
                    if not (response.status_code == 200 or response.status_code == 204):
                        Toast_txt_error(hashMap, response)
                        return hashMap
                elif get_response.status_code == 404 or not get_response.json():
                    # Запись не существует, выполняем POST-запрос для создания новой
                    response = requests.post(url, json=data, headers=headers, timeout=timeout)
                    if not response.status_code == 201:
                        Toast_txt_error(hashMap, response)
                        return hashMap
                else:
                    Toast_txt_error(hashMap, response)
                    return hashMap
                    
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')
                return hashMap

            #----------------------wms_operations
            # Путь к нужной таблице или представлению
            path = 'wms_operations'
            path_get = f'{path}?order_id=eq.{order_id}&no_order=eq.{no_order}&sku_id=eq.{nom_id}&user=eq.{ANDROID_ID}&address_id=eq.{ANDROID_ID}&to_operation=eq.1'

            # Полный URL для запроса
            url = f'{postgrest_url}/{path}'
            url_get = f'{postgrest_url}/{path_get}'

            #Параметры запроса (например, фильтрация данных)
            data = {
            "order_id": str(order_id),
            "no_order": str(no_order),
            "qty": hashMap.get("qty"),
            "sku_id": str(nom_id),
            "user": ANDROID_ID,
            "address_id": ANDROID_ID,
            "to_operation": "1"
            }
            
            try:
                # Проверка существования записи
                get_response = requests.get(url_get, headers=headers, timeout=timeout)
                
                if get_response.status_code == 200 and get_response.json():
                    # Запись существует, выполняем PATCH-запрос для обновления записи
                    patch_data = {
                        "qty": hashMap.get("qty")
                    }
                    patch_url = f'{postgrest_url}/{path}?order_id=eq.{order_id}&no_order=eq.{no_order}&sku_id=eq.{nom_id}&user=eq.{ANDROID_ID}&address_id=eq.{ANDROID_ID}&to_operation=eq.1'
                    response = requests.patch(patch_url, json=patch_data, headers=headers, timeout=timeout)
                    if response.status_code == 200 or response.status_code == 204:
                        hashMap.put("ShowScreen", "wms.Ввод товара приемка факт")
                    else:
                        Toast_txt_error(hashMap, response)
                elif get_response.status_code == 404 or not get_response.json():
                    # Запись не существует, выполняем POST-запрос для создания новой
                    response = requests.post(url, json=data, headers=headers, timeout=timeout)
                    if response.status_code == 201:
                        hashMap.put("ShowScreen", "wms.Ввод товара приемка факт")
                    else:
                        Toast_txt_error(hashMap, response)
                else:
                    Toast_txt_error(hashMap, response)
                    
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
            "no_order": str(no_order),
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
                    "no_order": str(no_order),
                    "qty": hashMap.get("qty"),
                    "sku_id": hashMap.get("nom_id"),
                    "user": hashMap.get("ANDROID_ID"),
                    "address_id": hashMap.get("ANDROID_ID"),
                    "to_operation": "5"
                    }
                    
                    try:
                        # Отправка GET-запроса
                        response = requests.post(url, json=data, timeout=timeout)

                        # Проверка статуса ответа
                        if response.status_code == 201:
                            hashMap.put("ShowScreen", "wms.Ввод адреса")
                        else:
                            Toast_txt_error(hashMap, response)       
                    except Exception as e:
                        hashMap.put("toast", f'Exception occurred: {str(e)}')
                    
                else:
                    Toast_txt_error(hashMap, response)
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
            "no_order": str(no_order),
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
                    "no_order": str(no_order),
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
                            Toast_txt_error(hashMap, response)       
                    except Exception as e:
                        hashMap.put("toast", f'Exception occurred: {str(e)}')
                    
                else:
                    Toast_txt_error(hashMap, response)
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')            

    elif CurScreen == "wms.Ввод количества отбор":

        if listener is None:
            
            permit = get_Permit_On_qty(hashMap, user_locale)
            if permit:

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
                "no_order": 'true',
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
                        "no_order": str(no_order),
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
                                Toast_txt_error(hashMap, response)       
                        except Exception as e:
                            hashMap.put("toast", f'Exception occurred: {str(e)}')
                        
                    else:
                        Toast_txt_error(hashMap, response)
                except Exception as e:
                    hashMap.put("toast", f'Exception occurred: {str(e)}')

            else:        
                if user_locale == 'ua':
                    hashMap.put("toast", 'Не можна перевищувати кількість до відбору')
                elif user_locale == 'ru':
                    hashMap.put("toast", 'Нельзя превышать количество к отбору')

    elif CurScreen == "wms.Ввод количества отгрузка":

        if listener is None:
        
            permit = get_Permit_On_qty(hashMap, user_locale)
            if permit:
                        
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
                "no_order": str(no_order),
                "qty": hashMap.get("qty_minus"),
                "sku_id": hashMap.get("nom_id"),
                "user": hashMap.get("ANDROID_ID"),
                "order_id": hashMap.get("orderRef"),
                "address_id": 'ОТБОР'
                }

                try:
                    # Отправка POST-запроса
                    response = requests.post(url, json=data, timeout=timeout)

                    # Проверка статуса ответа
                    if response.status_code == 201:
                        hashMap.put("ShowScreen", "wms.Ввод товара отгрузка")                                        
                    else:
                        Toast_txt_error(hashMap, response)
                except Exception as e:
                    hashMap.put("toast", f'Exception occurred: {str(e)}')
            else:        
                if user_locale == 'ua':
                    hashMap.put("toast", 'Не можна перевищувати кількість відібраного по замовленню')
                elif user_locale == 'ru':
                    hashMap.put("toast", 'Нельзя превышать количество отобранного по заказу')

    elif CurScreen == "wms.Ввод количества инвентаризация":

        if listener is None:
        
            # Путь к нужной таблице или представлению
            path = 'wms_inventory'
            
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
            "order_id": hashMap.get("orderRef"),
            "address_id": hashMap.get("addr_id")
            }

            try:
                # Отправка POST-запроса
                response = requests.post(url, json=data, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 201:
                    
                    path = f'rpc/get_inventory_list?orderid={hashMap.get("orderRef")}&select=Товар:nom,План:qty_plan,Факт:qty_fact'
            
                    # Полный URL для запроса
                    url = f'{postgrest_url}/{path}'
                    
                    # Отправка GET-запроса
                    response = requests.get(url, timeout=timeout)

                    # Проверка статуса ответа
                    if response.status_code == 200:
                        # Парсинг JSON ответа
                        data = response.json()

                        hashMap.put("table", json.dumps(data))
                        hashMap.put("central_table", json.dumps(fill_central_table(data,CurScreen,user_locale)))
                        hashMap.put("ShowScreen", "wms.Ввод адреса инвентаризация")
                            
                    else:
                        hashMap.put("toast", f'Error: {response.status_code}')
                    
                else:
                    Toast_txt_error(hashMap, response)       
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')            
  
    elif CurScreen == "wms.Ввод адреса инвентаризация":

        if listener == 'btn_done':
            
            order_id = hashMap.get("orderRef")
            path = f'rpc/get_finished_inventory_list?orderid={order_id}&select=sku_id:sku_id,address_id:address_id,qty:qty'

            url = f'{postgrest_url}/{path}'

            try:
                
                # Отправка GET-запроса
                response = requests.get(url, timeout=timeout)

                # Проверка статуса ответа
                if response.status_code == 200:
                    # Парсинг JSON ответа
                    data = response.json()
                        
                else:
                    hashMap.put("toast", f'Error: {response.status_code}')
                    return hashMap
                    
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')
                return hashMap

            # Путь к нужной таблице или представлению
            path = 'wms_operations'
            
            # Полный URL для запроса
            url = f'{postgrest_url}/{path}'

            # Заголовки для запроса
            headers = {
            'Content-Type': 'application/json'
            }
            
            for row in data:

                # #Параметры запроса (например, фильтрация данных)
                data = {
                "qty": row["qty"],
                "sku_id": row["sku_id"],
                "user": hashMap.get("ANDROID_ID"),
                "address_id": row["address_id"],
                "no_order": 'true'
                }

                try:
                    # Отправка POST-запроса
                    response = requests.post(url, json=data, timeout=timeout)

                    # Проверка статуса ответа
                    if not response.status_code == 201:
                        Toast_txt_error(hashMap, response)       
                except Exception as e:
                    hashMap.put("toast", f'Exception occurred: {str(e)}')

    elif CurScreen == "wms.Ввод количества списание":

        if listener is None:            
            order_id = hashMap.get("orderRef")
            hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))

            path = 'wms_orders'
            url = f'{postgrest_url}/{path}'
            
            # Заголовки для запроса
            headers = {
            'Content-Type': 'application/json'
            }

            #Параметры запроса (например, фильтрация данных)
            data = {
            "sku_id": hashMap.get("nom_id"),
            "qty_plan": str(hashMap.get("qty")),
            "qty_fact": str(hashMap.get("qty")),
            "order_id": str(order_id)
            }

            try:
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
                if not response.status_code == 201:
                    Toast_txt_error(hashMap, response)
                    return hashMap
                    
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')
                return hashMap


            #---------------------------------    
            # Путь к нужной таблице или представлению
            path = 'wms_operations'
                
            # Полный URL для запроса
            url = f'{postgrest_url}/{path}'
    
            #Параметры запроса (например, фильтрация данных)
            data = {
            "order_id": order_id,
            "no_order": 'true',
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
                    hashMap.put("ShowScreen", "wms.Ввод адреса списание")
                else:
                    Toast_txt_error(hashMap, response)
                        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')
            order_id = hashMap.get("orderRef")
            hashMap.put("qty_minus", str(-1*int(hashMap.get("qty"))))

            path = 'wms_orders'
            url = f'{postgrest_url}/{path}'
            
            # Заголовки для запроса
            headers = {
            'Content-Type': 'application/json'
            }

            #Параметры запроса (например, фильтрация данных)
            data = {
            "sku_id": hashMap.get("nom_id"),
            "qty_plan": str(hashMap.get("qty")),
            "qty_fact": str(hashMap.get("qty")),
            "order_id": str(order_id)
            }

            try:
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
                if not response.status_code == 201:
                    Toast_txt_error(hashMap, response)
                    return hashMap
                    
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')
                return hashMap


            #---------------------------------    
            # Путь к нужной таблице или представлению
            path = 'wms_operations'
                
            # Полный URL для запроса
            url = f'{postgrest_url}/{path}'
    
            #Параметры запроса (например, фильтрация данных)
            data = {
            "order_id": order_id,
            "no_order": 'true',
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
                    hashMap.put("ShowScreen", "wms.Ввод адреса списание")
                else:
                    Toast_txt_error(hashMap, response)
                        
            except Exception as e:
                hashMap.put("toast", f'Exception occurred: {str(e)}')

    hashMap.put('qty_plan', '')
    hashMap.put('qty', '')

    return hashMap 

def Toast_txt_error(hashMap, response):
    error_message = response.json().get('message', response.text)
    hashMap.put("toast", f'Error: {response.status_code}, Message: {error_message}')

def on_units_input(hashMap,_files=None,_data=None):
    
    user_locale = hashMap.get("USER_LOCALE")
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
                        
                        data_with_ids = json.loads(hashMap.get('data_with_ids'))
                        filtered_data = [item for item in data_with_ids if item['id'] == jrecord['id']]  
                        if not filtered_data:
                            
                            hashMap.put("nom", '')
                            hashMap.put("art", '')
                            hashMap.put("nom_id", '')
                            hashMap.put("unit", '')
                            if user_locale == 'ua':
                                hashMap.put("toast", 'Вказаний товар відсутній у списку на забір для розміщення') 
                            elif user_locale == 'ru':
                                hashMap.put("toast", 'Указанный товар отсутствует в списке на забор для размещения') 
                            hashMap.put("ShowScreen", "wms.Ввод товара размещение взять")
                        else:
                            hashMap.put("filtered_data", json.dumps(filtered_data))
                            hashMap.put("ShowScreen", "wms.Ввод количества взять размещение")
                    elif CurScreen == "wms.Ввод товара размещение":
                        data_with_ids = json.loads(hashMap.get('data_with_ids'))
                        filtered_data = [item for item in data_with_ids if item['id'] == jrecord['id']]  
                        if not filtered_data:
                            
                            hashMap.put("nom", '')
                            hashMap.put("art", '')
                            hashMap.put("nom_id", '')
                            hashMap.put("unit", '')
                            if user_locale == 'ua':
                                hashMap.put("toast", 'Вказаний товар відсутній у списку на розміщення') 
                            elif user_locale == 'ru':
                                hashMap.put("toast", 'Указанный товар отсутствует в списке на размещение') 
                            hashMap.put("ShowScreen", "wms.Ввод товара размещение")
                        else:
                            hashMap.put("ShowScreen", "wms.Ввод количества размещение")
                    elif CurScreen == "wms.Ввод товара приемка факт":
                        hashMap.put("ShowScreen", "wms.Ввод количества факт")
                    elif CurScreen == "wms.Ввод товара перемещение":
                        hashMap.put("ShowScreen", "wms.Ввод количества взять")        
                    elif CurScreen == "wms.Ввод товара положить":
                        hashMap.put("ShowScreen", "wms.Ввод количества положить")
                    elif CurScreen == "wms.Ввод товара отбор" or CurScreen == "wms.Ввод товара отгрузка":
 
                        data_with_ids = json.loads(hashMap.get('data_with_ids'))
                        if CurScreen == "wms.Ввод товара отбор":
                            filtered_data = [item for item in data_with_ids if item['id'] == jrecord['id'] and item['Адрес' if user_locale == 'ru' else 'Адреса'] == hashMap.get('addr_id')]  
                        else:    
                            filtered_data = [item for item in data_with_ids if item['id'] == jrecord['id']]  
                        if not filtered_data:
                            
                            hashMap.put("nom", '')
                            hashMap.put("art", '')
                            hashMap.put("nom_id", '')
                            hashMap.put("unit", '')
                            if CurScreen == "wms.Ввод товара отбор":
                                if user_locale == 'ua':
                                    hashMap.put("toast", 'Товар не відповідає вказаній комірці') 
                                elif user_locale == 'ru':
                                    hashMap.put("toast", 'Товар не соответствует указанной ячейке') 
                                hashMap.put("ShowScreen", "wms.Ввод товара отбор")
                            else:
                                if user_locale == 'ua':
                                    hashMap.put("toast", 'Товар відсутній у заказі на відбір') 
                                elif user_locale == 'ru':
                                    hashMap.put("toast", 'Товар отсутствует в заказе на отбор') 
                                hashMap.put("ShowScreen", "wms.Ввод товара отбор")

                        else:
                            if CurScreen == "wms.Ввод товара отбор":
                                hashMap.put("ShowScreen", "wms.Ввод количества отбор")
                            elif CurScreen == "wms.Ввод товара отгрузка":
                                hashMap.put("ShowScreen", "wms.Ввод количества отгрузка")        
                    elif CurScreen == 'wms.Ввод товара списание':
                        hashMap.put("ShowScreen", "wms.Ввод количества списание")        
                    elif CurScreen == "wms.Ввод товара инвентаризация":
                        hashMap.put("ShowScreen", "wms.Ввод количества инвентаризация")

                else:    
                    if user_locale == 'ua':
                        hashMap.put("toast", f"Товар з штрихкодом {barcode} не знайдено")        
                    elif user_locale == 'ru':
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
                hashMap.put("orderIsManual", str(jrecord['manual']))
                if CurScreen == 'wms.Выбор распоряжения отбор':
                    hashMap.put("ShowScreen", "wms.Ввод адреса отбор")        
                elif CurScreen == 'wms.Выбор распоряжения':    
                    hashMap.put("ShowScreen", "Приемка по заказу начало")
                elif CurScreen == 'wms.Выбор распоряжения отгрузка':    
                    hashMap.put("ShowScreen", "wms.Ввод товара отгрузка")
                elif CurScreen == 'wms.Выбор ручного списания':    
                    hashMap.put("ShowScreen", "wms.Ввод адреса списание")
                elif CurScreen == 'wms.Выбор распоряжения по факту':    
                    hashMap.put("ShowScreen", "wms.Ввод товара приемка факт")    
            else:
                hashMap.put("toast", f'Error: {response.status_code}')
        except Exception as e:
            hashMap.put("toast", f'Exception occurred: {str(e)}')
        
    return hashMap

# #Пример использования функции
# class MockHashMap:
#     def __init__(self):
#         self.store = {}

#     def put(self, key, value):
#         self.store[key] = value

#     def get(self, key, default=None):
#        return self.store.get(key, default)

# #Тестирование функции
# if __name__ == "__main__":
#     hashMap = MockHashMap()
    
#     hashMap.put("ANDROID_ID","380eaecaff29d921")
#     hashMap.put("USER_LOCALE","ua")
#     hashMap.put("orderRef","263")
#     hashMap.put("listener",None)
#     hashMap.put("current_screen_name","wms.Ввод количества списание")
#     hashMap.put("nom_id","95")
#     hashMap.put("qty","1")
#     on_input_qtyfact(hashMap)
    