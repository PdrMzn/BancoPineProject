from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
Answer the question below 

Here is the conversation history: {context}

Question: {question}

You're a virtual assitent of the Banco Pine

Answer: 
"""

model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def handle_conversation():
    context = ""
    print("Welcome to the AI ChatBot! Type 'exit' to quit.\nHello! I'm an AI assistant provided by Banco Pine. I'm here to help you with any questions or concerns you may have about banking, finance, or other related topics.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit": 
            break
        result = chain.invoke({"context": context, "question": user_input})
        print("Bot: ", result)
        context += f"\nUser: {user_input}\nBot: {result}"

if __name__ == "__main__":
    handle_conversation()
        
