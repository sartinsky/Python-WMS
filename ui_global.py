from pony import orm
from pony.orm import Database,Required,Set,Json,PrimaryKey,Optional
from pony.orm.core import db_session
import datetime

db = Database()
db.bind(provider='sqlite', filename='//data/data/ru.travelfood.simple_ui/databases/SimpleWMS', create_db=True)

class WmsAddresses(db.Entity):
    _table_ = "wms_addresses"
    id = PrimaryKey(str, max_len=25)
    simple_order = Optional(int)
    max_volume = Optional(float)
    max_qty = Optional(float)
    max_weight = Optional(float)
    barcode = Optional(str, max_len=128)
    caption = Optional(str)
    not_for_picking = Optional(bool)
    allowed_places = Set('WmsAllowedPlaces', reverse="address")
    distances_src = Set('WmsDistances', reverse="address_source")
    distances_dest = Set('WmsDistances', reverse="address_dest")

class WmsGoods(db.Entity):
    _table_ = "wms_goods"
    id = PrimaryKey(int, auto=True)
    code = Optional(str, max_len=50)
    caption = Optional(str, max_len=150)
    weight = Optional(float)
    volume = Optional(float)
    unit_str = Optional(str)
    barcodes = Set('WmsGoodsBarcodes')
    allowed_places = Set('WmsAllowedPlaces', reverse="sku")

class WmsGoodsBarcodes(db.Entity):
    _table_ = "wms_goods_barcodes"
    id = PrimaryKey(int, auto=True)
    goods = Required(WmsGoods, column="goods_id", on_delete="CASCADE")
    barcode = Required(str, max_len=128)
    unit_str = Optional(str)
    composite_key(goods, barcode)

class WmsAllowedPlaces(db.Entity):
    _table_ = "wms_allowed_places"
    sku = Required(WmsGoods, column="sku_id", on_delete="CASCADE")
    address = Required(WmsAddresses, column="address", on_delete="CASCADE")
    composite_key(sku, address)

class WmsDistances(db.Entity):
    _table_ = "wms_distances"
    address_source = Required(WmsAddresses, column="address_source")
    address_dest = Required(WmsAddresses, column="address_dest")
    distance = Optional(float)

class WmsOperations(db.Entity):
    _table_ = "wms_operations"
    sku_id = Required(int)
    address_id = Optional(str, max_len=25)
    qty = Optional(float)
    created_at = Optional(datetime.datetime, default=datetime.datetime.now)
    order_id = Optional(int)
    no_order = Optional(bool)
    user = Optional(str, max_len=50)
    to_operation = Optional(int)

class WmsTotals(db.Entity):
    _table_ = "wms_totals"
    sku_id = Required(int)
    address_id = Required(str, max_len=25)
    total = Optional(float)
    to_operation = Optional(int)
    composite_key(sku_id, address_id)

class WmsOrders(db.Entity):
    _table_ = "wms_orders"
    id = PrimaryKey(int, auto=True)
    sku_id = Optional(int)
    qty_plan = Optional(float)
    qty_fact = Optional(float)
    done = Optional(bool)
    order_id = Optional(int)
    line_id = Optional(str, max_len=100)
    composite_key(order_id, line_id)

@db_session
def create_triggers_and_procedures():
    # Проверка и создание функции wms_caculate_totals
    db.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'wms_caculate_totals') THEN
            CREATE OR REPLACE FUNCTION wms_caculate_totals()
            RETURNS trigger
            LANGUAGE 'plpgsql'
            AS $BODY$
            BEGIN 
                LOCK TABLE wms_totals IN EXCLUSIVE MODE;

                -- Обработка INSERT
                IF tg_op = 'INSERT' THEN
                    BEGIN
                        INSERT INTO wms_totals (sku_id, address_id, total)
                        VALUES
                        (
                            NEW.sku_id,
                            NEW.address_id,
                            NEW.qty
                        ) 
                        ON CONFLICT (sku_id, address_id) 
                        DO UPDATE
                        SET total = wms_totals.total + EXCLUDED.total;

                        -- Проверка на отрицательный остаток
                        IF (SELECT total FROM wms_totals WHERE sku_id = NEW.sku_id AND address_id = NEW.address_id) < 0 THEN
                            RAISE EXCEPTION 'Не можна перевищувати залишок';
                        END IF;
                    EXCEPTION
                        WHEN unique_violation THEN
                            UPDATE wms_totals
                            SET total = wms_totals.total + NEW.qty
                            WHERE sku_id = NEW.sku_id AND address_id = NEW.address_id;

                            -- Проверка на отрицательный остаток
                            IF (SELECT total FROM wms_totals WHERE sku_id = NEW.sku_id AND address_id = NEW.address_id) < 0 THEN
                                RAISE EXCEPTION 'Не можна перевищувати залишок';
                            END IF;
                    END;

                -- Обработка UPDATE
                ELSIF tg_op = 'UPDATE' THEN
                    BEGIN
                        UPDATE wms_totals
                        SET total = wms_totals.total + (NEW.qty - OLD.qty)
                        WHERE sku_id = NEW.sku_id AND address_id = NEW.address_id;

                        IF (SELECT total FROM wms_totals WHERE sku_id = NEW.sku_id AND address_id = NEW.address_id) < 0 THEN
                            RAISE EXCEPTION 'Не можна перевищувати залишок';
                        END IF;
                    END;

                -- Обработка DELETE
                ELSIF tg_op = 'DELETE' THEN
                    BEGIN
                        UPDATE wms_totals
                        SET total = wms_totals.total - OLD.qty
                        WHERE sku_id = OLD.sku_id AND address_id = OLD.address_id;
                    END;

                ELSE
                    RAISE EXCEPTION '% в wms_operations предполагаются только INSERT, UPDATE или DELETE', tg_op;
                END IF;

                RETURN NEW;
            END;
            $BODY$;
        END IF;
    END;
    $$;
    """)

    # Проверка и создание триггера calculate_total
    db.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'calculate_total') THEN
            CREATE TRIGGER calculate_total
            AFTER INSERT OR UPDATE OR DELETE
            ON wms_operations
            FOR EACH ROW
            EXECUTE FUNCTION wms_caculate_totals();
        END IF;
    END;
    $$;
    """)

    # Проверка и создание функции add_fact_to_order
    db.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'add_fact_to_order') THEN
            CREATE OR REPLACE FUNCTION add_fact_to_order()
            RETURNS trigger
            LANGUAGE 'plpgsql'
            AS $BODY$
            BEGIN
               IF (TG_OP = 'INSERT') THEN
                   IF (NEW.order_id > 0 AND NEW.qty > 0) THEN
                       INSERT INTO wms_orders(sku_id, qty_fact, order_id)
                       VALUES (NEW.sku_id, NEW.qty, NEW.order_id);
                   END IF;
               ELSIF (TG_OP = 'UPDATE') THEN
                   IF (NEW.order_id > 0 AND NEW.qty > 0) THEN
                       PERFORM 1 FROM wms_orders
                       WHERE sku_id = NEW.sku_id AND order_id = NEW.order_id AND qty_plan IS NULL;

                       IF FOUND THEN
                           UPDATE wms_orders
                           SET qty_fact = NEW.qty
                           WHERE sku_id = NEW.sku_id AND order_id = NEW.order_id AND qty_plan IS NULL;
                       ELSE
                           INSERT INTO wms_orders(sku_id, qty_fact, order_id)
                           VALUES (NEW.sku_id, NEW.qty, NEW.order_id);
                       END IF;
                   END IF;
               END IF;

               RETURN NEW;
            END;
            $BODY$;
        END IF;
    END;
    $$;
    """)

    # Проверка и создание триггера add_fact
    db.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'add_fact') THEN
            CREATE TRIGGER add_fact
            BEFORE INSERT OR UPDATE
            ON wms_operations
            FOR EACH ROW
            EXECUTE FUNCTION add_fact_to_order();
        END IF;
    END;
    $$;
    """)


def init():
    db.generate_mapping(create_tables=True)
    create_triggers_and_procedures()  
