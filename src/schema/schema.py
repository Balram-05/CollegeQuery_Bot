from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from pydantic import BaseModel

# LangGraph Conversation State Schema
class State(TypedDict):
    messages: Annotated[list, add_messages]


# FastAPI User Validation Pydantic Schema
class UserAuthModel(BaseModel):
    username: str
    password: str


# FastAPI Query Request Pydantic Schema
class ChatQueryModel(BaseModel):
    question: str
    thread_id: str
