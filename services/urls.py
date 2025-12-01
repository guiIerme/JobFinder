"""
Services URL Configuration

This module defines all URL patterns for the services app, including:
- Public pages (home, search, about, contact, etc.)
- User pages (profile, orders, payment methods)
- Provider pages (dashboard, service management, requests)
- Admin pages (dashboard, bulk operations, analytics)
- API endpoints (v1 with versioning support)
- WebSocket endpoints (via routing.py)

API Endpoints:
- /api/v1/ - Version 1 of the API (see services/api/urls_v1.py)
  - /api/v1/search/ - Advanced search with filters
  - /api/v1/analytics/ - Performance and error metrics
  - /api/v1/batch/ - Batch processing operations
  - /api/v1/mobile/ - Mobile-optimized endpoints
  - /api/v1/admin/ - Admin bulk operations and exports

Requirements: All (comprehensive integration)
"""
from django.urls import path, include
from . import views
from . import chat_views
from . import rate_limit_views
from .api import admin_bulk_views, admin_export_views, admin_async_views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    # Registration is now publicly accessible for both workers and clients
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.all_professionals, name='search_new'),
    path('search/ajax/', views.search_ajax, name='search_ajax'),
    path('sponsors-new/', views.sponsors_new, name='sponsors_new'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('information/', views.information, name='information'),
    path('help-support/', views.help_support, name='help_support'),
    
    # User pages
    path('profile/', views.profile_view, name='profile'),
    path('profile-new/', views.profile_new, name='profile_new'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('add-payment-method/', views.add_payment_method, name='add_payment_method'),
    path('edit-payment-method/<int:payment_method_id>/', views.edit_payment_method, name='edit_payment_method'),
    path('delete-payment-method/<int:payment_method_id>/', views.delete_payment_method, name='delete_payment_method'),
    path('sponsors/', views.sponsors_view, name='sponsors'),
    path('sponsors-new/', views.sponsors_new, name='sponsors_new'),
    path('partnership/<str:level>/', views.partnership_details, name='partnership_details'),
    path('requested-services/', views.requested_services, name='requested_services'),
    path('bulk-payment/', views.bulk_payment, name='bulk_payment'),
    path('providers/<str:service_category>/', views.providers_by_service, name='providers_by_service'),
    path('professionals/', views.all_professionals, name='all_professionals'),



    # Service requests - TODAS redirecionam para solicitar-servico-completo
    path('request-service/<int:service_id>/', views.redirect_to_solicitar_completo, name='request_service'),
    path('request-custom-service/<int:custom_service_id>/', views.redirect_to_solicitar_completo, name='request_custom_service'),
    path('schedule-service/', views.redirect_to_solicitar_completo, name='schedule_service'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-payment/<int:order_id>/', views.order_payment, name='order_payment'),

    # Página principal de solicitação de serviço
    path('solicitar-servico-completo/', views.solicitar_servico_completo, name='solicitar_servico_completo'),
    path('processar-solicitacao/', views.processar_solicitacao, name='processar_solicitacao'),
    
    # URLs antigas redirecionam para a página completa
    path('submit-service-request/', views.redirect_to_solicitar_completo, name='submit_service_request'),
    path('solicitar-servico-pagina/', views.redirect_to_solicitar_completo, name='solicitar_servico_pagina'),
    path('provider-service-requests/', views.provider_service_requests, name='provider_service_requests'),
    path('provider-service-requests-page/', views.provider_service_requests_page, name='provider_service_requests_page'),
    path('update-service-request-status/<int:request_id>/', views.update_service_request_status, name='update_service_request_status'),
    
    # Provider pages
    path('provider-dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('provider-ai-insights/', views.provider_ai_insights, name='provider_ai_insights'),
    path('provider/<int:provider_id>/', views.provider_profile, name='provider_profile'),
    path('add-custom-service/', views.add_custom_service, name='add_custom_service'),
    path('edit-custom-service/<int:service_id>/', views.edit_custom_service, name='edit_custom_service'),
    path('remove-custom-service/<int:service_id>/', views.remove_custom_service, name='remove_custom_service'),
    path('service-history-new/', views.service_history_new, name='service_history_new'),
    path('save-zip-code/', views.save_zip_code, name='save_zip_code'),
    
    # Provider features - Agendamento, Avaliações, Financeiro, Relatórios
    path('provider/agendamento/', views.provider_agendamento, name='provider_agendamento'),
    path('provider/avaliacoes/', views.provider_avaliacoes, name='provider_avaliacoes'),
    path('provider/financeiro/', views.provider_financeiro, name='provider_financeiro'),
    path('provider/relatorios/', views.provider_relatorios, name='provider_relatorios'),
    
    # Chat API endpoints
    path('api/chat/message/', chat_views.chat_message, name='chat_message'),
    path('api/chat/rating/', chat_views.chat_rating, name='chat_rating'),
    
    # Chat pages (TODO: Implement these views)
    # path('chats/', chat_views.chat_list, name='chat_list'),
    # path('chats/<int:chat_id>/', chat_views.chat_room, name='chat_room'),
    # path('chats/create/<int:order_id>/', chat_views.create_chat, name='create_chat'),
    
    # Chat Analytics Dashboard (Requirements: 7.2)
    # path('admin/chat-analytics/', include('services.chat.analytics_urls')),
    
    # Service detail page
    path('service-detail/<int:order_id>/', views.service_detail, name='service_detail'),
    
    # Request service from search
    path('request-service-from-search/<int:custom_service_id>/', views.request_service_from_search, name='request_service_from_search'),
    
    # Provider service management
    path('remove-custom-service/<int:service_id>/', views.remove_custom_service, name='remove_custom_service'),

    # Service details API
    path('api/service/<int:service_id>/', views.get_service_details, name='get_service_details'),
    
    # Service review API
    path('api/review/<int:order_id>/', views.submit_service_review, name='submit_service_review'),
    
    # AI Suggestions API
    path('api/ai-suggestions/', views.ai_suggestions, name='ai_suggestions'),
    
    # Geolocation API
    path('api/update-location/', views.update_user_location, name='update_user_location'),
    path('api/nearby-professionals/', views.get_nearby_professionals, name='get_nearby_professionals'),
    path('map/', views.map_view, name='map_view'),
    
    # Gamification
    path('achievements/', views.user_achievements, name='user_achievements'),
    
    # Admin pages
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard-new/', views.admin_dashboard_new, name='admin_dashboard_new'),
    path('admin-dashboard-new/update-request-status/', views.update_request_status, name='update_request_status'),
    path('admin-dashboard-new/update-service/', views.update_service, name='update_service'),
    path('admin-dashboard-new/customer-requests/<int:customer_id>/', views.get_customer_requests, name='get_customer_requests'),
    path('admin-dashboard-new/providers/', views.admin_providers_list, name='admin_providers_list'),
    path('admin-dashboard-new/provider/<int:provider_id>/services/', views.admin_provider_services, name='admin_provider_services'),
    path('admin-dashboard-new/settings/', views.admin_settings, name='admin_settings'),
    # Exportação de dados do admin
    path('admin-dashboard-new/exportar-atividades/', views.exportar_atividades_admin, name='exportar_atividades_admin'),
    path('admin-dashboard-new/exportar-grafico/<str:tipo_grafico>/', views.exportar_grafico_admin, name='exportar_grafico_admin'),
    path('admin-dashboard-new/exportar-relatorio-completo/', views.exportar_relatorio_completo_admin, name='exportar_relatorio_completo_admin'),
    path('admin-dashboard-new/exportar-excel-profissional/', views.exportar_excel_profissional, name='exportar_excel_profissional'),
    path('ai-dashboard/', views.ai_dashboard, name='ai_dashboard'),
    
    # Rate Limiting Dashboard
    path('admin/rate-limits/', rate_limit_views.rate_limit_dashboard, name='rate_limit_dashboard'),
    path('admin/rate-limits/stats/', rate_limit_views.rate_limit_stats_api, name='rate_limit_stats_api'),
    path('admin/rate-limits/cleanup/', rate_limit_views.rate_limit_cleanup, name='rate_limit_cleanup'),
    
    # API Deprecation Management (Requirements: 12.2, 12.3, 12.4)
    path('admin/api-deprecation/', views.api_deprecation_dashboard, name='api_deprecation_dashboard'),
    path('admin/api-deprecation/schedule/', views.schedule_deprecation_api, name='schedule_deprecation_api'),
    path('admin/api-deprecation/cancel/', views.cancel_deprecation_api, name='cancel_deprecation_api'),
    path('admin/api-deprecation/status/', views.deprecation_status_api, name='deprecation_status_api'),
    # Removed duplicate register path
    path('test-template/', views.test_template, name='test_template'),

    path('notification-demo/', views.notification_demo, name='notification_demo'),
    path('notifications/', views.notifications_view, name='notifications'),
    
    # Profile change tracking
    path('profile-changes/', views.profile_changes, name='profile_changes'),
    path('admin-profile-changes/', views.admin_profile_changes, name='admin_profile_changes'),
    
    # SEO and system files
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # Analytics
    path('analytics/', include('analytics.urls')),
    
    # Admin Bulk Operations API (Requirements: 11.1, 11.2)
    path('api/v1/admin/bulk/orders/update-status/', admin_bulk_views.BulkOrderUpdateView.as_view(), name='api_bulk_order_update'),
    path('api/v1/admin/bulk/professionals/approve/', admin_bulk_views.BulkProfessionalApprovalView.as_view(), name='api_bulk_professional_approval'),
    path('api/v1/admin/bulk/services/update/', admin_bulk_views.BulkServiceUpdateView.as_view(), name='api_bulk_service_update'),
    
    # Admin Data Export API (Requirement: 11.3)
    path('api/v1/admin/export/orders/', admin_export_views.ExportOrdersView.as_view(), name='api_export_orders'),
    path('api/v1/admin/export/users/', admin_export_views.ExportUsersView.as_view(), name='api_export_users'),
    path('api/v1/admin/export/services/', admin_export_views.ExportServicesView.as_view(), name='api_export_services'),
    
    # Admin Async Processing API (Requirements: 11.4, 11.5)
    path('api/v1/admin/async/submit/', admin_async_views.AsyncBulkOperationView.as_view(), name='api_async_bulk_submit'),
    path('api/v1/admin/async/status/<int:batch_id>/', admin_async_views.AsyncBatchStatusView.as_view(), name='api_async_batch_status'),
    path('api/v1/admin/async/cancel/<int:batch_id>/', admin_async_views.AsyncBatchCancelView.as_view(), name='api_async_batch_cancel'),
    
    # Review system URLs
    path('submit-review/<int:order_id>/', views.submit_review, name='submit_review'),
    path('professional-reviews/<int:professional_id>/', views.get_professional_reviews, name='get_professional_reviews'),
    
    # Order cancellation
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Test template not found
    path('test-template-not-found/', views.test_template_not_found, name='test_template_not_found'),
    
    # Error reporting
    path('report-error/', views.report_error, name='report_error'),
    
    # Test error pages
    path('test-404/', views.test_404_error, name='test_404'),
    path('test-403/', views.custom_403, name='test_403'),
    path('test-400/', views.custom_400, name='test_400'),
    path('test-500/', views.test_500_error, name='test_500'),
    
    # Solicitação de serviços - URLs atualizadas (redireciona para página completa)
    path('solicitar-servico/', views.solicitar_servico_completo, name='solicitar_servico'),
    path('minhas-solicitacoes/', views.minhas_solicitacoes, name='minhas_solicitacoes'),
    path('cancelar-solicitacao/<int:solicitacao_id>/', views.cancelar_solicitacao, name='cancelar_solicitacao'),
    
    # Fluxo antigo de solicitação em 4 etapas - REDIRECIONADO
    path('solicitar/<int:service_id>/', views.redirect_to_solicitar_completo, name='solicitar_servico_step1'),
    path('solicitar/etapa-1/', views.redirect_to_solicitar_completo, name='solicitar_step1_post'),
    path('solicitar/etapa-2/', views.redirect_to_solicitar_completo, name='solicitar_step2'),
    path('solicitar/etapa-3/', views.redirect_to_solicitar_completo, name='solicitar_step3'),
    path('solicitar/etapa-4/', views.redirect_to_solicitar_completo, name='solicitar_step4'),
    path('solicitar/confirmar/', views.redirect_to_solicitar_completo, name='solicitar_confirm'),
    path('acompanhar/<int:request_id>/', views.acompanhar_solicitacao, name='acompanhar_solicitacao'),
    
    # Novas URLs para visualização de solicitações
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('painel-prestador/', views.painel_prestador, name='painel_prestador'),
    path('confirmar-solicitacao/<int:request_id>/', views.confirmar_solicitacao, name='confirmar_solicitacao'),
    path('rejeitar-solicitacao/<int:request_id>/', views.rejeitar_solicitacao, name='rejeitar_solicitacao'),
    
    # APIs auxiliares para o fluxo
    path('api/validate-step/', views.validate_step_api, name='validate_step_api'),
    path('api/check-availability/', views.check_availability_api, name='check_availability_api'),
    
    # Página de teste para o fluxo de solicitação
    path('teste-solicitacao/', views.teste_solicitacao, name='teste_solicitacao'),
    
    # URLs para prestadores
    path('prestador/solicitacoes/', views.solicitacoes_prestador, name='solicitacoes_prestador'),
    path('prestador/alterar-status-solicitacao/<int:solicitacao_id>/', views.alterar_status_solicitacao, name='alterar_status_solicitacao'),
    path('prestador/dashboard-solicitacoes/', views.dashboard_prestador_solicitacoes, name='dashboard_prestador_solicitacoes'),
    
    # Chat AI API
    path('api/chat-ai/', views.chat_ai_response, name='chat_ai_response'),
    path('api/chat/message/', chat_views.chat_message, name='chat_message'),
    path('api/chat/rating/', chat_views.chat_rating, name='chat_rating'),
    
    # ============================================================================
    # API v1 - RESTful API Endpoints
    # ============================================================================
    # All API v1 endpoints are namespaced under /api/v1/
    # This includes:
    # - Search API (Requirements: 3.1-3.5)
    # - Analytics API (Requirements: 6.1-6.5)
    # - Batch Processing API (Requirements: 7.1-7.5)
    # - Mobile API (Requirements: 10.1-10.5)
    # - Admin Bulk Operations (Requirements: 11.1-11.5)
    # - API Versioning (Requirements: 12.1-12.5)
    path('api/v1/', include('services.api.urls_v1', namespace='api_v1')),
]