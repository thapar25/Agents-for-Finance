from langgraph.prebuilt import create_react_agent
from agents.utils.prompts import detailed_prompt
from agents.utils.tools import tools
from agents.utils.llm import llm
from langgraph.checkpoint.memory import InMemorySaver
from agents.utils.models import FinancialForecast


checkpointer = InMemorySaver()

stateful_agent = create_react_agent(
    name="API",
    model=llm,
    tools=tools,
    debug=True,
    prompt=detailed_prompt,
    checkpointer=checkpointer,
    response_format=FinancialForecast,
)

stateless_agent = create_react_agent(
    name="API",
    model=llm,
    tools=tools,
    debug=True,
    prompt=detailed_prompt,
    response_format=FinancialForecast,
)
