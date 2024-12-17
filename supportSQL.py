import pyodbc

# Configuração da string de conexão
conn_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"  # Nome do servidor/instância
        "DATABASE=BancoPineDB;"          # Nome do banco
        "UID=pine_user;"                 # Usuário criado
        "PWD=pine_password;"             # Senha criada
    )

#testa conexão  
def test_connection():
    
    try:
        # Estabelecer a conexão
        conn = pyodbc.connect(conn_string)
        print("Conexão bem-sucedida!")
        conn.close()  # Fechar a conexão após o teste
    except pyodbc.Error as e:
        print("Erro ao conectar ao banco de dados:", e)

def retrieve_data():

    conversation_history = []

    try:
        # Estabelecer a conexão
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # Consultar os dados
        cursor.execute("SELECT * FROM ConversationLog")
        rows = cursor.fetchall()  # Retorna todos os resultados da consulta
        
        # Processar resultados
        for row in rows:
            #print(f"ID: {row.Id}, UserInput: {row.UserInput}, BotResponse: {row.BotResponse}, Timestamp: {row.Timestamp}")
            conversation_history.append(f"ID: {row.Id}\nUserInput: {row.UserInput}\nBotResponse: {row.BotResponse}\nTimestamp: {row.Timestamp}\n\n")
        
    except pyodbc.Error as e:
        print("Erro ao acessar dados do banco de dados:", e)
        
    finally:
        conn.close()  # Fechar a conexão
    
    return conversation_history

def save_history_to_file(conversation_history, filename):
    try:
        with open(filename, 'w') as file:
            file.writelines(conversation_history)
        print(f"Histórico de conversas salvo em {filename}")
    except IOError as e:
        print("Erro ao salvar o arquivo:", e)

def save_to_database(user_input, bot_response, conversation_history, filename):

    try:
        # Estabelecer a conexão
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # Inserir os dados na tabela
        cursor.execute(
            "INSERT INTO ConversationLog (UserInput, BotResponse, Timestamp) VALUES (?, ?, GETDATE())",
            (user_input, bot_response)
        )
        conn.commit()  # Confirmar a transação
        print("Dados salvos com sucesso.")
        
    except pyodbc.Error as e:
        print("Erro ao salvar dados no banco de dados:", e)
        
    finally:
        conn.close()  # Fechar a conexão

    save_history_to_file(conversation_history, filename)
    #save_to_database(user_input, bot_response)   

if __name__ == "__main__":
    test_connection()
    
