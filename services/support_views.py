"""
Views para o sistema de suporte
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from .models import (
    SupportTicket, SupportMessage, SupportAgent, 
    SupportKnowledgeBase, UserProfile, Notification
)
from django.contrib.auth.models import User


def is_support_agent(user):
    """Verifica se o usuário é um agente de suporte"""
    try:
        return user.userprofile.user_type == 'support' or user.is_staff
    except:
        return user.is_staff


# ============================================================================
# VIEWS DO CLIENTE
# ============================================================================

@login_required
def customer_support_dashboard(request):
    """Dashboard de suporte para clientes"""
    tickets = SupportTicket.objects.filter(customer=request.user).order_by('-created_at')
    
    # Estatísticas
    stats = {
        'total': tickets.count(),
        'open': tickets.filter(status__in=['open', 'in_progress', 'waiting_customer', 'waiting_support']).count(),
        'resolved': tickets.filter(status='resolved').count(),
        'closed': tickets.filter(status='closed').count(),
    }
    
    # Paginação
    paginator = Paginator(tickets, 10)
    page = request.GET.get('page')
    tickets_page = paginator.get_page(page)
    
    context = {
        'tickets': tickets_page,
        'stats': stats,
    }
    return render(request, 'services/support/customer_dashboard.html', context)


@login_required
def create_support_ticket(request):
    """Criar novo ticket de suporte"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        category = request.POST.get('category')
        priority = request.POST.get('priority', 'medium')
        attachment = request.FILES.get('attachment')
        
        # Criar ticket
        ticket = SupportTicket.objects.create(
            customer=request.user,
            subject=subject,
            description=description,
            category=category,
            priority=priority,
            attachment=attachment,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Criar mensagem inicial
        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message_type='message',
            content=description
        )
        
        # Notificar agentes disponíveis
        available_agents = SupportAgent.objects.filter(
            is_active=True,
            is_available=True
        )
        for agent in available_agents:
            if agent.can_accept_tickets:
                Notification.objects.create(
                    user=agent.user,
                    notification_type='system',
                    title='Novo Ticket de Suporte',
                    message=f'Novo ticket #{ticket.ticket_number}: {subject}',
                    related_object_id=ticket.id,
                    related_object_type='support_ticket'
                )
        
        messages.success(request, f'Ticket #{ticket.ticket_number} criado com sucesso!')
        return redirect('support_ticket_detail', ticket_id=ticket.id)
    
    context = {
        'categories': SupportTicket.CATEGORY_CHOICES,
        'priorities': SupportTicket.PRIORITY_CHOICES,
    }
    return render(request, 'services/support/create_ticket.html', context)


@login_required
def support_ticket_detail(request, ticket_id):
    """Detalhes de um ticket de suporte"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    # Verificar permissão
    if ticket.customer != request.user and not is_support_agent(request.user):
        return HttpResponseForbidden("Você não tem permissão para ver este ticket.")
    
    # Marcar mensagens como lidas
    if request.user != ticket.customer:
        # Agente de suporte lendo
        ticket.messages.filter(sender=ticket.customer, is_read=False).update(is_read=True)
    else:
        # Cliente lendo
        ticket.messages.exclude(sender=ticket.customer).filter(is_read=False).update(is_read=True)
    
    # Processar nova mensagem
    if request.method == 'POST':
        content = request.POST.get('content')
        attachment = request.FILES.get('attachment')
        
        if content:
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message_type='message',
                content=content,
                attachment=attachment
            )
            messages.success(request, 'Mensagem enviada!')
            return redirect('support_ticket_detail', ticket_id=ticket.id)
    
    context = {
        'ticket': ticket,
        'messages': ticket.messages.filter(message_type__in=['message', 'system']).order_by('created_at'),
        'is_agent': is_support_agent(request.user),
    }
    return render(request, 'services/support/ticket_detail.html', context)


@login_required
def rate_support_ticket(request, ticket_id):
    """Avaliar atendimento do ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, customer=request.user)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        feedback = request.POST.get('feedback', '')
        
        ticket.customer_rating = rating
        ticket.customer_feedback = feedback
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()
        
        # Atualizar estatísticas do agente
        if ticket.assigned_to and hasattr(ticket.assigned_to, 'support_agent_profile'):
            ticket.assigned_to.support_agent_profile.update_statistics()
        
        messages.success(request, 'Obrigado pela sua avaliação!')
        return redirect('customer_support_dashboard')
    
    return render(request, 'services/support/rate_ticket.html', {'ticket': ticket})


# ============================================================================
# VIEWS DO AGENTE DE SUPORTE
# ============================================================================

@login_required
def agent_support_dashboard(request):
    """Dashboard para agentes de suporte"""
    if not is_support_agent(request.user):
        return HttpResponseForbidden("Acesso negado. Apenas agentes de suporte.")
    
    # Tickets do agente
    my_tickets = SupportTicket.objects.filter(assigned_to=request.user)
    
    # Tickets não atribuídos
    unassigned_tickets = SupportTicket.objects.filter(
        assigned_to__isnull=True,
        status='open'
    ).order_by('-priority', '-created_at')
    
    # Estatísticas
    stats = {
        'my_open': my_tickets.filter(status__in=['open', 'in_progress', 'waiting_customer', 'waiting_support']).count(),
        'my_total': my_tickets.count(),
        'unassigned': unassigned_tickets.count(),
        'waiting_response': my_tickets.filter(status='waiting_support').count(),
    }
    
    # Tickets recentes
    recent_tickets = my_tickets.order_by('-updated_at')[:10]
    
    context = {
        'stats': stats,
        'recent_tickets': recent_tickets,
        'unassigned_tickets': unassigned_tickets[:5],
        'is_agent': True,
    }
    return render(request, 'services/support/agent_dashboard.html', context)


@login_required
def agent_ticket_list(request):
    """Lista de tickets para agentes"""
    if not is_support_agent(request.user):
        return HttpResponseForbidden("Acesso negado.")
    
    # Filtros
    status_filter = request.GET.get('status', 'all')
    assigned_filter = request.GET.get('assigned', 'all')
    priority_filter = request.GET.get('priority', 'all')
    search = request.GET.get('search', '')
    
    # Query base
    tickets = SupportTicket.objects.all()
    
    # Aplicar filtros
    if status_filter != 'all':
        tickets = tickets.filter(status=status_filter)
    
    if assigned_filter == 'me':
        tickets = tickets.filter(assigned_to=request.user)
    elif assigned_filter == 'unassigned':
        tickets = tickets.filter(assigned_to__isnull=True)
    
    if priority_filter != 'all':
        tickets = tickets.filter(priority=priority_filter)
    
    if search:
        tickets = tickets.filter(
            Q(ticket_number__icontains=search) |
            Q(subject__icontains=search) |
            Q(description__icontains=search) |
            Q(customer__username__icontains=search) |
            Q(customer__email__icontains=search)
        )
    
    tickets = tickets.order_by('-created_at')
    
    # Paginação
    paginator = Paginator(tickets, 20)
    page = request.GET.get('page')
    tickets_page = paginator.get_page(page)
    
    context = {
        'tickets': tickets_page,
        'status_filter': status_filter,
        'assigned_filter': assigned_filter,
        'priority_filter': priority_filter,
        'search': search,
        'is_agent': True,
    }
    return render(request, 'services/support/agent_ticket_list.html', context)


@login_required
def assign_ticket(request, ticket_id):
    """Atribuir ticket a um agente"""
    if not is_support_agent(request.user):
        return HttpResponseForbidden("Acesso negado.")
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign_to_me':
            ticket.assign_to_agent(request.user)
            messages.success(request, f'Ticket #{ticket.ticket_number} atribuído a você!')
        elif action == 'unassign':
            ticket.assigned_to = None
            ticket.status = 'open'
            ticket.save()
            messages.success(request, f'Ticket #{ticket.ticket_number} desatribuído!')
        
        return redirect('support_ticket_detail', ticket_id=ticket.id)
    
    return redirect('agent_support_dashboard')


@login_required
def update_ticket_status(request, ticket_id):
    """Atualizar status do ticket"""
    if not is_support_agent(request.user):
        return HttpResponseForbidden("Acesso negado.")
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in dict(SupportTicket.STATUS_CHOICES):
            ticket.status = new_status
            ticket.save()
            
            # Criar mensagem do sistema
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message_type='system',
                content=f'Status alterado para: {ticket.get_status_display()}'
            )
            
            messages.success(request, 'Status atualizado!')
        
        return redirect('support_ticket_detail', ticket_id=ticket.id)
    
    return redirect('agent_support_dashboard')


@login_required
def agent_statistics(request):
    """Estatísticas do agente de suporte"""
    if not is_support_agent(request.user):
        return HttpResponseForbidden("Acesso negado.")
    
    try:
        agent_profile = request.user.support_agent_profile
    except:
        # Criar perfil se não existir
        agent_profile = SupportAgent.objects.create(user=request.user)
    
    # Atualizar estatísticas
    agent_profile.update_statistics()
    
    # Tickets por status
    tickets_by_status = SupportTicket.objects.filter(assigned_to=request.user).values('status').annotate(
        count=Count('id')
    )
    
    # Tickets por categoria
    tickets_by_category = SupportTicket.objects.filter(assigned_to=request.user).values('category').annotate(
        count=Count('id')
    )
    
    context = {
        'agent_profile': agent_profile,
        'tickets_by_status': tickets_by_status,
        'tickets_by_category': tickets_by_category,
        'is_agent': True,
    }
    return render(request, 'services/support/agent_statistics.html', context)


# ============================================================================
# BASE DE CONHECIMENTO
# ============================================================================

def knowledge_base_list(request):
    """Lista de artigos da base de conhecimento"""
    category = request.GET.get('category', 'all')
    search = request.GET.get('search', '')
    
    articles = SupportKnowledgeBase.objects.filter(is_published=True)
    
    if category != 'all':
        articles = articles.filter(category=category)
    
    if search:
        articles = articles.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(keywords__icontains=search)
        )
    
    articles = articles.order_by('-view_count', '-created_at')
    
    # Paginação
    paginator = Paginator(articles, 12)
    page = request.GET.get('page')
    articles_page = paginator.get_page(page)
    
    context = {
        'articles': articles_page,
        'category': category,
        'search': search,
        'categories': SupportKnowledgeBase.CATEGORY_CHOICES,
    }
    return render(request, 'services/support/knowledge_base_list.html', context)


def knowledge_base_article(request, slug):
    """Detalhes de um artigo da base de conhecimento"""
    article = get_object_or_404(SupportKnowledgeBase, slug=slug, is_published=True)
    
    # Incrementar visualizações
    article.view_count += 1
    article.save(update_fields=['view_count'])
    
    # Artigos relacionados
    related_articles = SupportKnowledgeBase.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'services/support/knowledge_base_article.html', context)


@login_required
def rate_article(request, slug):
    """Avaliar utilidade de um artigo"""
    if request.method == 'POST':
        article = get_object_or_404(SupportKnowledgeBase, slug=slug)
        helpful = request.POST.get('helpful') == 'yes'
        
        if helpful:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1
        
        article.save()
        
        return JsonResponse({'success': True, 'ratio': article.helpfulness_ratio})
    
    return JsonResponse({'success': False})


# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required
def get_unread_messages_count(request):
    """Retorna contagem de mensagens não lidas"""
    if is_support_agent(request.user):
        # Agente: contar mensagens de clientes não lidas
        count = SupportMessage.objects.filter(
            ticket__assigned_to=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
    else:
        # Cliente: contar mensagens de suporte não lidas
        count = SupportMessage.objects.filter(
            ticket__customer=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
    
    return JsonResponse({'count': count})
