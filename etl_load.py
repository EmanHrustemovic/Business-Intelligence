import os
import json
import time
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def get_connection_string():
    """Reads the connection string from .gemini/settings.json."""
    settings_path = os.path.join('.gemini', 'settings.json')
    if not os.path.exists(settings_path):
        raise FileNotFoundError(f"Settings file not found at {settings_path}")
        
    with open(settings_path, 'r') as f:
        config = json.load(f)
        
    try:
        args = config['mcpServers']['postgres']['args']
        conn_str = args[-1]
        return conn_str
    except KeyError as e:
        raise ValueError("Could not find the PostgreSQL connection string in .gemini/settings.json") from e

def prepare_data(df, columns):
    """
    Keeps only target columns, handles NULL values by converting pandas NaN/NaT
    to Python None, handles datetime conversions, and converts numpy numeric types
    to native Python integers/floats.
    """
    df_temp = df[columns].copy()
    
    # Replace all pandas null values (NaN, NaT, <NA>) with Python None
    df_temp = df_temp.where(pd.notnull(df_temp), None)
    
    data = []
    for row in df_temp.itertuples(index=False, name=None):
        clean_row = []
        for val in row:
            if val is None:
                clean_row.append(None)
            elif isinstance(val, pd.Timestamp):
                clean_row.append(val.to_pydatetime())
            elif hasattr(val, 'item') and not isinstance(val, str):
                # Convert numpy scalars (int64, float64, etc.) to Python native types
                clean_row.append(val.item())
            elif pd.isna(val):
                clean_row.append(None)
            else:
                clean_row.append(val)
        data.append(tuple(clean_row))
        
    return data

def run_etl():
    start_time = time.time()
    
    # 1. Read Connection String
    try:
        conn_str = get_connection_string()
        print("Successfully read database connection string.")
    except Exception as e:
        print(f"Error reading configuration: {e}")
        sys.exit(1)
        
    # 2. Establish DB Connection
    try:
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        print("Connected to PostgreSQL database successfully.")
    except Exception as e:
        print(f"Database connection error: {e}")
        sys.exit(1)
        
    try:
        # Start a single transaction
        print("\nStarting ETL Load Transaction...")
        
        # ==========================================
        # 1. LOAD dim_customers
        # ==========================================
        print("\n[1/5] Processing dim_customers...")
        df_cust = pd.read_csv('olist_customers_dataset.csv')
        df_cust = df_cust.dropna(subset=['customer_id'])
        df_cust['customer_zip_code_prefix'] = pd.to_numeric(df_cust['customer_zip_code_prefix'], errors='coerce').astype('Int64')
        df_cust_clean = df_cust.drop_duplicates(subset=['customer_id'], keep='first')
        
        cust_columns = ['customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 'customer_city', 'customer_state']
        cust_data = prepare_data(df_cust_clean, cust_columns)
        
        cust_query = """
            INSERT INTO dim_customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
            VALUES %s
            ON CONFLICT (customer_id) DO NOTHING;
        """
        execute_values(cursor, cust_query, cust_data, page_size=5000)
        print(f"Loaded {len(cust_data)} records into dim_customers.")
        
        # ==========================================
        # 2. LOAD dim_sellers
        # ==========================================
        print("\n[2/5] Processing dim_sellers...")
        df_sellers = pd.read_csv('olist_sellers_dataset.csv')
        df_sellers = df_sellers.dropna(subset=['seller_id'])
        df_sellers['seller_zip_code_prefix'] = pd.to_numeric(df_sellers['seller_zip_code_prefix'], errors='coerce').astype('Int64')
        df_sellers_clean = df_sellers.drop_duplicates(subset=['seller_id'], keep='first')
        
        sel_columns = ['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state']
        sel_data = prepare_data(df_sellers_clean, sel_columns)
        
        sel_query = """
            INSERT INTO dim_sellers (seller_id, seller_zip_code_prefix, seller_city, seller_state)
            VALUES %s
            ON CONFLICT (seller_id) DO NOTHING;
        """
        execute_values(cursor, sel_query, sel_data, page_size=5000)
        print(f"Loaded {len(sel_data)} records into dim_sellers.")
        
        # ==========================================
        # 3. LOAD dim_products
        # ==========================================
        print("\n[3/5] Processing dim_products...")
        df_prod = pd.read_csv('olist_products_dataset.csv')
        df_prod = df_prod.dropna(subset=['product_id'])
        df_trans = pd.read_csv('product_category_name_translation.csv')
        
        # Merge for English category names
        df_prod_merged = df_prod.merge(df_trans, on='product_category_name', how='left')
        df_prod_merged['product_category_name'] = df_prod_merged['product_category_name_english']
        
        # Cast numeric dimensions
        int_prod_cols = [
            'product_name_lenght', 'product_description_lenght', 'product_photos_qty',
            'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'
        ]
        for col in int_prod_cols:
            df_prod_merged[col] = pd.to_numeric(df_prod_merged[col], errors='coerce').astype('Int64')
            
        df_prod_clean = df_prod_merged.drop_duplicates(subset=['product_id'], keep='first')
        
        prod_columns = [
            'product_id', 'product_category_name', 'product_name_lenght', 'product_description_lenght',
            'product_photos_qty', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'
        ]
        prod_data = prepare_data(df_prod_clean, prod_columns)
        
        prod_query = """
            INSERT INTO dim_products (product_id, product_category_name, product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
            VALUES %s
            ON CONFLICT (product_id) DO NOTHING;
        """
        execute_values(cursor, prod_query, prod_data, page_size=5000)
        print(f"Loaded {len(prod_data)} records into dim_products.")
        
        # ==========================================
        # 4. LOAD dim_orders_context
        # ==========================================
        print("\n[4/5] Processing dim_orders_context...")
        df_orders = pd.read_csv('olist_orders_dataset.csv')
        df_orders = df_orders.dropna(subset=['order_id'])
        
        # Convert datetime fields
        date_orders_cols = [
            'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
            'order_delivered_customer_date', 'order_estimated_delivery_date'
        ]
        for col in date_orders_cols:
            df_orders[col] = pd.to_datetime(df_orders[col], errors='coerce')
            
        df_orders_clean = df_orders.drop_duplicates(subset=['order_id'], keep='first')
        
        ord_columns = [
            'order_id', 'order_status', 'order_purchase_timestamp', 'order_approved_at',
            'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'
        ]
        ord_data = prepare_data(df_orders_clean, ord_columns)
        
        ord_query = """
            INSERT INTO dim_orders_context (order_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date)
            VALUES %s
            ON CONFLICT (order_id) DO NOTHING;
        """
        execute_values(cursor, ord_query, ord_data, page_size=5000)
        print(f"Loaded {len(ord_data)} records into dim_orders_context.")
        
        # ==========================================
        # 5. LOAD fact_order_items
        # ==========================================
        print("\n[5/5] Processing fact_order_items...")
        df_items = pd.read_csv('olist_order_items_dataset.csv')
        df_items = df_items.dropna(subset=['order_id', 'order_item_id'])
        
        df_payments = pd.read_csv('olist_order_payments_dataset.csv')
        df_reviews = pd.read_csv('olist_order_reviews_dataset.csv')
        
        # Aggregate payments to order_id level
        df_payments_agg = df_payments.groupby('order_id').agg({
            'payment_sequential': 'max',
            'payment_type': 'first',
            'payment_installments': 'max',
            'payment_value': 'sum'
        }).reset_index()
        
        # Aggregate reviews to order_id level
        df_reviews_agg = df_reviews.groupby('order_id').agg({
            'review_score': 'mean'
        }).reset_index()
        df_reviews_agg['review_score'] = df_reviews_agg['review_score'].round()
        
        # Merge items with parent customer_id, payments, and reviews
        df_fact = df_items.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')
        df_fact = df_fact.merge(df_payments_agg, on='order_id', how='left')
        df_fact = df_fact.merge(df_reviews_agg, on='order_id', how='left')
        
        # Standardize data types
        df_fact['shipping_limit_date'] = pd.to_datetime(df_fact['shipping_limit_date'], errors='coerce')
        int_fact_cols = ['order_item_id', 'payment_sequential', 'payment_installments', 'review_score']
        for col in int_fact_cols:
            df_fact[col] = pd.to_numeric(df_fact[col], errors='coerce').astype('Int64')
            
        df_fact_clean = df_fact.drop_duplicates(subset=['order_id', 'order_item_id'], keep='first')
        
        fact_columns = [
            'order_id', 'order_item_id', 'product_id', 'seller_id', 'customer_id',
            'shipping_limit_date', 'price', 'freight_value', 'payment_sequential',
            'payment_type', 'payment_installments', 'payment_value', 'review_score'
        ]
        fact_data = prepare_data(df_fact_clean, fact_columns)
        
        fact_query = """
            INSERT INTO fact_order_items (order_id, order_item_id, product_id, seller_id, customer_id, shipping_limit_date, price, freight_value, payment_sequential, payment_type, payment_installments, payment_value, review_score)
            VALUES %s
            ON CONFLICT (order_id, order_item_id) DO NOTHING;
        """
        execute_values(cursor, fact_query, fact_data, page_size=5000)
        print(f"Loaded {len(fact_data)} records into fact_order_items.")
        
        # Commit transaction
        conn.commit()
        print("\nETL Load successfully completed and committed!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nETL Load transaction aborted and rolled back due to error: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
        print("Database connection closed.")
        
    duration = time.time() - start_time
    print(f"Total time elapsed: {duration:.2f} seconds.")

if __name__ == "__main__":
    run_etl()
