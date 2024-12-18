from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import supportSQL
import cambios
import streamlit as st
import os
from auth import generate_token, verify_token

# Integration of chatbot logic with Streamlit

# LangChain setup
template = """
Answer the question below 

Here is the conversation history: {context}

Question: {question}

You're a virtual assistant of the Banco Pine


Answer: 
"""
#Function to convert the dollar to euro: cambios.get_exchange_rate_google("USD", "EUR")

model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Streamlit setup
st.set_page_config(page_title="Banco Pine Chatbot")
st.title("Banco Pine AI Chatbot")

# Ensure the script runs in the correct context
if not st.runtime.exists():
    raise RuntimeError("Streamlit script is not running in a proper ScriptRunContext!")

if "context" not in st.session_state:
    st.session_state.context = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to generate a chatbot response
def generate_response(user_input):
    #result = convertCurrencies(user_input)
    result = chain.invoke({"context": st.session_state.context, "question": user_input})
    if check(user_input, result):
        st.session_state.context += f"\nUser: {user_input}\nBot: {result}"
    else:
        while not check(user_input, result):
            result = chain.invoke({"context": st.session_state.context, "question": user_input})
        st.session_state.context += f"\nUser: {user_input}\nBot: {result}"
    return result

def check(user_input, answer1):
    answer2 = chain.invoke({"context": "", "question": user_input})
    return bool(chain.invoke({"context": answer2, "question": f"Responda com 'True' ou 'False' se {answer1} e {answer2} são iguais?"}))

def convertCurrencies(user_input):
    # Verificar se a pergunta é sobre câmbio
    is_currency_question = bool(chain.invoke({
        "context": "",
        "question": f"Responda com 'True' ou 'False': a pergunta '{user_input}' é sobre a cotação de moedas?"
    }))
    
    if is_currency_question:
        # Perguntar ao modelo as moedas envolvidas
        moeda_info = chain.invoke({
            "context": "",
            "question": f"Na pergunta '{user_input}', identifique as moedas de origem e destino no formato: 'origem: <moeda_origem>, destino: <moeda_destino>'. Responda somente com 'origem: (abreviação da moeda), (destino: abreviação da moeda) "
        })
        
        try:
            # Usar regex para capturar os valores de origem e destino
            import re
            
            # Regex para capturar "origem" e "destino"
            origem_match = re.search(r"(origem|origin):\s*([A-Za-z]{3})", moeda_info, re.IGNORECASE)
            destino_match = re.search(r"(destino|destination):\s*([A-Za-z]{3})", moeda_info, re.IGNORECASE)
            
            # Atribuir valores encontrados ou None se não encontrados
            origem = origem_match.group(2).upper() if origem_match else None
            destino = destino_match.group(2).upper() if destino_match else None
            
            if origem and destino:
                # Chamar a função do módulo cambios
                return cambios.get_exchange_rate_google(origem, destino)#, st.write(f"Debug: {moeda_info}", print(origem,destino))
            else:
                return "Não foi possível identificar as moedas na pergunta. Por favor, tente novamente."#, st.write(f"Debug: {moeda_info}", print(origem,destino))
        except Exception as e:
            return f"Erro ao processar moedas: {e}"#, st.write(f"Debug: {moeda_info}", print(origem,destino))

    # Resposta padrão caso não seja sobre câmbio
    return chain.invoke({"context": st.session_state.context, "question": user_input})


def save_conversation_to_db(user_input, bot_response):
    conversation_history = supportSQL.retrieve_data()
    supportSQL.save_to_database(user_input, bot_response, conversation_history, 'conversation_history.txt')

### Bearer JWT integration 

# Button Authentication
with st.sidebar:
    st.title('Authentication')
    user_id = st.text_input("User ID", value="user_123")
    if st.button('Generate Token'):
        token = generate_token(user_id)
        st.session_state.auth_token = token
        st.query_params["auth_token"] = token  # Set token as query parameter
        st.write("Generated Token:", token)

if "auth_token" not in st.session_state:
    st.session_state.auth_token = ""

def is_authenticated():
    token_data = verify_token(st.session_state.auth_token)
    return "user_id" in token_data

if not is_authenticated():
    st.warning("Please enter a valid Bearer Token to proceed.")
    st.stop()
###

# Chat Interface in Streamlit
with st.sidebar:
    st.title('Options')

#    if st.button('Toggle Chat Verificantion Visibility'):
#        if st.session_state.get('chat_visible', True):
#           #st.session_state.auth_token = st.text_input("Enter your Bearer Token", type="password") # Token Input
#            st.session_state.chat_visible = False
#        else:
#            st.session_state.chat_visible = True

    if st.button('Clear Chat History'):
        st.session_state.context = ""
        st.session_state.messages = []
        st.success('Chat history cleared!')

## verification Bearer JWT
if is_authenticated():
    with st.sidebar:
        st.success("Authenticated successfully!")

    # Display conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

     # Input box with unique key
    if prompt := st.chat_input(key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = convertCurrencies(prompt) or generate_response(prompt)
                st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_conversation_to_db(prompt, response)

