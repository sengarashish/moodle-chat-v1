"""
LangGraph agent service with intelligent query routing
"""
from typing import Dict, Any, List, Optional, Literal, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, AIMessage
from loguru import logger
import operator

from app.config import settings
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.services.search_service import SearchService


class AgentState(TypedDict):
    """State for the agent graph - using latest LangGraph patterns"""
    query: str
    history: List[Dict[str, str]]
    user_age: Optional[int]
    rag_results: Optional[List[Dict[str, Any]]]
    search_results: Optional[List[Dict[str, Any]]]
    route: Optional[Literal["rag", "llm", "search"]]
    response: Optional[str]
    sources: Annotated[List[str], operator.add]  # Use operator.add for list concatenation


class AgentService:
    """LangGraph-based agent with query routing"""

    def __init__(self):
        self.vector_store = VectorStoreService.get_instance()
        self.llm_service = LLMService.get_instance()
        self.search_service = SearchService()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow using latest API"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("route_query", self._route_query)
        workflow.add_node("retrieve_from_rag", self._retrieve_from_rag)
        workflow.add_node("search_web", self._search_web)
        workflow.add_node("generate_response", self._generate_response)

        # Define edges - using START instead of set_entry_point
        workflow.add_edge(START, "route_query")

        workflow.add_conditional_edges(
            "route_query",
            self._decide_route,
            {
                "rag": "retrieve_from_rag",
                "search": "search_web",
                "llm": "generate_response"
            }
        )

        workflow.add_edge("retrieve_from_rag", "generate_response")
        workflow.add_edge("search_web", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    async def _route_query(self, state: AgentState) -> AgentState:
        """
        Determine which route to take for the query
        Uses LLM to classify the query type
        """
        query = state["query"]
        logger.info(f"Routing query: {query[:100]}...")

        # Use LLM to classify query intent
        classification_prompt = f"""Classify the following user query into one of these categories:

1. "knowledge_base" - Questions about course materials, documents, or information that would be in uploaded PDFs/URLs
2. "current_events" - Questions about recent events, news, or time-sensitive information
3. "general" - General questions, explanations, help with concepts

Query: {query}

Respond with ONLY one word: knowledge_base, current_events, or general"""

        try:
            messages = [{"role": "user", "content": classification_prompt}]
            classification = await self.llm_service.generate_response(messages)
            classification = classification.strip().lower()

            if "knowledge_base" in classification:
                state["route"] = "rag"
                logger.info("→ Route: RAG (Knowledge Base)")
            elif "current_events" in classification or "current" in classification:
                state["route"] = "search"
                logger.info("→ Route: Web Search")
            else:
                state["route"] = "llm"
                logger.info("→ Route: Direct LLM")

        except Exception as e:
            logger.error(f"Routing failed: {e}, defaulting to RAG")
            state["route"] = "rag"  # Default to RAG

        return state

    def _decide_route(self, state: AgentState) -> str:
        """Decide which node to go to next"""
        return state["route"]

    async def _retrieve_from_rag(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents from RAG system"""
        query = state["query"]
        logger.info("Retrieving from RAG...")

        try:
            results = await self.vector_store.search(
                query=query,
                top_k=settings.rag_top_k,
                score_threshold=settings.rag_score_threshold
            )

            if results:
                state["rag_results"] = results
                logger.info(f"✓ Retrieved {len(results)} relevant documents")
            else:
                logger.info("No relevant documents found, falling back to direct LLM")
                state["route"] = "llm"  # Fall back if no results

        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
            state["route"] = "llm"  # Fall back on error

        return state

    async def _search_web(self, state: AgentState) -> AgentState:
        """Search the web for current information"""
        query = state["query"]
        logger.info("Searching web...")

        try:
            results = await self.search_service.search(query, max_results=5)

            if results:
                state["search_results"] = results
                logger.info(f"✓ Found {len(results)} web results")
            else:
                logger.info("No web results found, falling back to direct LLM")
                state["route"] = "llm"

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            state["route"] = "llm"

        return state

    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate final response using LLM"""
        query = state["query"]
        history = state.get("history", [])
        user_age = state.get("user_age")

        logger.info("Generating response...")

        try:
            # Build context
            context = ""
            sources = []

            # Add RAG context if available
            if state.get("rag_results"):
                context += "\n\n=== Relevant Information from Knowledge Base ===\n"
                for i, result in enumerate(state["rag_results"], 1):
                    context += f"\n[Source {i}]: {result['text']}\n"
                    source_info = result['metadata'].get('source', 'Unknown')
                    sources.append(source_info)
                context += "\n"

            # Add web search context if available
            if state.get("search_results"):
                context += "\n\n=== Current Information from Web ===\n"
                context += self.search_service.format_search_results(state["search_results"])
                sources.extend([r['link'] for r in state["search_results"]])

            # Get age-appropriate system prompt
            system_prompt = self.llm_service.get_age_based_system_prompt(user_age)

            if context:
                system_prompt += f"\n\nUse the following context to answer the user's question:\n{context}"
                system_prompt += "\n\nCite your sources when using this information."

            # Build message history
            messages = []
            for msg in history[-settings.max_history_length:]:
                messages.append(msg)

            # Add current query
            messages.append({"role": "user", "content": query})

            # Generate response
            response = await self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt
            )

            state["response"] = response
            state["sources"] = list(set(sources))  # Remove duplicates

            logger.info("✓ Response generated")

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            state["response"] = "I apologize, but I encountered an error while processing your request. Please try again."
            state["sources"] = []

        return state

    async def process_query(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the agent

        Args:
            query: User's question
            history: Chat history
            user_age: User's age for customization

        Returns:
            Response with content and sources
        """
        logger.info(f"Processing query: {query[:100]}...")

        initial_state: AgentState = {
            "query": query,
            "history": history or [],
            "user_age": user_age,
            "rag_results": None,
            "search_results": None,
            "route": None,
            "response": None,
            "sources": None
        }

        try:
            # Run through the graph
            final_state = await self.graph.ainvoke(initial_state)

            return {
                "content": final_state["response"],
                "sources": final_state.get("sources", []),
                "route": final_state.get("route", "unknown"),
                "model": settings.llm_provider
            }

        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return {
                "content": "I apologize, but I encountered an error. Please try again.",
                "sources": [],
                "route": "error",
                "model": settings.llm_provider
            }
