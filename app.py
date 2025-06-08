import os
import warnings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

warnings.filterwarnings("ignore", category=DeprecationWarning)

os.environ["OPENAI_API_KEY"] = (
    "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"
)


embeddings = OpenAIEmbeddings()
vectordb = FAISS.load_local("banco_faiss", embeddings, allow_dangerous_deserialization=True)

docs = vectordb.similarity_search('O que é o perceptron?', k=5)

contexto = "\n\n".join([
        f"Material: {doc.page_content}"
        for doc in docs
])

messages = [
        {"role": "system", "content": f"Você é um assistente virtual e deve responder com precissão as perguntas sobre uma empresa.\n\n{contexto}"},
        {"role": "user", "content": 'O que é o perceptron?'}
    ]

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
)

print(llm.invoke(messages))