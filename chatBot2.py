from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import supportSQL
import cambios
from datetime import datetime
import streamlit as st
import os
from auth import generate_token, verify_token
import re

# Integration of chatbot logic with Streamlit

# LangChain setup
template = """
Answer the question below 

Here is the conversation history: {context}

Question: {question}

You're a virtual assistant of the Banco Pine

Below are examples of questions that require escalation to a human assistant in a banking context. If any user inquiry matches these patterns, escalate the case to a human agent.

1. Security and Fraud Issues:
- "My account has been hacked. What should I do?"
- "I noticed a transaction on my statement that I don't recognize."
- "I received a strange alert in my email about my account. Is it legitimate?"

2. Complex Transactions:
- "I want to renegotiate my debt."
- "I need to transfer an amount that exceeds the daily limit."
- "How do I pay off a loan early?"

3. Legal or Regulatory Questions:
- "My account has been frozen due to a court order. What should I do?"
- "What are my rights regarding fees charged incorrectly?"
- "I want to dispute the bank's decision about my contract."

4. Complex Complaints:
- "I'm unhappy with the service I received at a branch."
- "I want to talk to someone about a recurring issue that is never resolved."
- "My problem hasn't been fixed by the automated solutions."

5. Accessibility Cases:
- "I have a visual impairment and I'm struggling to access the app."
- "I need help understanding how to use the bank's telephone service."

6. Personalization or Specific Products:
- "What is the best investment for my profile?"
- "I want to open a joint account with special conditions."
- "I'm considering purchasing insurance. Which one is the most suitable for me?"

7. Financial Emergencies:
- "I need an emergency credit card limit increase."
- "My account has been blocked, and I urgently need the funds."
- "I want to request emergency credit."

8. Highly Emotional Cases:
- "I'm facing severe financial difficulties. I need help."
- "I just lost a loved one and need to know how to close their account."
- "I'm thinking about closing my account. I'm very dissatisfied."

9. Documentation and Specific Processes:
- "How do I send proof of residence to update my profile?"
- "What documents are needed to open a business account?"
- "My ID has expired, but I haven't updated it yet. Can I still use my account?"

10. System Errors:
- "I can't access my account through the app."
- "The ATM didn't dispense cash, but the amount was debited."
- "The system is down, and I urgently need assistance."

If a user inquiry matches the nature of the examples provided above, respond with: "This issue requires special attention. I will connect you with a human assistant." 

Answer: 
"""

model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Streamlit setup
st.set_page_config(page_title="Banco Pine Chatbot", page_icon="🌲", layout="wide", initial_sidebar_state="collapsed")
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

def dtime():
    # Obter data e hora atuais
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    # Adicionar data e hora à resposta
    return current_time

def convertCurrencies(user_input):
    # Verificar se a pergunta é sobre câmbio
    # is_currency_question = bool(chain.invoke({
    #     "context": "",
    #     "question": f"Responda com 'True' ou 'False': a pergunta '{user_input}' é sobre a cotação de moedas?"
    # }))
    
    # if is_currency_question:
        # Perguntar ao modelo as moedas envolvidas
    moeda_info = chain.invoke({
        "context": "",
        "question": f"Na pergunta '{user_input}', identifique as moedas de origem e destino no formato: 'origem: <moeda_origem>, destino: <moeda_destino>'. Responda somente com 'origem: (abreviação da moeda), destino: (abreviação da moeda)' "
    })
    
    try:
        # Regex para capturar "origem" e "destino"
        origem_match = re.search(r"(origem|origin):\s*([A-Za-z]{3})", moeda_info, re.IGNORECASE)
        destino_match = re.search(r"(destino|destination):\s*([A-Za-z]{3})", moeda_info, re.IGNORECASE)
        
        # Atribuir valores encontrados ou None se não encontrados
        origem = origem_match.group(2).upper() if origem_match else None
        destino = destino_match.group(2).upper() if destino_match else None
        
        if origem and destino:
            # Chamar a função do módulo cambios
            exchange_rate = cambios.get_exchange_rate_google(origem, destino)
            if not exchange_rate:
                return "Não foi possível obter a taxa de câmbio. Por favor, tente novamente." 
            st.session_state.messages.append({"role": "assistant", "content": f"A taxa de câmbio de {origem} para {destino} é {exchange_rate}. Qual valor você deseja contratar na moeda {destino}?"}) 
            return f"A taxa de câmbio de {origem} para {destino} é {exchange_rate} Qual valor você deseja contratar na moeda {destino}?" + '  ' +str(dtime())
            #return exchange_rate + ' ' + str(dtime()) + ' Qual valor você deseja contratar na moeda {destino}?'
            
        else:
            return "Não foi possível identificar as moedas na pergunta. Por favor, tente novamente."
    except Exception as e:
        return f"Erro ao processar moedas: {e}" 

    # Resposta padrão caso não seja sobre câmbio
    #return chain.invoke({"context": st.session_state.context, "question": user_input})

#def contrata_moedas():

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
    st.warning("Please generate a Token to proceed.")
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
# Function to process user input and route appropriately
def process_user_input(user_input):
    # Verificar se a pergunta é sobre câmbio
    is_currency_question = bool(chain.invoke({
        "context": "",
        "question": f"Responda com 'True' ou 'False': a pergunta '{user_input}' é sobre a cotação de moedas? Se não for responda 'False' "
    }))
    
    if is_currency_question:
        return convertCurrencies(user_input)
    else:
        return generate_response(user_input)

# Chat Interface in Streamlit
if is_authenticated():
    with st.sidebar:
        st.success("Authenticated successfully!")

    # Mensagem inicial do chatbot
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Olá, sou o assistente virtual do Banco Pine. Como posso ajudar você hoje?"
        })

    # Display conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input box with unique key
    if prompt := st.chat_input(key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Process input and generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                #response = process_user_input(prompt)
                response = generate_response(prompt)
                st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_conversation_to_db(prompt, response)
