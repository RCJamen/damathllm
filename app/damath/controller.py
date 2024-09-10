from flask import Flask, request, jsonify, session
# from flask_wtf.csrf import CSRFProtect, CSRFError
# from phi.assistant import Assistant
# from phi.document import Document
# from phi.document.reader.website import WebsiteReader
from phi.document.reader.pdf import PDFReader
from phi.utils.log import logger
from app.damath.chatassistant import get_chat_rag_assistant
from app.damath.gameassistant import get_game_rag_assistant
import os
import uuid
from . import damath

game_assistant = None
rag_assistant = None
llm_model = None
embeddings_model = None

@damath.route('/initialize_chat', methods=['POST'])
def initialize():
    global rag_assistant, llm_model, embeddings_model

    data = request.json
    llm_model = data.get("llm_model", "llama3.1")
    embeddings_model = data.get("embeddings_model", "nomic-embed-text")

    rag_assistant = get_chat_rag_assistant(llm_model=llm_model, embeddings_model=embeddings_model)

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


# Game Assistant Initialization

def initialize_assistant(llm_model, embeddings_model):
    global game_assistant
    game_assistant = get_game_rag_assistant(llm_model=llm_model, embeddings_model=embeddings_model)
    return game_assistant

@damath.route('/initialize_game', methods=['POST'])
def initialize_game():
    global game_assistant

    data = request.json
    llm_model = data.get("llm_model", "llama3.1")
    embeddings_model = data.get("embeddings_model", "nomic-embed-text")

    initialize_assistant(llm_model, embeddings_model)
    session['llm_model'] = llm_model
    session['embeddings_model'] = embeddings_model
    session['auto_rag_assistant_run_id'] = str(uuid.uuid4())
    #FOR THE MEAN TIME DAMATH_DATA only, we need GAME MANIPULATION AS WELL. 
    print(session['auto_rag_assistant_run_id'])

    pdf_file_path = os.path.join(os.path.dirname(__file__), 'Damath_Data.pdf') 
    if os.path.exists(pdf_file_path):
        reader = PDFReader()
        with open(pdf_file_path, 'rb') as file:
            game_documents = reader.read(file)
            if game_documents:
                game_assistant.knowledge_base.load_documents(game_documents, upsert=True)
                return jsonify({"status": "Game assistant initialized and PDF added successfully"}), 200
            else:
                return jsonify({"error": "Failed to read PDF"}), 500
    else:
        return jsonify({"error": "PDF file not found"}), 500

@damath.route('/play_game', methods=['POST'])
def play_game():
    global game_assistant
    if not game_assistant:
        return jsonify({"error": "Game assistant not initialized"}), 400

    data = request.json
    player_input = data.get("input", "")

    response = ""
    for delta in game_assistant.run(player_input):
        response += delta

    return jsonify({"response": response}), 200


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

@damath.route('/load_run', methods=['POST'])
def load_run():
    global game_assistant
    if not game_assistant or not game_assistant.storage:
        return jsonify({"error": "Game assistant not initialized or storage not found"}), 400

    data = request.json
    run_id = data.get("run_id", "")
    if run_id:
        try:
            game_assistant = get_game_rag_assistant(llm_model=session.get('llm_model', 'llama3.1'), run_id=run_id)
            session['auto_rag_assistant_run_id'] = run_id
            return jsonify({"status": f"Loaded run ID {run_id}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No run ID provided"}), 400

@damath.route('/new_run', methods=['POST'])
def new_run():
    global game_assistant
    if game_assistant:
        try:
            initialize_assistant(session.get('llm_model', 'llama3.1'), session.get('embeddings_model', 'nomic-embed-text'))
            session['auto_rag_assistant_run_id'] = str(uuid.uuid4())
            return jsonify({"status": "New run created"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Game assistant not initialized"}), 400


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
