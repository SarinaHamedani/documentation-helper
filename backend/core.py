from typing import Any, Dict, List
from dotenv import load_dotenv
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from langchain.prompts import PromptTemplate
import os

load_dotenv()
INDEX_NAME="langchain-doc-index"

def run_llm_simple(query, llm, ):
    chain = PromptTemplate.from_template(query) | llm
    result = chain.invoke(input={})
    new_result = {
        "query": query,
        "source_documents": [],
        "result": result.content
    }
    return  new_result

def run_llm(query: str, chat_history: List[Dict[str, Any]] = []):
    print(os.environ["OPENAI_API_KEY"])
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    docsearch = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
    chat = ChatOpenAI(model="gpt-4o-mini", verbose=True, temperature=0)

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    stuff_documents_chain = create_stuff_documents_chain(llm=chat, prompt=retrieval_qa_chat_prompt)

    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=docsearch.as_retriever(), prompt=rephrase_prompt
    )
    qa = create_retrieval_chain(
        retriever=history_aware_retriever, combine_docs_chain=stuff_documents_chain
    )


    result = qa.invoke(input={"input": query, "chat_history": chat_history})
    
    # return run_llm_simple(query, chat)

    new_result = {
        "query": result["input"],
        "source_documents": result["context"],
        "result": result["output"]
    }
    
    return new_result


if __name__=="__main__":
    res = run_llm("What is a Langchain Chain?")
    print(res["result"])
