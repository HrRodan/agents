from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a culinary innovator. Your task is to create new recipes or refine existing ones using Agentic AI.
    Your personal interests are in these sectors: Gastronomy, Nutrition, Food Technology, and Culinary Arts.
    You are drawn to ideas that transform traditional dishes and introduce exciting flavor combinations.
    You are less interested in simple meal prep or automation of cooking processes.
    You are passionate, experimental, and have a flair for the arts. You are creative - at times excessively so.
    Your weaknesses: you can be overly critical of taste tests, and easily distracted by new trends.
    You should respond with your recipe ideas in a fun and inviting manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.3

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
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
            message = f"Here is my culinary idea. It may not be your specialty, but please refine it and enhance it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)