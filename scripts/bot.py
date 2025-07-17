import os 
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
# from langgraph.checkpoint.postgres import PosgresSaver
from langchain_community.document_loaders import UnstructuredExcelLoader
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, END,  MessagesState, StateGraph


load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# Local Ollama model configurations
base_url = "http://localhost:11434"
model = "gemma3:1b"
chatbot = ChatOllama(base_url=base_url, model=model, temperature = 0.3)

system_prompt = '''
                    <core_identity> You are an business assistant/advisor called Cenly, 
                    whose sole purpose is to analyze and solve problems asked by the user using their data, including but not limited to: sales revenue,
                      inventory, income,.... 
                    Your responses must be specific, accurate, and actionable. </core_identity>

                    <general_guidelines>

                    NEVER use meta-phrases (e.g., "let me help you", "I can see that").
                    NEVER summarize unless explicitly requested.
                    ALWAYS be specific, detailed, and accurate.
                    ALWAYS acknowledge uncertainty when present.
                    ALWAYS use markdown formatting.
                    If you don't know something, just say I don't know. 
                    </general_guidelines>

                '''


user_prompt = '''
                Be concise!
                Context: {context}
                Question: {question}
                '''


template = ChatPromptTemplate.from_messages([("system", system_prompt),
                                             MessagesPlaceholder("conversation_history"),
                                             ("human", user_prompt)])

chain = template | chatbot | StrOutputParser()

def cenly_analyze(context, question, conversation_history = None):
    if conversation_history is None:
        conversation_history = []
    
    # Debug
    # print(f"Context length: {len(context)}")
    # print(f"Question: {question}")
    # print(f"History length: {len(conversation_history)}")
    
    result = chain.invoke({
        'context': context, 
        'conversation_history': conversation_history, 
        'question': question
    }) 
    
    return result

    