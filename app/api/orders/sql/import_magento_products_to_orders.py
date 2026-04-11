"""
Script to import data from magento_products.csv into the orders table.
"""
import csv
from datetime import datetime
from app.utils.db import get_db_connection_direct

CSV_PATH = "app/static/csv/magento_products.csv"

# List of columns in the orders table (must match the table definition)
ORDERS_COLUMNS = [
    "sku","store_view_code","attribute_set_code","product_type","categories","product_websites","name","description","short_description","weight","product_online","tax_class_name","visibility","price","special_price","special_price_from_date","special_price_to_date","url_key","meta_title","meta_keywords","meta_description","base_image","base_image_label","small_image","small_image_label","thumbnail_image","thumbnail_image_label","swatch_image","swatch_image_label","created_at","updated_at","new_from_date","new_to_date","display_product_options_in","map_price","msrp_price","map_enabled","gift_message_available","custom_design","custom_design_from","custom_design_to","custom_layout_update","page_layout","product_options_container","msrp_display_actual_price_type","country_of_manufacture","additional_attributes","qty","out_of_stock_qty","use_config_min_qty","is_qty_decimal","allow_backorders","use_config_backorders","min_cart_qty","use_config_min_sale_qty","max_cart_qty","use_config_max_sale_qty","is_in_stock","notify_on_stock_below","use_config_notify_stock_qty","manage_stock","use_config_manage_stock","use_config_qty_increments","qty_increments","use_config_enable_qty_inc","enable_qty_increments","is_decimal_divided","website_id","related_skus","related_position","crosssell_skus","crosssell_position","upsell_skus","upsell_position","additional_images","additional_image_labels","hide_from_product_page","custom_options","bundle_price_type","bundle_sku_type","bundle_price_view","bundle_weight_type","bundle_values","bundle_shipment_type","associated_skus","downloadable_links","downloadable_samples","configurable_variations","configurable_variation_labels","hide","flag"
]


def import_csv_to_orders():
    conn = get_db_connection_direct()
    inserted = 0
    total = 0
    with conn:
        with conn.cursor() as cur:
            print("Clearing orders table before import...")
            cur.execute("TRUNCATE TABLE orders;")
            print("orders table cleared.")
            seen_skus = set()
            with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for idx, row in enumerate(reader):
                    original_sku = row.get("sku")
                    new_sku = original_sku
                    # Ensure SKU is unique in this import batch
                    suffix = 1
                    while new_sku in seen_skus:
                        new_sku = f"{original_sku}_{suffix}"
                        suffix += 1
                    if new_sku != original_sku:
                        print(f"Duplicate SKU found: {original_sku}, changed to {new_sku}")
                    row["sku"] = new_sku
                    seen_skus.add(new_sku)
                    total += 1
                    # Add hide and flag fields if not present
                    row.setdefault("hide", False)
                    row.setdefault("flag", False)
                    # Convert empty strings to None
                    values = [row.get(col) if row.get(col) != '' else None for col in ORDERS_COLUMNS]
                    # Print first row and values for debug
                    if idx == 0:
                        print("First CSV row:", row)
                        print("First values list:", values)
                    # Convert booleans and numerics as needed
                    for i, col in enumerate(ORDERS_COLUMNS):
                        if col in ["hide", "flag", "product_online", "use_config_min_qty", "is_qty_decimal", "allow_backorders", "use_config_backorders", "use_config_min_sale_qty", "use_config_max_sale_qty", "is_in_stock", "notify_on_stock_below", "use_config_notify_stock_qty", "manage_stock", "use_config_manage_stock", "use_config_qty_increments", "use_config_enable_qty_inc", "enable_qty_increments", "is_decimal_divided"]:
                            if values[i] is not None:
                                values[i] = str(values[i]).lower() in ("1", "true", "t", "yes")
                        elif col in ["weight", "price", "special_price", "map_price", "msrp_price", "qty", "out_of_stock_qty", "min_cart_qty", "max_cart_qty", "qty_increments"]:
                            if values[i] is not None:
                                try:
                                    values[i] = float(values[i])
                                except ValueError:
                                    values[i] = None
                        elif col.endswith("_date") or col.endswith("_at") or col in ["custom_design_from", "custom_design_to"]:
                            if values[i] is not None:
                                try:
                                    # Try parsing as date or datetime
                                    values[i] = datetime.strptime(values[i], "%m/%d/%y")
                                except Exception:
                                    try:
                                        values[i] = datetime.strptime(values[i], "%Y-%m-%d")
                                    except Exception:
                                        values[i] = None
                    placeholders = ','.join(['%s'] * len(ORDERS_COLUMNS))
                    sql = f"INSERT INTO orders ({', '.join(ORDERS_COLUMNS)}) VALUES ({placeholders})"
                    try:
                        cur.execute(sql, values)
                        inserted += 1
                    except Exception as e:
                        print(f"Error inserting row {idx+1} (sku={row.get('sku')}): {e}")
            try:
                conn.commit()
                print("Database commit successful.")
            except Exception as e:
                print(f"Error during commit: {e}")
    print(f"Total rows processed: {total}")
    print(f"Total rows attempted to insert: {inserted}")
    if inserted == 0:
        print("No rows were inserted. Please check for errors above or review the data and schema alignment.")
    print("Data import attempt complete.")

if __name__ == "__main__":
    import_csv_to_orders()
