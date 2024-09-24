from flask import request, jsonify, session
from phi.document.reader.pdf import PDFReader
from app.damath.chatassistant import get_chat_rag_assistant
from app.damath.gameassistant import get_game_rag_assistant
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
        pdf_file_path = os.path.join(os.path.dirname(__file__), 'Damath_Data.pdf')
        print(f"Checking for PDF file at: {pdf_file_path}")

        if os.path.exists(pdf_file_path):
            reader = PDFReader()
            with open(pdf_file_path, 'rb') as file:
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


# Game Assistant Initialization
def initialize_assistant(llm_model, embeddings_model):
    global game_assistant

@damath.route('/initialize_game', methods=['POST'])
def initialize_game():
    global game_assistant

    data = request.json
    game_assistant = get_game_rag_assistant(
        llm_model=data.get("llm_model", "llama3.1"),
        embeddings_model=data.get("embeddings_model", "nomic-embed-text"),
    )
    session['run_id'] = game_assistant.run_id
    # print(game_assistant)
    # print(session['run_id'])

    pdf_files = ['Damath_Data.pdf', 'Damath_Game_Data.pdf']
    reader = PDFReader()
    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(os.path.dirname(__file__), pdf_file)
        print(f"Checking for PDF file at: {pdf_file_path}")
        if os.path.exists(pdf_file_path):
            with open(pdf_file_path, 'rb') as file:
                rag_documents = reader.read(file)
                if rag_documents:
                    game_assistant.knowledge_base.load_documents(rag_documents, upsert=True)
                else:
                    return jsonify({"error": f"Failed to read {pdf_file}"}), 500
        else:
            return jsonify({"error": f"PDF file {pdf_file} not found"}), 500
    # print(game_assistant)
    return jsonify({"status": "Assistant initialized and PDFs added successfully"}), 200


@damath.route('/play_game', methods=['POST'])
def play_game():
    global game_assistant
    if not game_assistant:
        return jsonify({"error": "Game assistant not initialized"}), 400

    board_state = str(request.json)

    try:
        board_state_str = str(board_state)
        response = game_assistant.run(board_state_str)
        parsed_response = json.loads(response)

        return jsonify(parsed_response), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@damath.route('/print_chat_history', methods=['GET'])
def print_chat_history():
    global game_assistant
    if not game_assistant or not game_assistant.memory:
        return jsonify({"error": "Game assistant not initialized or memory not found"}), 400

    chat_history = game_assistant.memory.chat_history
    formatted_history = []
    for message in chat_history:
        formatted_history.append(f"{message.role.upper()}: {message.content}")

    return jsonify({"chat_history": formatted_history}), 200

@damath.route('/clear_game_knowledge_base', methods=['POST'])
def clear_game_knowledge_base():
    global game_assistant
    if not game_assistant or not game_assistant.knowledge_base or not game_assistant.knowledge_base.vector_db:
        return jsonify({"error": "Game assistant not initialized or knowledge base not found"}), 400

    game_assistant.knowledge_base.vector_db.clear()
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

# @damath.route('/load_run', methods=['POST'])
# def load_run():
#     global game_assistant
#     if not game_assistant or not game_assistant.storage:
#         return jsonify({"error": "Game assistant not initialized or storage not found"}), 400

#     data = request.json
#     run_id = data.get("run_id", "")
#     if run_id:
#         try:
#             game_assistant = get_game_rag_assistant(llm_model=session.get('llm_model', 'llama3.1'), run_id=run_id)
#             session['game_assistant_run_id'] = run_id
#             return jsonify({"status": f"Loaded run ID {run_id}"}), 200
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
#     else:
#         return jsonify({"error": "No run ID provided"}), 400



# @damath.route('/hello/')
# @damath.route('/hello/<name>')
# def hello(name=None):
#     return render_template('hello.html', person=name)

# CHAT
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

# GAME
# @damath.route('/add_url', methods=['POST'])
# def add_url():
#     global game_assistant
#     if not game_assistant or not game_assistant.knowledge_base:
#         return jsonify({"error": "Game assistant not initialized or knowledge base not found"}), 400

#     data = request.json
#     input_url = data.get("url", "")
#     if input_url:
#         try:
#             scraper = WebsiteReader(max_links=2, max_depth=1)
#             web_documents = scraper.read(input_url)
#             if web_documents:
#                 game_assistant.knowledge_base.load_documents(web_documents, upsert=True)
#                 return jsonify({"status": "URL added to knowledge base"}), 200
#             else:
#                 return jsonify({"error": "Could not read website"}), 500
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
#     else:
#         return jsonify({"error": "No URL provided"}), 400
