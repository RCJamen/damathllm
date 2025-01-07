from flask import request, jsonify, session
from phi.document.reader.pdf import PDFReader
from agent.newagent import get_chat_rag_assistant
import os
import json
from . import damath

# Code Documentation
# Variables:
# llm_model
# embeddings_model
# chat_assistant(llm-model, embedding model)
# game_assistant(llm-model, embedding model)


game_assistant = None
chat_assistant = None

@damath.route('/initialize_chat', methods=['POST'])
def initialize():
    global chat_assistant
    data = request.json
    session['llm_model'] = data.get("llm_model", "llama3.1")
    session['embeddings_model'] = data.get("embeddings_model", "nomic-embed-text")
    chat_assistant = get_chat_rag_assistant(llm_model=session['llm_model'], embeddings_model=session['embeddings_model'])
    print(chat_assistant)
    if chat_assistant:
        doc_file_path = os.path.join(os.path.dirname(__file__), 'Damath_Data.pdf')
        print(f"Checking for PDF file at: {doc_file_path}")

        if os.path.exists(doc_file_path):
            reader = PDFReader()
            with open(doc_file_path, 'rb') as file:
                rag_documents = reader.read(file)
                if rag_documents:
                    chat_assistant.knowledge_base.load_documents(rag_documents, upsert=True)
                    return jsonify({"status": "Assistant initialized and PDF added successfully"}), 200
                else:
                    return jsonify({"error": "Failed to read PDF"}), 500
        else:
            return jsonify({"error": "PDF file not found"}), 500
    else:
        return jsonify({"error": "Failed to initialize assistant"}), 500


@damath.route('/chat', methods=['POST'])
def chat():
    global chat_assistant
    if not chat_assistant:
        return jsonify({"error": "Assistant not initialized"}), 400

    data = request.json
    user_message = data.get("message", "")

    response = ""
    for delta in chat_assistant.run(user_message):
        response += delta

    return jsonify({"response": response}), 200


@damath.route('/clear_knowledge_base', methods=['POST'])
def clear_knowledge_base():
    global chat_assistant
    if not chat_assistant or not chat_assistant.knowledge_base or not chat_assistant.knowledge_base.vector_db:
        return jsonify({"error": "Assistant not initialized or knowledge base not found"}), 400

    chat_assistant.knowledge_base.vector_db.clear()

    return jsonify({"status": "Knowledge base cleared"}), 200


@damath.route('/get_run_ids', methods=['GET'])
def get_run_ids():
    if not game_assistant or not game_assistant.storage:
        return jsonify({"error": "Game assistant not initialized or storage not found"}), 400

    try:
        run_ids = game_assistant.storage.get_all_run_ids()
        return jsonify({"run_ids": run_ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500