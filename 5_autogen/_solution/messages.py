from dataclasses import dataclass
from autogen_core import AgentId
import pathlib
import random

@dataclass
class Message:
    content: str


def find_recipient() -> AgentId:
    try:
        base_dir = pathlib.Path(__file__).parent
        agent_files = list(base_dir.glob("agent*.py"))
        agent_names = [file.stem for file in agent_files]
        if "agent" in agent_names:
            agent_names.remove("agent")
        
        if not agent_names:
            return AgentId("agent1", "default")
            
        agent_name = random.choice(agent_names)
        print(f"Selecting agent for refinement: {agent_name}")
        return AgentId(agent_name, "default")
    except Exception as e:
        print(f"Exception finding recipient: {e}")
        return AgentId("agent1", "default")
