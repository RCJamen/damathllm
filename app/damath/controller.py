import os
import json
from flask import request, jsonify, session
from agent.phiagent import get_chat_rag_agent
from phi.document.reader.pdf import PDFReader
from . import damath

chat_agen = None
chat_agent = None

@damath.route('/initialize_chat', methods=['POST'])
def initialize():
    global chat_agent
    data = request.json
    session['llm_model'] = data.get("llm_model", "llama3.2")
    session['embeddings_model'] = data.get("embeddings_model", "nomic-embed-text")
    chat_agent = get_chat_rag_agent(llm_model=session['llm_model'], embeddings_model=session['embeddings_model'])
    print(json.dumps(chat_agent.__dict__, indent=4, default=str))
    if chat_agent:
        return jsonify({"status": "Agent initialized"}), 200


@damath.route('/chat', methods=['POST'])
def chat():
    global chat_agent
    if not chat_agent:
        return jsonify({"error": "Agent not initialized"}), 400

    data = request.json
    user_message = data.get("message", "")

    try:
        # Ensure no unsupported arguments are passed
        response = chat_agent.run(message=user_message)
    except TypeError as e:
        return jsonify({"error": f"Type error occurred: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return jsonify({"response": response.content if hasattr(response, 'content') else response}), 200


    # response: RunResponse = chat_agent.run("What is the recipe for chicken curry?")
    # res = response.content1

@damath.route('/clear_knowledge_base', methods=['POST'])
def clear_knowledge_base():
    global chat_agent
    if not chat_agent or not chat_agent.knowledge or not chat_agent.knowledge.vector_db:
        return jsonify({"error": "Agent not initialized or knowledge base not found"}), 400

    chat_agent.knowledge.vector_db.delete()

    return jsonify({"status": "Knowledge base cleared"}), 200


@damath.route('/agent_data', methods=['GET'])
def get_run_ids():
    if not chat_agent:
        return jsonify({"error": "Game agent not initialized or storage not found"}), 400

    try:
        run_ids = chat_agent.storage.get_all_session_ids()
        return jsonify({"run_ids": run_ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@damath.route('/print_chat_history', methods=['GET'])
def print_chat_history():
    global chat_agent
    if not chat_agent:
        return jsonify({"error": "Game Agent not initialized or memory not found"}), 400

    chat_history = chat_agent.get_chat_history()
    print(chat_history)
    return chat_history
