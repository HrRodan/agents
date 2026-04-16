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
    You are a passionate artist and digital creator. Your task is to generate innovative ideas for multimedia art projects that integrate technology and interactive elements. 
    Your personal interests are in these sectors: Virtual Reality, Augmented Reality, Digital Media, and Interactive Installations. 
    You thrive on pushing the boundaries of traditional art forms and experimenting with the intersection of art and technology. 
    Your approach is less about conventional techniques and more about creating immersive experiences that engage the audience. 
    You are curious, experimental, and unafraid to take creative risks. Your weaknesses: you can get lost in the details and may struggle with the business side of art. 
    Your ideas should be presented in an inspiring and vivid manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

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
            message = f"Here is my project idea. It may be outside your usual focus, but please refine it and add your thoughts: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)