import os 
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import (SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate, ChatPromptTemplate)
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import UnstructuredExcelLoader
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, END,  MessagesState, StateGraph
from scripts import bot
from rag import vector_stores


def call_model(state: MessagesState):
    messages = state["messages"]        # get all past messages + current message
    question = messages[-1].content

    checking conversation history
    for msg in messages:                                      
        role = getattr(msg, "type")
        if role == "system":
            print(f"[System]: {msg.content}")
        elif role == "human":
            print(f"[me]: {msg.content}")
        elif role == "ai" or role == "AIMessage":
            print(f"[Cenly]: {msg.content}")
        else:
            print(f"[{role}]: {msg.content}")


    # # Mock data loading
    # loader = UnstructuredExcelLoader("mock_data/mock_sales_revenue.xlsx", mode = "elements")
    # docs =  loader.load()
    # doc = docs[0]    # context = doc.metadata['text_as_html']
    try: 
        vector_store = vector_stores.load_vector_store()
    except:
        # print("No vector storage saved in local memory")
        vector_stores.create_vector_store()
        vector_store = vector_stores.load_vector_store()
        

    retriever = vector_store.as_retriever(search_type='mmr', search_kwargs = {'k' : 3, 'fetch_k' : 10, 'lambda_mult': 1})
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    # print(context)

    response = AIMessage(bot.cenly_analyze(context, question, messages))
    return {"messages": [response]} 


# Chat message history graph creation 
workflow = StateGraph(state_schema=MessagesState)

def workflow_setup():
    workflow.add_edge(START, "chatbot")
    workflow.add_node("chatbot", call_model) 
    workflow.add_edge("chatbot", END)

workflow_setup()

# Database context window
with SqliteSaver.from_conn_string("ted_chat_history.db") as memory:
    app = workflow.compile(checkpointer=memory)
    config = {"configurable": {"thread_id": "first"}}
    

    question = input("Enter your question: ")
    human_message = HumanMessage(question)
    messages = [human_message]
    output = app.invoke({"messages": messages}, config)

    print(f"Cenly: {output['messages'][-1].content}")
    



