# Copied from: https://mlflow.org/docs/latest/genai/serving/agent-server/

# Need to import the agent to register the functions with the server
import agent  # noqa: F401
from mlflow.genai.agent_server import (
    AgentServer,
    setup_mlflow_git_based_version_tracking,
)
import json

agent_server = AgentServer("ResponsesAgent")
app = agent_server.app

# Optionally, set up MLflow git-based version tracking
# to correspond your agent's traces to a specific git commit
setup_mlflow_git_based_version_tracking()

# Add agent card endpoint
@app.get("/.well-known/agent-card")
async def get_agent_card():
    with open("agent-card.json") as f:
        agent_card = json.load(f)
    return agent_card


def main():
    # To support multiple workers, pass the app as an import string
    agent_server.run(app_import_string="start_server:app")


if __name__ == "__main__":
    main()