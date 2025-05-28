import pyodbc
from tkinter import messagebox
import utils.config_manager as config_manager

def connect_to_database():
    """Conecta ao banco de dados"""
    try:
        conn_str = ';'.join(f"{key}={value}" for key, value in config_manager.DB_CONFIG.items())
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database: {e}")
        return None

def insert_client_data(client_data):
    """
    Insere um novo cliente na tabela FBCLIENTES ou indica se o cliente já existe.
    Retorna Verdadeiro em caso de inserção bem-sucedida, Falso se o cliente já existir ou em caso de erro.
    """
    conn = connect_to_database()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        insert_columns = [field["db_column"] for field in config_manager.CLIENT_FIELDS_CONFIG]
        
        placeholders = ', '.join(['?'] * len(insert_columns))
        columns_str = ', '.join(insert_columns)

        query = f'''
        DECLARE @Status INT;

        IF NOT EXISTS (SELECT 1 FROM SM11_PROD.dbo.FBCLIENTES WHERE XCLIENTES = ?)
            BEGIN
                INSERT INTO SM11_PROD.dbo.FBCLIENTES
                    ({columns_str})
                VALUES ({placeholders});
                SET @Status = 1; -- Successfully inserted
            END
        ELSE
            BEGIN
                SET @Status = 0; -- Client already exists
            END

        SELECT @Status AS Resultado; -- Return the status
        '''
        values_for_insert_statement = [client_data.get(field["name"]) for field in config_manager.CLIENT_FIELDS_CONFIG]
        
        values_to_insert = (client_data.get("XCLIENTES"),) + tuple(values_for_insert_statement)
        
        cursor.execute(query, values_to_insert)
        conn.commit()
        return True
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"An error occurred during insertion: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_table_columns(table_name="FBCLIENTES"):
    """Fetches column names from the specified table in the database."""
    conn = connect_to_database()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = 'dbo'")
        columns = [row[0] for row in cursor.fetchall()]
        return columns
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error fetching table columns: {e}")
        return []
    finally:
        if conn:
            conn.close()
