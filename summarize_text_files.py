import getpass
import os
import dotenv

dotenv.load_dotenv()
openai_api_key = os.getenv('openai_api_key')

import bs4
from langchain import hub
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
import os
from openai import OpenAI
import progressbar

llm = ChatOpenAI(api_key=openai_api_key,model="gpt-4-turbo-2024-04-09")

def summarize_with_gpt(text):
    prompt = ChatPromptTemplate.from_template("""Answer the following questions in German based only on the provided context:
    <context>
    {context}
    </context>

    Questions: {input}""")

    document_chain = create_stuff_documents_chain(llm, prompt)

    response = document_chain.invoke({
        "input": "Identify the key points raised by the stakeholder in their accompanying messages (and, if feasible, their attached documents) \
        Summarise the stakeholder feedback in bullets, grouping similar statements and highlighting divergent opinions \
        Cluster opinions according to positive and negative sentiment (supportive or against the proposed regulation) \
        Identify evidence from the inputs that can reinforce or contradict the proposed rules",
        "context": text
    })
    return(response)


def summarize_each_feedback(folder_path):
    folder_name = "summarization"
    text_files = [file for file in os.listdir(folder_path) if file.endswith(".txt")]
    print(text_files)
    for text_file in  progressbar.progressbar(text_files, redirect_stdout=True):
        
        # Check if the summary file already exists
        summary_path = os.path.join(folder_name, text_file)
        if os.path.exists(summary_path):
            print(f"Skipping existing summary for {text_file}")
            continue
        print(summary_path)
        text_path = os.path.join(folder_path, text_file)
        loader = TextLoader(text_path)
        text =  loader.load()
        summarized_text = summarize_with_gpt(text)
        file_name_without_extension = text_file.rsplit('.', 2)[0].rsplit('_', 1)[0]  # Remove the extension

        with open(f"{folder_name}/{text_file}", "w") as f: 
            f.write("Feedback from: "+file_name_without_extension + "\n" + "\n" + summarized_text)
          
summarize_each_feedback("text_per_pdf")