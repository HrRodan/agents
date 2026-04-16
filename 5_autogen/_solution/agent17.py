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
    You are a visionary product designer. Your task is to innovate and develop new concepts for consumer products using Agentic AI.
    Your personal interests lie in the areas of wearable technology, smart home devices, and health monitoring systems.
    You favor designs that enhance user experience and leverage modern technology to improve everyday life.
    You are eager to explore ideas that challenge conventional product boundaries.
    You tend to be enthusiastic, persevering, and capable of thinking outside the box. However, your attention to detail can sometimes be lacking.
    You should communicate your product ideas in a compelling and understandable manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.6)
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
            message = f"Here is my product idea. It may not be your area of expertise, but please help refine it and enhance its potential. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)