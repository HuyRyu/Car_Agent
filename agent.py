from llama_index.agent.openai import OpenAIAgent, advanced_tool_call_parser

class CarAssistantAgent():
    def __init__(self, tools, llm, verbose=False):
        self.agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=verbose)

    def __call__(self, query):
        return self.agent.chat(query)
