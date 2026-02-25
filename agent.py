import os
from pathlib import Path
import json

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import mlflow
from mlflow.genai.agent_server import invoke
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse, create_text_output_item

load_dotenv()

mlflow.langchain.autolog()

DIRECTORY_PATH = Path(__file__).parent
CONFIG_PATH = DIRECTORY_PATH / "mcp.json"

async def get_mcp_tools():
    """Get tools from MCP servers."""
    mcp_config = json.loads(CONFIG_PATH.read_text())
    mcp_client = MultiServerMCPClient(mcp_config["mcpServers"])
    tools = await mcp_client.get_tools()
    return tools


async def build_agent():
    """Construct the OpenAI agent."""
    model = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    )
    tools = await get_mcp_tools()
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="Use the available tools to help the user answer their request.",
    )
    return agent


@invoke()
async def invocation(request: ResponsesAgentRequest) -> ResponsesAgentResponse:
    """Invoke the agent."""
    msgs = [i.model_dump() for i in request.input]
    
    agent = await build_agent()
    input = {"messages": msgs}
    response = await agent.ainvoke(input=input)
    last_message: AIMessage = response["messages"][-1]
    output = [create_text_output_item(text=last_message.content, id="msg_1")]
    return ResponsesAgentResponse(
        output=output,
    )
