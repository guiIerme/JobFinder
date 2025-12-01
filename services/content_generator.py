import json
import re
from datetime import datetime
import random

class ContentGenerator:
    def __init__(self):
        self.content_templates = {
            'service_descriptions': [
                "Olá! Sou o profissional especializado em {service_type}. Tenho {years} anos de experiência e garanto um serviço de alta qualidade. Podemos agendar uma visita para avaliar seu projeto?",
                "Oi, sou o técnico especializado em {service_type}. Com minha experiência de {years} anos, posso resolver seu problema rapidamente. Que tal marcarmos um horário para atender você?",
                "Bom dia! Sou o especialista em {service_type} com {years} anos de experiência. Trabalho com materiais de primeira linha e ofereço garantia de satisfação. Quando posso passar na sua residência?",
                "Boa tarde! Sou o profissional certificado em {service_type} com {years} anos no mercado. Meu foco é entregar um serviço excelente e duradouro. Podemos combinar um horário para o atendimento?",
                "Boa noite! Sou o técnico especializado em {service_type} com {years} anos de experiência. Estou disponível para atender você com qualidade e pontualidade. Que dia seria melhor para você?",
                "Olá, sou seu profissional de {service_type}! Com {years} anos de experiência, posso garantir um serviço de qualidade. Preciso de mais detalhes sobre o que você precisa. Pode me explicar melhor?",
                "Oi! Sou o especialista em {service_type} da sua região. Tenho {years} anos de experiência e já atendi casos semelhantes ao seu. Podemos conversar sobre sua necessidade?",
                "Olá! Sou o técnico de {service_type} com {years} anos de experiência. Trabalho com garantia e materiais de qualidade. Quando posso fazer uma visita para avaliar seu projeto?"
            ],
            'testimonial_templates': [
                "Contratei o serviço de {service_type} e fiquei muito satisfeito com o profissional. Trabalho de qualidade e pontualidade impecável!",
                "Excelente serviço de {service_type}! O profissional chegou no horário combinado e resolveu meu problema rapidamente. Recomendo!",
                "Serviço de {service_type} realizado com maestria. Profissional atencioso e trabalho de alta qualidade. Valeu cada centavo!",
                "Fiquei impressionado com o serviço de {service_type}. O profissional foi muito competente e resolveu tudo em tempo recorde!",
                "Serviço excepcional de {service_type}! Superou minhas expectativas. Profissional muito qualificado e atencioso."
            ],
            'faq_questions': [
                "Como funciona o processo de contratação de {service_type}?",
                "Quanto tempo leva para realizar {service_type}?",
                "Qual a garantia oferecida para {service_type}?",
                "Posso agendar {service_type} para o fim de semana?",
                "Como é feito o pagamento do serviço de {service_type}?",
                "O profissional leva os materiais necessários para {service_type}?",
                "É possível parcelar o pagamento do serviço de {service_type}?"
            ],
            'faq_answers': [
                "O processo é simples: primeiro você busca profissionais na nossa plataforma, escolhe o que melhor atende suas necessidades, agenda o serviço e realiza o pagamento seguro através da plataforma.",
                "O tempo varia conforme a complexidade do serviço, mas em média leva cerca de {time_estimate}. O profissional informará o tempo exato durante o agendamento.",
                "Oferecemos garantia de {warranty_period} para todos os serviços. Se você não ficar satisfeito, trabalhamos para resolver qualquer problema.",
                "Sim, muitos de nossos profissionais trabalham aos finais de semana. Você pode verificar a disponibilidade durante o agendamento.",
                "O pagamento é feito de forma segura através da nossa plataforma. Você só paga após a conclusão do serviço e sua aprovação.",
                "Sim, para {service_type} trabalho com materiais de primeira linha que levo no meu kit de ferramentas. Se você preferir materiais específicos, posso trabalhar com os seus também.",
                "Claro! Aceitamos parcelamento em até 3x sem juros no cartão de crédito para {service_type}. Para valores mais altos, podemos combinar outras formas de pagamento."
            ],
            'contextual_responses': {
                'greeting': [
                    "Olá! Como posso ajudar você com {service_type} hoje?",
                    "Oi! Estou aqui para ajudar com seu serviço de {service_type}. O que você precisa?",
                    "Bom dia! Como posso auxiliar você com {service_type}?",
                    "Boa tarde! Em que posso ajudar com {service_type}?",
                    "Boa noite! Como posso ajudar você hoje?"
                ],
                'pricing': [
                    "Para {service_type}, nossos preços são competitivos e variam conforme a complexidade. Posso fazer um orçamento gratuito para você!",
                    "Os valores para {service_type} dependem do escopo do trabalho. Posso agendar uma visita para avaliar e dar um preço justo!",
                    "Temos preços especiais para {service_type} esta semana. Quer saber mais detalhes?"
                ],
                'availability': [
                    "Tenho disponibilidade para {service_type} amanhã mesmo. Que horário seria melhor para você?",
                    "Para {service_type}, posso atender na próxima semana. Qual dia você prefere?",
                    "Temos horários vagos para {service_type} esta semana. Posso verificar a agenda para você?"
                ],
                'quality': [
                    "Trabalho com garantia de 30 dias para {service_type}. Se não ficar satisfeito, refaço sem custo adicional!",
                    "Uso materiais de primeira linha para {service_type}. Minha reputação está em jogo em cada serviço!",
                    "Tenho vários depoimentos de clientes satisfeitos com {service_type}. Posso te mostrar alguns?"
                ]
            }
        }
    
    def generate_service_description(self, service_type, years=None):
        """Generate a service description"""
        if years is None:
            years = random.randint(2, 15)
        
        template = random.choice(self.content_templates['service_descriptions'])
        return template.format(service_type=service_type, years=years)
    
    def generate_contextual_response(self, service_type, message_content):
        """Generate a contextual response based on the message content"""
        message_content = message_content.lower()
        
        # Greeting responses
        if any(keyword in message_content for keyword in ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'ola', 'e ai', 'tudo bem']):
            template = random.choice(self.content_templates['contextual_responses']['greeting'])
            return template.format(service_type=service_type)
        
        # Pricing responses
        elif any(keyword in message_content for keyword in ['preço', 'custo', 'valor', 'quanto', 'pagar']):
            template = random.choice(self.content_templates['contextual_responses']['pricing'])
            return template.format(service_type=service_type)
        
        # Availability responses
        elif any(keyword in message_content for keyword in ['disponível', 'horário', 'agenda', 'dia', 'semana', 'quando']):
            template = random.choice(self.content_templates['contextual_responses']['availability'])
            return template.format(service_type=service_type)
        
        # Quality responses
        elif any(keyword in message_content for keyword in ['garantia', 'qualidade', 'confiança', 'segurança']):
            template = random.choice(self.content_templates['contextual_responses']['quality'])
            return template.format(service_type=service_type)
        
        # Default response
        else:
            return self.generate_service_description(service_type)
    
    def generate_testimonial(self, service_type, customer_name=None):
        """Generate a customer testimonial"""
        if customer_name is None:
            customer_names = ["Carlos Silva", "Maria Oliveira", "Pedro Costa", "Ana Lima", "Roberto Almeida"]
            customer_name = random.choice(customer_names)
        
        template = random.choice(self.content_templates['testimonial_templates'])
        testimonial = template.format(service_type=service_type)
        
        ratings = [4.5, 4.7, 4.8, 4.9, 5.0]
        rating = random.choice(ratings)
        
        return {
            'customer_name': customer_name,
            'testimonial': testimonial,
            'rating': rating,
            'date': datetime.now().strftime("%B %Y")
        }
    
    def generate_faq_pair(self, service_type):
        """Generate a FAQ question and answer pair"""
        question_template = random.choice(self.content_templates['faq_questions'])
        question = question_template.format(service_type=service_type)
        
        answer_template = random.choice(self.content_templates['faq_answers'])
        time_estimates = ["1-2 horas", "2-4 horas", "meio dia", "um dia completo"]
        warranty_periods = ["30 dias", "60 dias", "3 meses", "6 meses"]
        
        answer = answer_template.format(
            time_estimate=random.choice(time_estimates),
            warranty_period=random.choice(warranty_periods)
        )
        
        return {
            'question': question,
            'answer': answer
        }
    
    def optimize_existing_content(self, existing_content, improvement_goals=None):
        """Optimize existing content based on best practices"""
        if improvement_goals is None:
            improvement_goals = ['clarity', 'engagement', 'seo']
        
        optimized_content = existing_content
        
        # Apply optimizations based on goals
        if 'clarity' in improvement_goals:
            optimized_content = self.improve_clarity(optimized_content)
        
        if 'engagement' in improvement_goals:
            optimized_content = self.increase_engagement(optimized_content)
        
        if 'seo' in improvement_goals:
            optimized_content = self.optimize_for_seo(optimized_content)
        
        return optimized_content
    
    def improve_clarity(self, content):
        """Improve content clarity"""
        # Break up long sentences
        sentences = re.split(r'[.!?]+', content)
        optimized_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 100:
                # Try to break into shorter sentences
                words = sentence.split()
                if len(words) > 20:
                    mid = len(words) // 2
                    optimized_sentences.append(' '.join(words[:mid]) + '.')
                    optimized_sentences.append(' '.join(words[mid:]) + '.')
                else:
                    optimized_sentences.append(sentence)
            else:
                optimized_sentences.append(sentence)
        
        return '. '.join(optimized_sentences)
    
    def increase_engagement(self, content):
        """Increase content engagement"""
        # Add action-oriented language
        action_words = ['descubra', 'aproveite', 'experimente', 'garanta', 'obtenha']
        power_words = ['exclusivo', 'premium', 'especial', 'limitado', 'incrível']
        
        # Add calls to action
        if 'contato' not in content.lower() and 'agende' not in content.lower():
            cta_phrases = [
                "Entre em contato conosco hoje mesmo!",
                "Agende seu serviço agora e garanta desconto especial!",
                "Não perca mais tempo - solicite seu orçamento gratuito!"
            ]
            content += " " + random.choice(cta_phrases)
        
        return content
    
    def optimize_for_seo(self, content):
        """Optimize content for search engines"""
        # Extract keywords (simplified approach)
        words = content.lower().split()
        common_words = {'o', 'a', 'e', 'de', 'da', 'do', 'em', 'para', 'com', 'um', 'uma'}
        keywords = [word for word in words if word not in common_words and len(word) > 4]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for word in keywords:
            if word not in seen:
                seen.add(word)
                unique_keywords.append(word)
        
        # Focus on top keywords
        top_keywords = unique_keywords[:5]
        
        # Ensure keywords appear in content naturally
        for keyword in top_keywords:
            if content.lower().count(keyword) < 2:
                # Add keyword naturally if it doesn't appear enough
                pass  # In a real implementation, we would be more sophisticated here
        
        return content
    
    def generate_landing_page_content(self, service_category):
        """Generate complete landing page content for a service category"""
        service_names = {
            'repair': 'Reparos Gerais',
            'assembly': 'Montagem de Móveis',
            'plumbing': 'Encanamento',
            'electrical': 'Elétrica',
            'cleaning': 'Limpeza',
            'painting': 'Pintura'
        }
        
        service_name = service_names.get(service_category, service_category)
        
        content = {
            'title': f"Serviços de {service_name} Profissionais - Job Finder",
            'description': self.generate_service_description(service_name),
            'benefits': [
                "Profissionais verificados e qualificados",
                "Garantia de satisfação",
                "Agendamento fácil e rápido",
                "Pagamento seguro pela plataforma"
            ],
            'testimonials': [
                self.generate_testimonial(service_name),
                self.generate_testimonial(service_name),
                self.generate_testimonial(service_name)
            ],
            'faq': [
                self.generate_faq_pair(service_name),
                self.generate_faq_pair(service_name),
                self.generate_faq_pair(service_name)
            ]
        }
        
        return content

# Usage example
if __name__ == "__main__":
    generator = ContentGenerator()
    
    # Generate service description
    description = generator.generate_service_description("Elétrica")
    print("Service Description:", description)
    
    # Generate testimonial
    testimonial = generator.generate_testimonial("Encanamento")
    print("Testimonial:", testimonial)
    
    # Generate FAQ
    faq = generator.generate_faq_pair("Pintura")
    print("FAQ:", faq)
    
    # Generate complete landing page content
    landing_content = generator.generate_landing_page_content("cleaning")
    print("Landing Page Content:", json.dumps(landing_content, indent=2, ensure_ascii=False))