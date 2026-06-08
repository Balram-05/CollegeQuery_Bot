from langchain_core.messages import HumanMessage
from src.components.graph_bot import CollegeGraphBot

class PredictPipeline:
    def __init__(self):
        self.bot = CollegeGraphBot()

    def generate_response(self, question: str, thread_id: str) -> str:
        config = {"configurable": {"thread_id": thread_id}}
        result = self.bot.graph.invoke(
            {"messages": [HumanMessage(content=question)]},
            config=config
        )
        # Extract the final AI Response content from message stack
        return result["messages"][-1].content
