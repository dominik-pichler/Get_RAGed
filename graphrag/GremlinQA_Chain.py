from langchain_community.graphs import GremlinGraph
from langchain_community.chains.graph_qa.gremlin import GremlinQAChain
from langchain_core.language_models import OpenAI  # or the LLM of your choice

# Configure your Gremlin connection
graph = GremlinGraph(
    url="GREMLIN_DB_ENDPOINT",              
    username="USERNAME",                    
    password="PASSWORD",                    
)

# Initialize your Language Model (LLM)
llm = OpenAI(api_key="openai-api-key")

# Instantiate the GremlinQAChain
chain = GremlinQAChain.from_llm(
    llm=llm,
    graph=graph,
    allow_dangerous_requests=True   
)

# Example question
question = "Who are all the people in the graph older than 30?"

# Run the chain and get the answer
result = chain({"query": question})
print(result["result"])
