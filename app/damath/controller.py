from flask import render_template, redirect, request, jsonify
from flask_wtf.csrf import CSRFProtect, CSRFError
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.document.reader.website import WebsiteReader
from app.damath.assistant import get_rag_assistant
import os
import app.models as damathModel
from . import damath

rag_assistant = None
llm_model = None
embeddings_model = None

@damath.route('/initialize', methods=['POST'])
def initialize():
    global rag_assistant, llm_model, embeddings_model

    data = request.json
    llm_model = data.get("llm_model", "llama3")
    embeddings_model = data.get("embeddings_model", "nomic-embed-text")

    rag_assistant = get_rag_assistant(llm_model=llm_model, embeddings_model=embeddings_model)

    if rag_assistant:
        pdf_file_path = os.path.join(os.path.dirname(__file__), 'Damath_Data.pdf')
        print(f"Checking for PDF file at: {pdf_file_path}")

        if os.path.exists(pdf_file_path):
            reader = PDFReader()
            with open(pdf_file_path, 'rb') as file:
                rag_documents = reader.read(file)
                if rag_documents:
                    rag_assistant.knowledge_base.load_documents(rag_documents, upsert=True)
                    return jsonify({"status": "Assistant initialized and PDF added successfully"}), 200
                else:
                    return jsonify({"error": "Failed to read PDF"}), 500
        else:
            return jsonify({"error": "PDF file not found"}), 500
    else:
        return jsonify({"error": "Failed to initialize assistant"}), 500

@damath.route('/chat', methods=['POST'])
def chat():
    global rag_assistant
    if not rag_assistant:
        return jsonify({"error": "Assistant not initialized"}), 400

    data = request.json
    user_message = data.get("message", "")

    response = ""
    for delta in rag_assistant.run(user_message):
        response += delta

    return jsonify({"response": response}), 200

@damath.route('/clear_knowledge_base', methods=['POST'])
def clear_knowledge_base():
    global rag_assistant
    if not rag_assistant or not rag_assistant.knowledge_base or not rag_assistant.knowledge_base.vector_db:
        return jsonify({"error": "Assistant not initialized or knowledge base not found"}), 400

    rag_assistant.knowledge_base.vector_db.clear()
    return jsonify({"status": "Knowledge base cleared"}), 200


@damath.route('/hello/')
@damath.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', person=name)


# @damath.route('/add_url', methods=['POST'])
# def add_url():
#     global rag_assistant
#     if not rag_assistant:
#         return jsonify({"error": "Assistant not initialized"}), 400

#     data = request.json
#     input_url = data.get("url", "")

#     scraper = WebsiteReader(max_links=2, max_depth=1)
#     web_documents = scraper.read(input_url)
#     if web_documents:
#         rag_assistant.knowledge_base.load_documents(web_documents, upsert=True)
#         return jsonify({"status": "URL added successfully"}), 200
#     else:
#         return jsonify({"error": "Failed to read URL"}), 500
