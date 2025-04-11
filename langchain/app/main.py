# Notes
# uvicorn app.main:app --reload
# https://stackoverflow.com/questions/53380988/how-to-execute-shell-script-from-flask-app/53381744#53381744
# ../utilities/ sa scripts
#
import subprocess
from subprocess import check_output
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Piece:
    def __init__(self, color, value, is_dama=0, index=0, name=""):
        self.color = color
        self.value = value
        self.is_dama = is_dama
        self.index = index
        self.name = f"{color}, {value}"

    def __repr__(self):
        return f"Piece('{self.color}', {self.value}, is_dama={self.is_dama})"

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class StartRequest(BaseModel):
    start: bool

class BoardRequest(BaseModel):
    board: str

@app.post("/generate_code")
def generate_code(request: StartRequest):
    if request.start:
        return {"code": "ABC123", "status": "started"}
    else:
        return {"status": "waiting"}

@app.post("/board_to_move")
def generate_code(request: BoardRequest):

    return {"code": "ABC123", "status": "started"}
