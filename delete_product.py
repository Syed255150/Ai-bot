import sqlite3
import time
from db_connection import get_connection

def delete_product(product_id, retries=3, delay=1):
    while retries > 0:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Example delete query
            cursor.execute("DELETE FROM product WHERE product_id = ?", (product_id,))
            
            # Commit the transaction
            conn.commit()
            
            print(f"Product with ID {product_id} deleted successfully.")
            return  # Exit function if successful
            
        except sqlite3.OperationalError as e:
            print(f"Error: {e}. Retrying...")
            retries -= 1
            time.sleep(delay)
            
        finally:
            conn.close()

    print(f"Failed to delete product with ID {product_id} after retries.")

# Example usage:
if __name__ == "__main__":
    product_id_to_delete = 5  # Replace with the actual product_id you want to delete
    delete_product(product_id_to_delete)
