from langgraph.prebuilt import create_react_agent
from agents.utils.prompts import analyst_prompt
from agents.utils.tools import tools
from agents.utils.llm import llm
from langgraph.checkpoint.memory import InMemorySaver


checkpointer = InMemorySaver()

stateful_agent = create_react_agent(
    name="API",
    model=llm,
    tools=tools,
    debug=True,
    prompt=analyst_prompt,
    checkpointer=checkpointer,
)

stateless_agent = create_react_agent(
    name="API",
    model=llm,
    tools=tools,
    debug=True,
    prompt=analyst_prompt,
)
