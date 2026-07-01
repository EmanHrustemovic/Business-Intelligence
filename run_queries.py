import psycopg2
import time
import sys

def get_connection():
    conn_str = "postgresql://postgres.zmruhqdtidrtggcoojzm:G3c9h.%2C1%3F0EH@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
    for attempt in range(1, 10):
        try:
            conn = psycopg2.connect(conn_str, connect_timeout=5)
            return conn
        except Exception as e:
            err_str = str(e)
            print(f"Attempt {attempt}/9 failed to connect: {err_str}", file=sys.stderr)
            if "ECIRCUITBREAKER" in err_str or "temporarily blocked" in err_str:
                print("Circuit breaker active. Waiting 15 seconds...", file=sys.stderr)
                time.sleep(15)
            else:
                print("Waiting 5 seconds...", file=sys.stderr)
                time.sleep(5)
    raise Exception("Could not establish database connection after multiple attempts.")

def execute_query(cursor, query):
    try:
        cursor.execute(query)
        if cursor.description is not None:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        return None, None
    except Exception as e:
        raise e

def main():
    # Establish connection
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    cursor = conn.cursor()
    
    # Define the 11 queries. We will handle column name fallback if needed.
    # Note: Query 5 has shipping_date_limit / shipping_limit_date fallback.
    # Note: Query 10 has payment_installments / payment_installment fallback.
    
    queries = {
        1: ("What is the total revenue?", "SELECT SUM(payment_value) AS total_revenue FROM fact_order_items;"),
        2: ("How many orders have been placed?", "SELECT COUNT(DISTINCT order_id) AS total_orders FROM fact_order_items;"),
        3: ("How many unique customers do we have?", "SELECT COUNT(DISTINCT customer_id) AS total_customers FROM fact_order_items;"),
        4: ("What is the average review score?", "SELECT AVG(review_score) AS average_review_score FROM fact_order_items;"),
        5: ("Show monthly revenue.", [
            "SELECT DATE_TRUNC('month', shipping_limit_date) AS month, SUM(payment_value) AS revenue FROM fact_order_items GROUP BY month ORDER BY month;",
            "SELECT DATE_TRUNC('month', shipping_date_limit) AS month, SUM(payment_value) AS revenue FROM fact_order_items GROUP BY month ORDER BY month;"
        ]),
        6: ("Show the top 10 product categories by revenue.", """
            SELECT dp.product_category_name, SUM(f.payment_value) AS revenue 
            FROM fact_order_items f 
            JOIN dim_products dp ON f.product_id = dp.product_id 
            GROUP BY dp.product_category_name 
            ORDER BY revenue DESC 
            LIMIT 10;
        """),
        7: ("Show the top 10 sellers by revenue.", "SELECT seller_id, SUM(payment_value) AS revenue FROM fact_order_items GROUP BY seller_id ORDER BY revenue DESC LIMIT 10;"),
        8: ("Show the order distribution by payment type.", "SELECT payment_type, COUNT(*) AS number_of_orders FROM fact_order_items GROUP BY payment_type;"),
        9: ("Show the average order value by review score.", "SELECT review_score, AVG(payment_value) AS average_order_value FROM fact_order_items GROUP BY review_score ORDER BY review_score;"),
        10: ("Show the average freight cost by number of payment installments.", [
            "SELECT payment_installments, AVG(freight_value) AS average_freight FROM fact_order_items GROUP BY payment_installments ORDER BY payment_installments;",
            "SELECT payment_installment, AVG(freight_value) AS average_freight FROM fact_order_items GROUP BY payment_installment ORDER BY payment_installment;"
        ]),
        11: ("Show revenue by customer state.", """
            SELECT c.customer_state, SUM(f.payment_value) AS revenue 
            FROM fact_order_items f 
            JOIN dim_customers c ON f.customer_id = c.customer_id 
            GROUP BY c.customer_state 
            ORDER BY revenue DESC;
        """)
    }
    
    results = {}
    
    for q_num, (desc, q_val) in queries.items():
        # Handle list of query variants for fallbacks
        if isinstance(q_val, list):
            last_err = None
            success = False
            for variant in q_val:
                try:
                    # rollback transaction if previous failed in the same session
                    conn.rollback()
                    cols, rows = execute_query(cursor, variant)
                    results[q_num] = (variant, cols, rows)
                    success = True
                    break
                except Exception as e:
                    last_err = e
            if not success:
                print(f"Query {q_num} failed with all variants. Last error: {last_err}")
                sys.exit(1)
        else:
            try:
                conn.rollback()
                cols, rows = execute_query(cursor, q_val)
                results[q_num] = (q_val, cols, rows)
            except Exception as e:
                print(f"Query {q_num} failed: {e}")
                sys.exit(1)
                
    # Close connection
    cursor.close()
    conn.close()
    
    # Print results in markdown format exactly as requested
    for q_num in sorted(results.keys()):
        q_val, cols, rows = results[q_num]
        print(f"### Question {q_num}: {queries[q_num][0]}")
        print("\n**SQL Query:**")
        print("```sql")
        print(q_val.strip())
        print("```")
        print("\n**Query Result:**")
        
        # Display rows
        if rows:
            # Print as a nice markdown table
            header = " | ".join(cols)
            separator = " | ".join(["---"] * len(cols))
            print(f"| {header} |")
            print(f"| {separator} |")
            for r in rows:
                row_str = " | ".join(str(val) if val is not None else "NULL" for val in r)
                print(f"| {row_str} |")
        else:
            print("No results returned.")
        print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
