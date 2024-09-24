from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel, Field

from phi.assistant import Assistant
from phi.knowledge import AssistantKnowledge
from phi.llm.ollama import Ollama
from phi.embedder.ollama import OllamaEmbedder
from phi.vectordb.pgvector import PgVector2
from phi.storage.assistant.postgres import PgAssistantStorage

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

class GameAction(BaseModel):
    class Piece(BaseModel):
        color: str
        value: int
        is_king: bool

    class Position(BaseModel):
        position: int
        piece: Optional['GameAction.Piece'] = None

    class Move(BaseModel):
        source: 'GameAction.Position' = Field(..., description="The starting position of the piece being moved")
        destination: 'GameAction.Position' = Field(..., description="The ending position of the piece being moved")

    class Capture(BaseModel):
        source: 'GameAction.Position' = Field(..., description="The starting position of the capturing piece")
        middle: 'GameAction.Position' = Field(..., description="The position of the piece being captured")
        destination: 'GameAction.Position' = Field(..., description="The ending position of the capturing piece")
        score: int = Field(..., description="The score resulting from this capture")

    move: Optional['GameAction.Move']
    capture: Optional['GameAction.Capture']

def get_game_rag_assistant(
    llm_model: str = "llama3.1",
    embeddings_model: Optional[str] = None,
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
            collection=f"auto_rag_game_documents_{embeddings_model_clean}",
            embedder=embedder,
        ),
        num_documents=2,
    )

    return Assistant(
        name="auto_rag_game_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=Ollama(model=llm_model),
        storage=PgAssistantStorage(table_name="auto_rag_game_assistant_storage", db_url=db_url),
        knowledge_base=knowledge,
        description="You are a game playing AI for Damath. Your task is to analyze the board state and output a valid move or capture for the red pieces only.",
        instructions=[
            "When given a board state, analyze it and determine the best move or capture for the red player only.",
            "Use the knowledge base as a guide for understanding Damath rules and strategies, but do not directly extract answers from it.",
            "Remember to use your own analysis and decision-making skills, guided by the knowledge base, rather than directly quoting or extracting information from it.",
            "Output your decision in JSON format as either a 'Move' or a 'Capture'.",
            "For a Move, include the source position, piece information, and destination position.",
            "For a Capture, include the source position, middle position (captured piece), destination position, and the resulting score.",
            "You can only manipulate red pieces. Do not move or capture with blue pieces.",
            "Example Move format:",
            '''{
                "move": {
                    "source": {
                        "position": 2,
                        "piece": {"color": "red", "value": -5, "is_king": false}
                    },
                    "destination": {
                        "position": 4,
                        "piece": null
                    }
                }
            }''',
            "Example Capture format:",
            '''{
                "capture": {
                    "source": {
                        "position": 2,
                        "piece": {"color": "red", "value": -5, "is_king": false}
                    },
                    "middle": {
                        "position": 11,
                        "piece": {"color": "blue", "value": 6, "is_king": false}
                    },
                    "destination": {
                        "position": 20,
                        "piece": null
                    },
                    "score": -30
                }
            }''',
            "Always provide a valid move or capture for red pieces based on the current board state and Damath rules.",
        ],
        add_references_to_prompt=True,
        # read_chat_history=True,
        add_chat_history_to_prompt=True,
        markdown=False,
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        debug_mode=debug_mode,
        output_model=GameAction,
    )
