"""
Módulo de SEO para o Job Finder
Otimização para mecanismos de busca e meta tags
"""

from django.utils.html import strip_tags
from django.utils.text import Truncator

class SEOService:
    """
    Serviço para gerenciar otimizações de SEO
    """
    
    @staticmethod
    def generate_meta_tags(title=None, description=None, keywords=None, author=None, 
                          og_title=None, og_description=None, og_image=None, og_url=None):
        """
        Gera tags meta para SEO e Open Graph
        """
        meta_tags = {}
        
        # Meta tags básicas
        if title:
            meta_tags['title'] = title
        if description:
            meta_tags['description'] = Truncator(strip_tags(description)).chars(160)
        if keywords:
            meta_tags['keywords'] = ', '.join(keywords) if isinstance(keywords, list) else keywords
        if author:
            meta_tags['author'] = author
            
        # Open Graph tags
        if og_title:
            meta_tags['og_title'] = og_title
        elif title:
            meta_tags['og_title'] = title
            
        if og_description:
            meta_tags['og_description'] = Truncator(strip_tags(og_description)).chars(200)
        elif description:
            meta_tags['og_description'] = Truncator(strip_tags(description)).chars(200)
            
        if og_image:
            meta_tags['og_image'] = og_image
        if og_url:
            meta_tags['og_url'] = og_url
            
        return meta_tags
    
    @staticmethod
    def generate_breadcrumb(breadcrumb_items):
        """
        Gera estrutura de breadcrumb para SEO
        breadcrumb_items: lista de tuplas (nome, url)
        """
        breadcrumb_list = []
        for i, (name, url) in enumerate(breadcrumb_items):
            breadcrumb_list.append({
                'position': i + 1,
                'name': name,
                'url': url
            })
        return breadcrumb_list
    
    @staticmethod
    def optimize_content(content, target_keywords=None):
        """
        Otimiza conteúdo para SEO
        """
        if not content:
            return content
            
        # Remover tags HTML para análise
        clean_content = strip_tags(content)
        
        # Otimizações básicas
        optimizations = []
        
        # Verificar densidade de palavras-chave
        if target_keywords:
            for keyword in target_keywords:
                count = clean_content.lower().count(keyword.lower())
                density = (count / len(clean_content.split())) * 100 if clean_content else 0
                optimizations.append({
                    'keyword': keyword,
                    'count': count,
                    'density': round(density, 2)
                })
        
        # Verificar comprimento do conteúdo
        word_count = len(clean_content.split())
        optimizations.append({
            'metric': 'word_count',
            'value': word_count
        })
        
        return {
            'content': content,
            'optimizations': optimizations
        }
    
    @staticmethod
    def generate_sitemap_urls():
        """
        Gera URLs para sitemap.xml
        """
        # URLs estáticas
        static_urls = [
            {'location': '/', 'priority': 1.0, 'changefreq': 'daily'},
            {'location': '/login/', 'priority': 0.8, 'changefreq': 'monthly'},
            {'location': '/register/', 'priority': 0.8, 'changefreq': 'monthly'},
            {'location': '/search/', 'priority': 0.9, 'changefreq': 'daily'},
            {'location': '/about/', 'priority': 0.7, 'changefreq': 'monthly'},
            {'location': '/support/', 'priority': 0.8, 'changefreq': 'weekly'},
            {'location': '/faq/', 'priority': 0.6, 'changefreq': 'monthly'},
            {'location': '/terms/', 'priority': 0.5, 'changefreq': 'yearly'},
            {'location': '/privacy/', 'priority': 0.5, 'changefreq': 'yearly'},
        ]
        
        return static_urls

# Funções auxiliares para templates

def get_seo_title(page_title, site_name="Job Finder"):
    """
    Gera título SEO otimizado
    """
    if page_title:
        return f"{page_title} - {site_name}"
    return site_name

def get_seo_description(description, max_length=160):
    """
    Trunca descrição para o tamanho ideal de SEO
    """
    if not description:
        return ""
    return Truncator(strip_tags(description)).chars(max_length)

def get_seo_keywords(base_keywords=None, additional_keywords=None):
    """
    Combina palavras-chave para SEO
    """
    default_keywords = [
        "serviços domésticos",
        "profissionais",
        "reparos",
        "encanamento",
        "elétrica",
        "limpeza",
        "pintura",
        "montagem"
    ]
    
    keywords = default_keywords.copy()
    
    if base_keywords:
        if isinstance(base_keywords, list):
            keywords.extend(base_keywords)
        else:
            keywords.append(base_keywords)
    
    if additional_keywords:
        if isinstance(additional_keywords, list):
            keywords.extend(additional_keywords)
        else:
            keywords.append(additional_keywords)
    
    # Remover duplicatas e limitar a 10 palavras-chave
    unique_keywords = list(dict.fromkeys(keywords))[:10]
    return ', '.join(unique_keywords)