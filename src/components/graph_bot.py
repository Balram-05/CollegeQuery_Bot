import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from src.schema.schema import State
from src.components.data_ingestion import DataIngestion

load_dotenv()

class CollegeGraphBot:
    def __init__(self):
        if not os.environ.get("GROQ_API_KEY"):
            os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"

        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        
        # Ensure ingestion has been setup and retrieve semantic database links
        ingestion = DataIngestion()
        ingestion.ingest() 
        self.retriever = ingestion.get_retriever()
        
        # Compile graph structure
        self.graph = self._build_graph()

    def rewrite_query(self, state: State):
        """Rewrites incoming short queries into stand-alone descriptive contexts."""
        messages = state["messages"]
        prompt = f"Based on the conversation history below, convert the latest question into a standalone question that makes sense without the context of previous messages.\n\nConversation History:\n{messages}\n\nPlease return ONLY the rewritten standalone question, nothing else."
        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    def rag_node(self, state: State):
        """Extracts text structures, builds prompt schemas, and delivers contextual conclusions."""
        standalone_question = state["messages"][-1].content
        docs = self.retriever.invoke(standalone_question)
        context = "\n\n".join(doc.page_content for doc in docs)

        prompt = f"You are a helpful college assistant. Answer the question using ONLY the provided context.\n\nContext from college documents:\n{context}\n\nQuestion:\n{standalone_question}\n\nIf the information is not available in the context, respond with: \"I don't have information about this in the available documents.\"\n\nProvide a clear and concise answer."
        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    def _build_graph(self):
        builder = StateGraph(State)
        builder.add_node("rewrite_query", self.rewrite_query)
        builder.add_node("rag_node", self.rag_node)

        builder.add_edge(START, "rewrite_query")
        builder.add_edge("rewrite_query", "rag_node")

        memory = InMemorySaver()
        return builder.compile(checkpointer=memory)
