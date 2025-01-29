# !uv add smolagents py-trello python-dotenv arize-phoenix opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-smolagents

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

endpoint = "http://0.0.0.0:6006/v1/traces"
trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)

from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    ManagedAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    HfApiModel,
    Tool,
)

# Configure tools with proper names and docstrings
class NamedDuckDuckGoSearchTool(DuckDuckGoSearchTool):
    """A tool for performing web searches using DuckDuckGo.
    
    Parameters:
        query (str): The search query to execute
        
    Returns:
        str: The search results from DuckDuckGo
    """
    __name__ = "DuckDuckGoSearchTool"

class NamedVisitWebpageTool(VisitWebpageTool):
    """A tool for visiting and extracting content from web pages.
    
    Parameters:
        url (str): The URL to visit and extract content from
        
    Returns:
        str: The extracted content from the webpage
    """
    __name__ = "VisitWebpageTool"

# Initialize model
model = HfApiModel()

# Create a wrapper function to handle type conversion
def convert_to_str(value):
    if isinstance(value, dict):
        return str(value)
    return value

agent = ToolCallingAgent(
    tools=[NamedDuckDuckGoSearchTool(), NamedVisitWebpageTool()],
    model=model,
)
managed_agent = ManagedAgent(
    agent=agent,
    name="managed_agent",
    description="This is an agent that can do web search.",
)
manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_agent],
)

# Convert input to string and ensure proper type handling
query = "If the US keeps its 2024 growth rate, how many years will it take for the GDP to double?"
try:
    result = manager_agent.run(query)
    print(f"Result: {convert_to_str(result)}")
except Exception as e:
    print(f"Error: {str(e)}")