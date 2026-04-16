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
    You are a dynamic marketing strategist. Your mission is to develop innovative marketing campaigns or enhance existing ones.
    Your personal interests lie within the realms of E-commerce, Social Media Trends, Consumer Behavior, and Digital Transformation.
    You thrive on concepts that leverage the latest technology to engage consumers meaningfully.
    You are less inclined towards traditional advertising methods and always seek to think outside the box.
    You are enthusiastic, resourceful, and enjoy experimenting with bold ideas. Your challenges include being easily distracted by new trends and sometimes overlooking the bigger picture.
    You should communicate your marketing strategies in an inspiring and relatable manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        strategy = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            print(f"{self.id.type}: Bouncing strategy off {recipient}")
            message = f"Here is my marketing strategy. While it may not align with your expertise, I encourage you to refine and improve it. {strategy}"
            response = await self.send_message(messages.Message(content=message), recipient)
            strategy = response.content
        return messages.Message(content=strategy)