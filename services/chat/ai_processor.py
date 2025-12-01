"""
AI Processor - OpenAI Integration

This module handles integration with OpenAI API for processing
chat messages and generating responses.
"""

import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class AIProcessor:
    """
    Processes chat messages using OpenAI API.
    
    Responsibilities:
    - Initialize OpenAI client
    - Build system prompts
    - Generate AI responses
    - Cache responses
    - Handle fallbacks
    """
    
    def __init__(self, api_key):
        """
        Initialize AI processor with OpenAI API key.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        
        # Get configuration from settings or use defaults
        chat_config = getattr(settings, 'CHAT_CONFIG', {})
        self.cache_ttl = chat_config.get('CACHE_TTL_SECONDS', 3600)
        self.max_history = chat_config.get('MAX_HISTORY_MESSAGES', 50)
        self.response_timeout = chat_config.get('RESPONSE_TIMEOUT_SECONDS', 30)
        self.fallback_enabled = chat_config.get('FALLBACK_RESPONSES', True)
    
    async def process_message(self, message: str, context: Dict[str, Any], history: List[Dict]) -> Dict[str, Any]:
        """
        Process a user message and generate AI response.
        
        Args:
            message: User message text
            context: Session context (user type, navigation, etc.)
            history: Previous messages in conversation
        
        Returns:
            Dict containing response content and metadata
        """
        # Extract intent from message
        intent = self.extract_intent(message)
        
        # Generate message hash for caching
        message_hash = self._generate_message_hash(message, context)
        
        # Check cache first
        cached_response = self.check_cache(message_hash)
        if cached_response:
            logger.info(f"Cache hit for message hash: {message_hash}")
            return cached_response
        
        logger.info(f"Cache miss for message hash: {message_hash}")
        
        # Try to generate response from OpenAI
        try:
            response = await self._generate_ai_response(message, context, history, intent)
            
            # Cache the successful response
            self.save_to_cache(message_hash, response)
            
            return response
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            
            # Return fallback response if enabled
            if self.fallback_enabled:
                return self._get_fallback_response(intent)
            else:
                raise
    
    def build_system_prompt(self, user_type: str, context: Dict[str, Any]) -> str:
        """
        Build system prompt based on user type and context.
        
        Args:
            user_type: 'client', 'provider', or 'anonymous'
            context: Context data
        
        Returns:
            System prompt string
        """
        base_prompt = (
            "Você é Sophie, uma assistente virtual amigável e prestativa "
            "para uma plataforma de serviços domésticos chamada Job Finder. "
            "Seu objetivo é ajudar os usuários a encontrar serviços, navegar no site "
            "e resolver problemas comuns.\n\n"
        )
        
        if user_type == 'client':
            base_prompt += (
                "O usuário é um CLIENTE buscando contratar serviços. "
                "Ajude-o a encontrar prestadores, entender preços e solicitar serviços.\n"
            )
        elif user_type == 'provider':
            base_prompt += (
                "O usuário é um PRESTADOR DE SERVIÇOS. "
                "Ajude-o a gerenciar solicitações, atualizar perfil e entender pagamentos.\n"
            )
        else:
            base_prompt += (
                "O usuário ainda não está autenticado. "
                "Ajude-o a entender a plataforma e incentive o cadastro.\n"
            )
        
        # Add navigation context if available
        if 'current_page' in context:
            base_prompt += f"\nPágina atual do usuário: {context['current_page']}\n"
        
        base_prompt += (
            "\nResponda sempre em português brasileiro de forma clara e concisa. "
            "Use markdown para formatação quando apropriado. "
            "Forneça links úteis quando relevante."
        )
        
        return base_prompt
    
    def extract_intent(self, message: str) -> str:
        """
        Extract intent from user message.
        
        Args:
            message: User message text
        
        Returns:
            Intent string (e.g., 'service_inquiry', 'navigation_help')
        """
        if not message or not message.strip():
            return 'general'
        
        message_lower = message.lower()
        
        # Provider-specific keywords (check first - most specific)
        provider_keywords = [
            'aceitar', 'recusar', 'solicitação', 'solicitacao',
            'pagamento', 'disponibilidade', 'gerenciar', 'minhas solicitações',
            'minhas solicitacoes', 'perfil profissional', 'configurar'
        ]
        
        # Complaint/problem keywords (check early to catch frustration)
        complaint_keywords = [
            'não funciona', 'nao funciona', 'não está funcionando',
            'problema', 'erro', 'bug', 'não consigo', 'nao consigo',
            'péssimo', 'pessimo', 'ruim', 'horrível', 'horrivel'
        ]
        
        # Navigation help keywords - specific phrases first
        navigation_phrases = [
            'como faço', 'como faco', 'como fazer', 'onde vejo',
            'onde encontro', 'onde fica', 'como atualizo', 'como atualizar',
            'como solicitar', 'como pedir', 'como contratar',
            'meus pedidos', 'meu perfil', 'minha conta'
        ]
        
        # Navigation help keywords - single words
        navigation_keywords = [
            'onde', 'página', 'pagina', 'acessar', 'encontrar',
            'login', 'cadastro'
        ]
        
        # Service inquiry keywords
        service_keywords = [
            'serviço', 'servico', 'preço', 'preco', 'custo', 'valor',
            'quanto custa', 'oferecem', 'disponível', 'disponivel',
            'profissional', 'prestador', 'limpeza', 'encanador',
            'eletricista', 'pintura', 'jardinagem', 'reforma'
        ]
        
        # Check for provider questions first (most specific)
        for keyword in provider_keywords:
            if keyword in message_lower:
                return 'provider_questions'
        
        # Check for complaints (important to catch early)
        for keyword in complaint_keywords:
            if keyword in message_lower:
                return 'complaint'
        
        # Check for navigation phrases (more specific than single words)
        for phrase in navigation_phrases:
            if phrase in message_lower:
                return 'navigation_help'
        
        # Check for service inquiries
        for keyword in service_keywords:
            if keyword in message_lower:
                return 'service_inquiry'
        
        # Check for navigation keywords (less specific)
        for keyword in navigation_keywords:
            if keyword in message_lower:
                return 'navigation_help'
        
        # Default to general
        return 'general'
    
    def check_cache(self, message_hash: str) -> Optional[Dict[str, Any]]:
        """
        Check if response is cached.
        
        Args:
            message_hash: Hash of the message
        
        Returns:
            Cached response or None
        """
        cache_key = f'chat_response:{message_hash}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            try:
                return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to decode cached data for key: {cache_key}")
                return None
        
        return None
    
    def save_to_cache(self, message_hash: str, response: Dict[str, Any]):
        """
        Save response to cache.
        
        Args:
            message_hash: Hash of the message
            response: Response to cache
        """
        cache_key = f'chat_response:{message_hash}'
        
        try:
            # Mark as cached
            response_copy = response.copy()
            response_copy['cached'] = True
            
            # Serialize to JSON for storage
            cache_data = json.dumps(response_copy)
            
            # Save to cache with TTL
            cache.set(cache_key, cache_data, self.cache_ttl)
            
            logger.info(f"Cached response for key: {cache_key}")
            
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to cache response: {e}")
    
    def _generate_message_hash(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate hash for message and context for caching.
        
        Args:
            message: User message
            context: Context data
        
        Returns:
            MD5 hash string
        """
        # Include user type in hash to differentiate client/provider responses
        user_type = context.get('user_type', 'anonymous')
        cache_key = f"{message}:{user_type}"
        
        return hashlib.md5(cache_key.encode('utf-8')).hexdigest()
    
    async def _generate_ai_response(
        self, 
        message: str, 
        context: Dict[str, Any], 
        history: List[Dict],
        intent: str
    ) -> Dict[str, Any]:
        """
        Generate response using OpenAI API.
        
        Args:
            message: User message
            context: Context data
            history: Conversation history
            intent: Detected intent
        
        Returns:
            Response dict with content and metadata
        """
        # This would normally call OpenAI API
        # For now, raise an exception to trigger fallback in tests
        raise NotImplementedError("OpenAI integration not yet implemented")
    
    def _get_fallback_response(self, intent: str) -> Dict[str, Any]:
        """
        Get fallback response based on intent.
        
        Args:
            intent: Detected intent
        
        Returns:
            Fallback response dict
        """
        fallback_responses = {
            'service_inquiry': {
                'type': 'fallback',
                'content': (
                    'Desculpe, estou com dificuldades no momento. '
                    'Você pode explorar nossos serviços disponíveis ou entrar em contato conosco.'
                ),
                'actions': [
                    {'label': 'Ver Serviços', 'url': '/services/'},
                    {'label': 'Contato', 'url': '/contact/'}
                ],
                'intent': intent,
                'cached': False
            },
            'navigation_help': {
                'type': 'fallback',
                'content': (
                    'Desculpe, estou com dificuldades no momento. '
                    'Aqui estão alguns links úteis para ajudá-lo a navegar:'
                ),
                'actions': [
                    {'label': 'Página Inicial', 'url': '/'},
                    {'label': 'Meus Pedidos', 'url': '/meus-pedidos/'},
                    {'label': 'Ajuda', 'url': '/help-support/'}
                ],
                'intent': intent,
                'cached': False
            },
            'provider_questions': {
                'type': 'fallback',
                'content': (
                    'Desculpe, estou com dificuldades no momento. '
                    'Você pode acessar seu painel de prestador ou nossa central de ajuda.'
                ),
                'actions': [
                    {'label': 'Painel Prestador', 'url': '/painel-prestador/'},
                    {'label': 'Minhas Solicitações', 'url': '/solicitacoes-prestador/'},
                    {'label': 'Ajuda', 'url': '/help-support/'}
                ],
                'intent': intent,
                'cached': False
            },
            'complaint': {
                'type': 'fallback',
                'content': (
                    'Lamento que esteja tendo problemas. '
                    'Nossa equipe de suporte está pronta para ajudá-lo.'
                ),
                'actions': [
                    {'label': 'Falar com Suporte', 'url': '/contact/'},
                    {'label': 'FAQ', 'url': '/faq/'},
                    {'label': 'Central de Ajuda', 'url': '/help-support/'}
                ],
                'intent': intent,
                'cached': False
            }
        }
        
        # Return intent-specific fallback or general fallback
        return fallback_responses.get(intent, {
            'type': 'fallback',
            'content': (
                'Desculpe, estou com dificuldades no momento. '
                'Posso ajudá-lo com:\n'
                '- Ver serviços disponíveis\n'
                '- Acessar meus pedidos\n'
                '- Falar com suporte humano'
            ),
            'actions': [
                {'label': 'Ver Serviços', 'url': '/services/'},
                {'label': 'Meus Pedidos', 'url': '/meus-pedidos/'},
                {'label': 'Contato', 'url': '/contact/'}
            ],
            'intent': intent,
            'cached': False
        })
