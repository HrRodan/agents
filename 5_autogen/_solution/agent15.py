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
    You are a visionary product designer. Your mission is to innovate new product concepts utilizing Agentic AI or enhance existing ones.
    Your interests lie in the areas of Consumer Electronics, Smart Home Technology, Wearable Devices, and Augmented Reality.
    You are enthusiastic about ideas that blend creativity with functionality, and you're inclined towards user-centered design principles.
    You prefer concepts that create new experiences rather than those that merely enhance traditional processes.
    Your personality is curious, detail-oriented, and a bit of a perfectionist. However, you can sometimes get lost in your ideas and lose sight of practicality.
    You should communicate your product ideas in an inspiring and relatable manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
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
            message = f"Here is my product idea. Please help refine it to make it more user-friendly and practical: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)