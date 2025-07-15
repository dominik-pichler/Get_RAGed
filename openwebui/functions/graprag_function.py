"""
GraphRAG Integration Function for Open WebUI
Place this file in: ./openwebui/functions/graphrag_function.py
"""

import requests
import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class GraphRAGFunction:
    """
    GraphRAG integration function for Open WebUI
    """

    def __init__(self):
        self.graphrag_url = os.getenv("GRAPHRAG_API_URL", "http://graphrag-service:8001")
        self.name = "graphrag_query"
        self.description = "Query knowledge graph using GraphRAG for enhanced contextual responses"

    class UserValves(BaseModel):
        """User-configurable settings"""
        graphrag_endpoint: str = Field(
            default="http://graphrag-service:8001",
            description="GraphRAG service endpoint URL"
        )
        max_results: int = Field(
            default=10,
            description="Maximum number of results to return"
        )
        similarity_threshold: float = Field(
            default=0.7,
            description="Similarity threshold for graph search"
        )
        enable_global_search: bool = Field(
            default=True,
            description="Enable global search across entire knowledge graph"
        )
        enable_local_search: bool = Field(
            default=True,
            description="Enable local search within specific graph communities"
        )

    def __init__(self):
        self.valves = self.UserValves()

    async def action(
            self,
            body: dict,
            __user__: Optional[dict] = None,
            __event_emitter__=None,
            __event_call__=None,
    ) -> Optional[dict]:
        """
        Main action function called by Open WebUI
        """

        try:
            # Extract query from the message
            messages = body.get("messages", [])
            if not messages:
                return body

            user_query = messages[-1].get("content", "")

            # Emit status update
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Querying knowledge graph...", "done": False},
                    }
                )

            # Query GraphRAG service
            graph_results = await self._query_graphrag(user_query)

            if graph_results:
                # Enhance the user's query with graph context
                enhanced_context = self._format_graph_context(graph_results)

                # Modify the last message to include graph context
                enhanced_query = f"""
Context from Knowledge Graph:
{enhanced_context}

User Query: {user_query}

Please provide a comprehensive answer using the above context and your knowledge.
"""

                messages[-1]["content"] = enhanced_query
                body["messages"] = messages

                # Emit completion status
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "Knowledge graph context added", "done": True},
                        }
                    )

            return body

        except Exception as e:
            print(f"GraphRAG function error: {e}")
            # Return original body if there's an error
            return body

    async def _query_graphrag(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Query the GraphRAG service
        """
        try:
            payload = {
                "query": query,
                "max_results": self.valves.max_results,
                "similarity_threshold": self.valves.similarity_threshold,
                "global_search": self.valves.enable_global_search,
                "local_search": self.valves.enable_local_search
            }

            response = requests.post(
                f"{self.valves.graphrag_endpoint}/query",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"GraphRAG API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error querying GraphRAG: {e}")
            return None

    def _format_graph_context(self, results: Dict[str, Any]) -> str:
        """
        Format graph query results into readable context
        """
        context_parts = []

        # Add global search results
        if "global_results" in results:
            context_parts.append("## Global Knowledge Graph Insights:")
            for result in results["global_results"][:3]:  # Top 3 results
                context_parts.append(f"- {result.get('summary', result.get('content', 'N/A'))}")

        # Add local search results
        if "local_results" in results:
            context_parts.append("\n## Relevant Graph Communities:")
            for result in results["local_results"][:3]:  # Top 3 results
                context_parts.append(f"- {result.get('summary', result.get('content', 'N/A'))}")

        # Add entity relationships
        if "entities" in results:
            context_parts.append("\n## Key Entities and Relationships:")
            for entity in results["entities"][:5]:  # Top 5 entities
                name = entity.get("name", "Unknown")
                description = entity.get("description", "No description")
                context_parts.append(f"- **{name}**: {description}")

        return "\n".join(context_parts)


# Initialize the function
graphrag_function = GraphRAGFunction()