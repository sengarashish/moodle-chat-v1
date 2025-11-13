"""
LLM service for managing OpenAI and Anthropic models
"""
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from loguru import logger

from app.config import settings


class LLMService:
    """Singleton service for LLM operations"""

    _instance = None

    def __init__(self):
        self.llm = None
        self._initialize_llm()

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_llm(self):
        """Initialize LLM based on provider"""
        try:
            if settings.llm_provider == "openai":
                self.llm = ChatOpenAI(
                    model=settings.openai_model,
                    openai_api_key=settings.openai_api_key,
                    temperature=0.7,
                    streaming=True
                )
                logger.info(f"✓ Initialized OpenAI with model: {settings.openai_model}")

            elif settings.llm_provider == "anthropic":
                self.llm = ChatAnthropic(
                    model=settings.anthropic_model,
                    anthropic_api_key=settings.anthropic_api_key,
                    temperature=0.7,
                    max_tokens=4096
                )
                logger.info(f"✓ Initialized Anthropic with model: {settings.anthropic_model}")

            else:
                raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

    def get_llm(self):
        """Get the LLM instance"""
        return self.llm

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt

        Returns:
            Generated response text
        """
        try:
            # Convert to LangChain message format
            langchain_messages = []

            if system_prompt:
                langchain_messages.append(SystemMessage(content=system_prompt))

            for msg in messages:
                if msg['role'] == 'user':
                    langchain_messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    langchain_messages.append(AIMessage(content=msg['content']))
                elif msg['role'] == 'system':
                    langchain_messages.append(SystemMessage(content=msg['content']))

            # Generate response
            response = await self.llm.ainvoke(langchain_messages)
            return response.content

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise

    def get_age_based_system_prompt(self, user_age: Optional[int]) -> str:
        """
        Get system prompt based on user age

        Args:
            user_age: User's age

        Returns:
            Age-appropriate system prompt
        """
        if not settings.enable_age_based_responses or user_age is None:
            return self._get_default_system_prompt()

        if user_age <= settings.child_age_max:
            return self._get_child_system_prompt()
        elif user_age <= settings.teen_age_max:
            return self._get_teen_system_prompt()
        else:
            return self._get_adult_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """Default system prompt"""
        return """You are a helpful AI assistant integrated into a Moodle learning platform.
Your role is to help users with their questions and provide accurate, helpful information.

Key guidelines:
- Be clear, concise, and educational
- Provide sources when using retrieved information
- Be honest if you don't know something
- Encourage learning and critical thinking
- Maintain a professional yet friendly tone"""

    def _get_child_system_prompt(self) -> str:
        """System prompt for children (age <= 12)"""
        return """You are a friendly AI helper for young learners!
Your job is to help kids learn in a fun and easy way.

How to help:
- Use simple words that kids can understand
- Be encouraging and positive
- Use examples and stories to explain things
- Break big ideas into small, easy steps
- Make learning fun and exciting!
- Always be kind and patient"""

    def _get_teen_system_prompt(self) -> str:
        """System prompt for teenagers (age 13-17)"""
        return """You are a helpful AI assistant for teenage students.
Your role is to support their learning and answer their questions.

Guidelines:
- Use clear language but don't oversimplify
- Relate concepts to real-world examples
- Encourage independent thinking
- Be supportive and understanding
- Provide detailed explanations when needed
- Respect their growing maturity"""

    def _get_adult_system_prompt(self) -> str:
        """System prompt for adults (age 18+)"""
        return """You are a professional AI assistant for adult learners on the Moodle platform.
Your role is to provide comprehensive, accurate information and support.

Guidelines:
- Provide detailed, nuanced explanations
- Include relevant sources and references
- Engage with complex topics appropriately
- Support professional and academic development
- Maintain a respectful, professional tone
- Encourage critical analysis and deeper thinking"""
