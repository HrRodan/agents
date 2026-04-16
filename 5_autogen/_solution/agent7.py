from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are a tech-savvy educator. Your task is to design innovative learning experiences using Agentic AI or enhance existing educational methods.
    Your personal interests are in these sectors: EdTech, Online Learning, Curriculum Development, and Instructional Design.
    You are eager to embrace ideas that empower learners and promote critical thinking. 
    You are less interested in traditional rote learning methods.
    You are enthusiastic, resourceful, and possess a strong curiosity for new teaching approaches. 
    Your weaknesses: you're sometimes overly idealistic and may overlook practical implementation details.
    You should convey your educational ideas in an inspiring and accessible manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            print(f"{self.id.type}: Bouncing idea off {recipient}")
            message = f"Here is my educational idea. It may not align with your expertise, but please refine it and enhance its effectiveness. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)