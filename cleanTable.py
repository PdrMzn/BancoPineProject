import pyodbc

def clear_table():
    conn_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=BancoPineDB;"
        "UID=pine_user;"
        "PWD=pine_password;"
    )

    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # Limpa os dados da tabela
        cursor.execute("TRUNCATE TABLE ConversationLog;")
        conn.commit()
        print("Tabela ConversationLog limpa com sucesso.")
        
    except pyodbc.Error as e:
        print("Erro ao limpar a tabela:", e)
        
    finally:
        conn.close()

# Execute a função
if __name__ == "__main__":
    clear_table()
