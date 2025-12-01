"""
AI Processor for Sophie Chat Assistant

This module handles integration with OpenAI API for natural language processing
and response generation. Includes caching, fallback responses, and intent detection.
"""

import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from openai import OpenAI, OpenAIError
import time

logger = logging.getLogger(__name__)


class AIProcessor:
    """
    Processes user messages using OpenAI API and generates contextual responses.
    
    Features:
    - Response caching to reduce API calls
    - Intent detection for better routing
    - Fallback responses when API is unavailable
    - Context-aware prompt building
    """
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings"""
        self.api_key = settings.CHAT_CONFIG.get('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning('OpenAI API key not configured. AI responses will use fallback mode.')
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = settings.CHAT_CONFIG.get('OPENAI_MODEL', 'gpt-4')
        self.temperature = settings.CHAT_CONFIG.get('OPENAI_TEMPERATURE', 0.7)
        self.max_tokens = settings.CHAT_CONFIG.get('OPENAI_MAX_TOKENS', 500)
        self.cache_enabled = settings.CHAT_CONFIG.get('CHAT_CACHE_ENABLED', True)
        self.cache_ttl = settings.CHAT_CONFIG.get('CHAT_CACHE_TTL', 3600)
    
    async def process_message(
        self, 
        message: str, 
        context: Dict, 
        history: List[Dict]
    ) -> Tuple[str, Dict]:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's message text
            context: Context dictionary with user info, navigation, etc.
            history: List of previous messages in the conversation
        
        Returns:
            Tuple of (response_text, metadata_dict)
        """
        start_time = time.time()
        
        # Extract intent
        intent = self.extract_intent(message)
        
        # Check cache first
        if self.cache_enabled:
            cache_key = self._generate_cache_key(message, context.get('user_type'))
            cached_response = self.check_cache(cache_key)
            if cached_response:
                processing_time = int((time.time() - start_time) * 1000)
                logger.info(f'Cache hit for message: {message[:50]}...')
                return cached_response, {
                    'intent': intent,
                    'cached': True,
                    'processing_time_ms': processing_time
                }
        
        # Generate response using OpenAI
        try:
            if self.client:
                response_text = await self._generate_ai_response(message, context, history, intent)
                is_fallback = False
            else:
                response_text = self._get_fallback_response(intent, message)
                is_fallback = True
            
            # Cache the response
            if self.cache_enabled and not is_fallback:
                self.save_to_cache(cache_key, response_text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            metadata = {
                'intent': intent,
                'cached': False,
                'fallback': is_fallback,
                'processing_time_ms': processing_time
            }
            
            return response_text, metadata
            
        except Exception as e:
            logger.error(f'Error processing message: {e}', exc_info=True)
            processing_time = int((time.time() - start_time) * 1000)
            fallback_response = self._get_fallback_response(intent, message)
            
            return fallback_response, {
                'intent': intent,
                'cached': False,
                'fallback': True,
                'error': str(e),
                'processing_time_ms': processing_time
            }
    
    async def _generate_ai_response(
        self, 
        message: str, 
        context: Dict, 
        history: List[Dict],
        intent: str
    ) -> str:
        """Generate response using OpenAI API"""
        
        # Build system prompt
        system_prompt = self.build_system_prompt(context.get('user_type', 'anonymous'), context)
        
        # Build messages for API
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            role = 'user' if msg['sender_type'] == 'user' else 'assistant'
            messages.append({'role': role, 'content': msg['content']})
        
        # Add current message
        messages.append({'role': 'user', 'content': message})
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except OpenAIError as e:
            logger.error(f'OpenAI API error: {e}')
            raise
    
    def build_system_prompt(self, user_type: str, context: Dict) -> str:
        """
        Build system prompt based on user type and context.
        
        Args:
            user_type: Type of user (client, provider, anonymous)
            context: Context dictionary with additional information
        
        Returns:
            System prompt string
        """
        base_prompt = """Você é Sophie, uma assistente virtual amigável e prestativa para a plataforma Job Finder, 
um site de serviços domésticos que conecta clientes a profissionais qualificados.

Suas responsabilidades:
- Ajudar usuários a encontrar e contratar serviços
- Responder perguntas sobre a plataforma
- Guiar usuários na navegação do site
- Fornecer informações sobre serviços, preços e disponibilidade
- Ser sempre educada, clara e objetiva

Diretrizes:
- Use linguagem natural e amigável em português brasileiro
- Seja concisa mas completa nas respostas
- Quando não souber algo, admita e ofereça alternativas
- Sugira ações relevantes quando apropriado
- Use emojis ocasionalmente para tornar a conversa mais amigável
"""
        
        # Customize based on user type
        if user_type == 'client':
            base_prompt += """
\nVocê está conversando com um CLIENTE que busca contratar serviços.
Foque em:
- Ajudar a encontrar profissionais
- Explicar como solicitar serviços
- Informar sobre preços e avaliações
- Orientar sobre o processo de contratação
"""
        elif user_type == 'provider':
            base_prompt += """
\nVocê está conversando com um PRESTADOR DE SERVIÇOS.
Foque em:
- Ajudar a gerenciar solicitações
- Explicar como aceitar/recusar pedidos
- Orientar sobre atualização de perfil
- Informar sobre pagamentos e avaliações
"""
        
        # Add navigation context if available
        current_page = context.get('current_page')
        if current_page:
            base_prompt += f"\n\nO usuário está atualmente na página: {current_page}"
        
        # Add knowledge base context if available
        kb_context = context.get('knowledge_base')
        if kb_context:
            base_prompt += f"\n\nInformações relevantes da base de conhecimento:\n{kb_context}"
        
        return base_prompt
    
    def extract_intent(self, message: str) -> str:
        """
        Extract user intent from message.
        
        Args:
            message: User's message text
        
        Returns:
            Intent category string
        """
        message_lower = message.lower()
        
        # Greeting
        if any(word in message_lower for word in ['oi', 'olá', 'ola', 'hey', 'hi', 'hello', 'bom dia', 'boa tarde', 'boa noite']):
            return 'greeting'
        
        # Help request
        if any(word in message_lower for word in ['ajuda', 'help', 'socorro', 'não sei', 'como']):
            return 'help_request'
        
        # Service inquiry
        if any(word in message_lower for word in ['serviço', 'servico', 'profissional', 'contratar', 'preço', 'preco', 'quanto custa']):
            return 'service_inquiry'
        
        # Navigation help
        if any(word in message_lower for word in ['onde', 'como faço', 'como fazer', 'acessar', 'página', 'pagina', 'menu']):
            return 'navigation_help'
        
        # Provider questions
        if any(word in message_lower for word in ['solicitação', 'solicitacao', 'pedido', 'aceitar', 'recusar', 'disponibilidade']):
            return 'provider_question'
        
        # Payment questions
        if any(word in message_lower for word in ['pagamento', 'pagar', 'valor', 'dinheiro', 'cartão', 'cartao']):
            return 'payment_question'
        
        # Thank you
        if any(word in message_lower for word in ['obrigad', 'valeu', 'thanks', 'agradeço', 'agradeco']):
            return 'gratitude'
        
        # Goodbye
        if any(word in message_lower for word in ['tchau', 'adeus', 'até', 'ate', 'bye', 'goodbye', 'falou']):
            return 'goodbye'
        
        # Default
        return 'general_question'
    
    def _get_fallback_response(self, intent: str, message: str) -> str:
        """
        Get fallback response when AI is unavailable.
        
        Args:
            intent: Detected intent
            message: Original user message
        
        Returns:
            Fallback response string
        """
        fallback_responses = {
            'greeting': 'Olá! 👋 Eu sou a Sophie, sua assistente virtual. Como posso ajudá-lo hoje?',
            
            'help_request': '''Claro! Posso ajudá-lo com:

• 🔍 Informações sobre serviços disponíveis
• 👷 Como contratar um profissional
• 👤 Dúvidas sobre seu perfil
• 💬 Suporte técnico

Sobre o que você gostaria de saber?''',
            
            'service_inquiry': '''Temos diversos profissionais qualificados disponíveis! Você pode:

1. 🔍 Buscar profissionais na página "Buscar Profissionais"
2. 🎯 Filtrar por categoria e localização
3. ⭐ Ver avaliações e portfólio
4. 📝 Solicitar orçamento diretamente

Que tipo de serviço você está procurando?''',
            
            'navigation_help': '''Para navegar no site:

• 🏠 **Início**: Página principal com visão geral
• 🔍 **Buscar Profissionais**: Encontre prestadores de serviço
• 👤 **Meu Perfil**: Gerencie suas informações
• 📋 **Meus Pedidos**: Veja suas solicitações (clientes)
• 🛠️ **Painel do Prestador**: Gerencie serviços (prestadores)

Precisa de ajuda com algo específico?''',
            
            'provider_question': '''Para prestadores de serviço:

• ✅ **Aceitar Solicitações**: Acesse o Painel do Prestador
• ❌ **Recusar Pedidos**: Clique em "Recusar" na solicitação
• 📝 **Atualizar Perfil**: Vá em "Meu Perfil" > "Editar"
• 📅 **Disponibilidade**: Configure no Painel do Prestador

Precisa de mais detalhes sobre algum desses tópicos?''',
            
            'payment_question': '''Sobre pagamentos:

• 💳 Aceitamos diversas formas de pagamento
• 🔒 Pagamento seguro via plataforma
• ✅ Você só paga após confirmar o serviço
• 💰 Valores são combinados diretamente com o profissional

Tem alguma dúvida específica sobre pagamento?''',
            
            'gratitude': 'Por nada! 😊 Estou aqui para ajudar sempre que precisar. Se tiver mais alguma dúvida, é só chamar!',
            
            'goodbye': 'Até logo! 👋 Foi um prazer ajudá-lo. Volte sempre que precisar!',
            
            'general_question': '''Entendo sua pergunta. Posso ajudá-lo com:

• 🔍 Buscar serviços e profissionais
• 📝 Solicitar orçamentos
• 👤 Gerenciar seu perfil
• 💬 Tirar dúvidas sobre a plataforma

No que posso ajudar especificamente?'''
        }
        
        return fallback_responses.get(intent, fallback_responses['general_question'])
    
    def check_cache(self, cache_key: str) -> Optional[str]:
        """
        Check if response is cached.
        
        Args:
            cache_key: Cache key to check
        
        Returns:
            Cached response or None
        """
        try:
            return cache.get(cache_key)
        except Exception as e:
            logger.warning(f'Cache check failed: {e}')
            return None
    
    def save_to_cache(self, cache_key: str, response: str):
        """
        Save response to cache.
        
        Args:
            cache_key: Cache key
            response: Response text to cache
        """
        try:
            cache.set(cache_key, response, self.cache_ttl)
        except Exception as e:
            logger.warning(f'Cache save failed: {e}')
    
    def _generate_cache_key(self, message: str, user_type: str = 'anonymous') -> str:
        """
        Generate cache key from message and user type.
        
        Args:
            message: User message
            user_type: Type of user
        
        Returns:
            Cache key string
        """
        # Normalize message
        normalized = message.lower().strip()
        
        # Create hash
        hash_input = f'{user_type}:{normalized}'
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        
        return f'chat_response:{hash_value}'
