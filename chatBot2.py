from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import supportSQL
import cambios
import streamlit as st
import os

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
    result = bool(chain.invoke({"context": "", "question": f"Responda com 'True' ou 'False': a pergunta {user_input} é para conversão entre duas moedas?"}))
    if result:
        moedas = tuple(chain.invoke({"context": "", "question": f"Guarde numa tupla as strings da moeda que deve ser convertida e a da moeda para a qual se deve converter a primeira"}))
        return cambios.get_exchange_rate_google(moedas[0], moedas[1])
    return chain.invoke({"context": st.session_state.context, "question": user_input})

def save_conversation_to_db(user_input, bot_response):
    conversation_history = supportSQL.retrieve_data()
    supportSQL.save_to_database(user_input, bot_response, conversation_history, 'conversation_history.txt')

# Chat Interface in Streamlit
with st.sidebar:
    st.title('Options')
    if st.button('Clear Chat History'):
        st.session_state.context = ""
        st.session_state.messages = []
        st.success('Chat history cleared!')

# Display conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input box
if prompt := st.chat_input(placeholder="Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_conversation_to_db(prompt, response)
