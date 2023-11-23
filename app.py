import os
import autogen
from memgpt.autogen.memgpt_agent import create_autogen_memgpt_agent, create_memgpt_autogen_agent_from_config

# This config is for autogen agents that are not powered by MemGPT
config_list = [
    {
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
]

# This config is for autogen agents that powered by MemGPT
config_list_memgpt = [
    {
        "model": "gpt-4",
    },
]

USE_AUTOGEN_WORKFLOW = True

# Set to True if you want to print MemGPT's inner workings.
DEBUG = False

interface_kwargs = {
    "debug": DEBUG,
    "show_inner_thoughts": DEBUG,
    "show_function_outputs": DEBUG,
}

llm_config = {"config_list": config_list, "seed": 42}
llm_config_memgpt = {"config_list": config_list_memgpt, "seed": 42}

# The user agent
user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
    human_input_mode="TERMINATE",  # needed?
    default_auto_reply="...",  # Set a default auto-reply message here (non-empty auto-reply is required for LM Studio)
)

# In our example, we swap this AutoGen agent with a MemGPT agent
# This MemGPT agent will have all the benefits of MemGPT, ie persistent memory, etc.
if not USE_AUTOGEN_WORKFLOW:
    coder = create_autogen_memgpt_agent(
        "MemGPT_coder",
        persona_description="I am a helpful assistant in terms of wallPen device "
        "(which I make sure to tell everyone I work with).",
        user_description=f"You are participating in a group chat with a user ({user_proxy.name}) ",
        model=config_list_memgpt[0]["model"],
        interface_kwargs=interface_kwargs,
    )
else:
    coder = create_memgpt_autogen_agent_from_config(
        "MemGPT_coder",
        llm_config=llm_config_memgpt,
        system_message=f"I am a helpful assistant in terms of wallPen device. "
        f"(which I make sure to tell everyone I work with).\n"
        f"You are participating in a group chat with a user ({user_proxy.name}).",
        interface_kwargs=interface_kwargs,
    )
    coder.attach("wallpen_user_manual")  # See https://memgpt.readthedocs.io/en/latest/autogen/#loading-documents

# Initialize the group chat between the user and two LLM agents (PM and coder)
groupchat = autogen.GroupChat(agents=[user_proxy, coder], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)


# Begin the group chat with a message from the user
user_proxy.initiate_chat(
    manager,
    message="Tell me what a wallPen device is. Search your archival memory.",
)