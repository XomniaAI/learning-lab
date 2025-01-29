# !uv add smolagents py-trello python-dotenv arize-phoenix opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-smolagents

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from smolagents import CodeAgent, ToolCallingAgent, HfApiModel, ManagedAgent, tool
from trello import TrelloClient
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import requests

# Load environment variables
load_dotenv()

# Setup OpenTelemetry with a single tracer
endpoint = "http://0.0.0.0:6006/v1/traces"
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Initialize Trello client
client = TrelloClient(
    api_key=os.getenv('TRELLO_API_KEY'),
    token=os.getenv('TRELLO_TOKEN')
)
board = client.get_board(os.getenv('TRELLO_BOARD_ID'))

# Create documentation search tool
@tool
def search_documentation(query: str) -> str:
    """Search the py-trello documentation for specific information.
    
    Args:
        query: The search query about Trello client functionality
        
    Returns:
        str: Relevant documentation information
    """
    # This is a simplified version - in reality you might want to use a more sophisticated
    # documentation search system or maintain local documentation
    base_url = "https://raw.githubusercontent.com/sarumont/py-trello/master/docs/"
    docs = [
        "api-members.rst",
        "api-boards.rst",
        "api-cards.rst",
        "api-lists.rst",
        "api-organizations.rst"
    ]
    
    results = []
    for doc in docs:
        try:
            response = requests.get(f"{base_url}{doc}")
            if response.status_code == 200:
                content = response.text
                if query.lower() in content.lower():
                    relevant_lines = [line.strip() for line in content.split('\n') 
                                   if query.lower() in line.lower()]
                    if relevant_lines:
                        results.append(f"From {doc}:")
                        results.extend(relevant_lines)
        except Exception as e:
            continue
            
    return "\n".join(results) if results else "No relevant documentation found."

# Create the documentation search agent
doc_search_agent = ToolCallingAgent(
    tools=[search_documentation],
    model=HfApiModel(),
    system_message="""You are a documentation search assistant for the py-trello library.
Your role is to search and interpret the documentation to help understand how to use the Trello client.
When asked a question, search the documentation and provide relevant information about the Trello client's capabilities."""
)

# Wrap the doc search agent as a managed agent
managed_doc_agent = ManagedAgent(
    agent=doc_search_agent,
    name="doc_search",
    description="Searches and interprets py-trello documentation. Use this when you need to understand how to use specific Trello client features."
)

# Create the main code agent with access to the Trello client and managed doc agent
code_agent = CodeAgent(
    tools=[],  # No direct tools needed
    model=HfApiModel(),
    managed_agents=[managed_doc_agent],
    system_message="""You are a Trello automation assistant that can directly interact with the Trello API using the py-trello library.
You have access to the following objects:
- client: A TrelloClient instance already configured with API credentials
- board: The current Trello board object

When you need to understand how to use specific Trello client features, you can ask the doc_search agent for help.
Example: result = doc_search("how to create a card")

Key capabilities of the Trello client:
1. List operations:
   - board.list_lists() -> Get all lists
   - list.list_cards() -> Get all cards in a list
   
2. Card operations:
   - list.add_card(name, desc) -> Create new card
   - card.set_name(name) -> Update card title
   - card.set_description(desc) -> Update description
   - card.change_list(list_id) -> Move card to different list
   - card.add_label(label) -> Add label to card
   
3. Label operations:
   - board.get_labels() -> Get all available labels

You can write and execute Python code to perform any Trello operations using these objects.
If you're unsure about how to use a specific feature, ask the doc_search agent for help.
Always handle errors appropriately and provide clear feedback about operations performed."""
)

if __name__ == "__main__":
    task = 'list the names of all boards the user has access to'

    # Run the task with tracing
    with tracer.start_as_current_span("trello_task") as span:
        try:
            result = code_agent.run(task)
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR), str(e))
            raise