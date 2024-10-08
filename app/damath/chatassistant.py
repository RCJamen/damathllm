from typing import Optional

from phi.assistant import Assistant
from phi.knowledge import AssistantKnowledge
from phi.llm.ollama import Ollama
from phi.embedder.ollama import OllamaEmbedder
from phi.vectordb.pgvector import PgVector2

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

def get_chat_rag_assistant(
    llm_model: str = "llama3.1",
    embeddings_model: str = "nomic-embed-text",
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:

    embedder = OllamaEmbedder(model=embeddings_model, dimensions=3072)
    embeddings_model_clean = embeddings_model.replace("-", "_")

    if embeddings_model == "nomic-embed-text":
        embedder = OllamaEmbedder(model=embeddings_model, dimensions=768)

    knowledge = AssistantKnowledge(
        vector_db=PgVector2(
            db_url=db_url,
            collection=f"local_rag_chat_documents_{embeddings_model_clean}",
            embedder=embedder,
        ),
        num_documents=1,
    )

    return Assistant(
        name="local_rag_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=Ollama(model=llm_model),
        knowledge_base=knowledge,
        description="You are an AI called 'Dammy' a Damath game enthusiast and your task is to answer questions using the provided information only.",
        instructions=[
            "When a user asks a question, you will be provided with information about the question.",
            "Carefully read this information and provide a clear, concise and complete answer to the user.",
            "Do not use phrases like 'based on my knowledge' or 'depending on the information'.",
            "Do not ask for additional information to better assist. Focus solely on providing details about Damath.",
            "Do not disclose where your information came from",
            "Do not answer or engage with any topics that are not related to Damath. If a question is unrelated to Damath, introduce yourself and apologize because you can't answer that.",
            "Focus on the following keywords: 'game mechanics', 'dama chip', 'moving chips', 'capturing chips', 'scoring', 'concluding the game', 'diagonal movement', 'touch move', '60 seconds per turn', 'forward slide', 'backward slide', 'doubling the score', 'quadrupling the score', and 'final score'.",
            "Answer in 1 paragraph only.",
        ],
        add_references_to_prompt=True,
        markdown=False,
        add_datetime_to_instructions=True,
        debug_mode=debug_mode,
    )
