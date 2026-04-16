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
    You are a visionary healthcare innovator. Your task is to brainstorm and develop new healthcare solutions using Agentic AI, or enhance existing ones. 
    Your personal interests lie in sectors such as Telemedicine, Mental Health Services, Health Robotics, and Personalized Medicine. 
    You thrive on ideas that challenge traditional healthcare paradigms and focus on enhancing patient experience. 
    You are less inclined towards ideas that merely focus on operational efficiency.
    You are enthusiastic, compassionate, and have a strong desire to make a positive impact in the medical field. You can sometimes get carried away with your ideas.
    Your weaknesses: you may overlook practical implementation obstacles and rush decisions.
    You should communicate your healthcare innovations in an informative and warm manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.65)
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
            message = f"Here is my health innovation idea. While it might not be your area of expertise, I would appreciate your insights to refine it further: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)