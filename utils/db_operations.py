import pyodbc
from tkinter import messagebox
from utils.config_manager import DB_CONFIG, CLIENT_FIELDS_CONFIG, INTERNAL_DEFAULT_FIELDS

def connect_to_database():
    """Conecta ao banco de dados"""
    try:
        conn_str = ';'.join(f"{key}={value}" for key, value in DB_CONFIG.items())
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

        insert_columns = [field["db_column"] for field in CLIENT_FIELDS_CONFIG]
        
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
        values_for_insert_statement = [client_data.get(field["name"]) for field in CLIENT_FIELDS_CONFIG]
        
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

def update_client_data(client_data):
    """
    Atualiza os dados de um cliente na tabela FBCLIENTES.
    Retorna Verdadeiro em caso de atualização bem-sucedida, Falso se o cliente não existir ou em caso de erro.
    """
    conn = connect_to_database()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Define as colunas a serem atualizadas
        update_columns = [field["db_column"] for field in CLIENT_FIELDS_CONFIG if field["name"] != "XCLIENTES"]
        
        # Cria a string de placeholders para os valores de atualização
        placeholders = ', '.join([f"{col} = ?" for col in update_columns])

        query = f'''
        DECLARE @Status INT;

        IF EXISTS (SELECT 1 FROM SM11_PROD.dbo.FBCLIENTES WHERE XCLIENTES = ?)
            BEGIN
                UPDATE SM11_PROD.dbo.FBCLIENTES
                SET {placeholders}
                WHERE XCLIENTES = ?;
                SET @Status = 1; -- Successfully updated
            END
        ELSE
            BEGIN
                SET @Status = 0; -- Client does not exist
            END

        SELECT @Status AS Resultado; -- Return the status
        '''
        
        # Obtém os valores a serem atualizados (sem incluir o campo 'XCLIENTES' que é a chave)
        values_for_update_statement = [client_data.get(field["name"]) for field in CLIENT_FIELDS_CONFIG if field["name"] != "XCLIENTES"]
        
        # Coloca o valor de XCLIENTES no início dos valores para a atualização
        values_to_update = tuple(values_for_update_statement) + (client_data.get("XCLIENTES"),)
        
        cursor.execute(query, values_to_update)
        conn.commit()

        # Verifica se a atualização foi bem-sucedida
        if cursor.fetchone()[0] == 1:
            return True
        else:
            return False

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"An error occurred during update: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_client_data(identifier):
    """
    Deletes a client from the FBCLIENTES table based on NRECNO or CGC.
    Returns True on successful deletion, False otherwise.
    """
    conn = connect_to_database()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        # Try to delete by NRECNO first (assuming it's numeric)
        cursor.execute("DELETE FROM SM11_PROD.dbo.FBCLIENTES WHERE NRECNO = ?", identifier)
        rows_affected = cursor.rowcount
        
        if rows_affected == 0:
            # If no rows deleted by NRECNO, try by CGC
            cursor.execute("DELETE FROM SM11_PROD.dbo.FBCLIENTES WHERE CGC = ?", identifier)
            rows_affected = cursor.rowcount

        conn.commit()
        return rows_affected > 0
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"An error occurred during deletion: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_client_data(identifier):
    """
    Fetches client data from the FBCLIENTES table based on XCLIENTES or NAME.
    Returns a dictionary of client data if found, None otherwise.
    """
    conn = connect_to_database()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        
        # Try to fetch by NRECNO first
        cursor.execute("SELECT * FROM SM11_PROD.dbo.FBCLIENTES WHERE XCLIENTES = ?", identifier)
        client_row = cursor.fetchone()

        if client_row is None:
            # If not found by NRECNO, try by CGC
            cursor.execute("SELECT * FROM SM11_PROD.dbo.FBCLIENTES WHERE NAME = ?", identifier)
            client_row = cursor.fetchone()

        if client_row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, client_row))
        else:
            return None
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while fetching client data: {e}")
        return None
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
