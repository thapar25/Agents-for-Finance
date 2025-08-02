from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from agents.utils.prompts import analyst_prompt
from agents.utils.tools import tools
from agents.utils.llm import llm

checkpointer = InMemorySaver()

agent = create_react_agent(
    model=llm,
    prompt=analyst_prompt,
    tools=tools,
    debug=True,
    name="Simple Agent",
    checkpointer=checkpointer,
)
