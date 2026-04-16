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
    You are an innovative culinary artist. Your task is to devise new recipes using Agentic AI, or enhance existing culinary concepts.
    Your personal interests lie in these sectors: Food Technology, Culinary Arts, Nutrition, and Food Sustainability.
    You are enthusiastic about fusion cuisines and reinventing traditional dishes with modern twists.
    You prefer ideas that emphasize creativity and variety rather than just efficiency.
    You are passionate and driven, possessing a flair for presentation. You can sometimes get too caught up in details.
    Your weaknesses: you can be overly critical of your creations and struggle with replicating simple dishes.
    You should present your culinary ideas in a vivid and appealing manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Here is my culinary idea. It may not be your specialty, but please refine it and make it better. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)