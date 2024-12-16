from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
Answer the question below 

Here is the conversation history: {context}

Question: {question}

You're a virtual assitent of the Banco Pine

Respond only with 'True' or 'False' when asked if two texts 'são compatíveis'

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
        if check(user_input, result):
            print("Bot: ", result)
            context += f"\nUser: {user_input}\nBot: {result}"
        else:
            while not check(user_input, result):
                result = chain.invoke({"context": context, "question": user_input})
            print("Bot: ", result)
            context += f"\nUser: {user_input}\nBot: {result}"

def check(user_input, answer1):
    answer2 = chain.invoke({"context": "", "question": user_input})
    return bool(chain.invoke({"context": answer2, "question": f"{answer1} e {answer2} são compatíveis?"}))

if __name__ == "__main__":
    handle_conversation()
        
