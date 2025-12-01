from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

# Helper function for default duration
def get_default_duration():
    return timedelta(hours=1)

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('repair', 'Reparo'),
        ('assembly', 'Montagem'),
        ('plumbing', 'Encanamento'),
        ('electrical', 'Elétrica'),
        ('cleaning', 'Limpeza'),
        ('painting', 'Pintura'),
        ('carpentry', 'Marcenaria'),
        ('gardening', 'Jardinagem'),
        ('pest_control', 'Controle de Pragas'),
        ('air_conditioning', 'Ar Condicionado'),
        ('locksmith', 'Chaveiro'),
        ('moving', 'Mudanças'),
        ('other', 'Outros'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.DurationField(help_text="Tempo estimado para concluir o serviço", default=get_default_duration)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Cliente'),
        ('professional', 'Profissional'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    number = models.CharField(max_length=10, blank=True)
    complement = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.IntegerField(default=0)
    # Geolocation fields
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # Profile picture field
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    promotional_emails = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    # Preferences
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='pt-br')
    timezone = models.CharField(max_length=50, default='America/Sao_Paulo')
    
    # Professional-specific fields
    bio = models.TextField(blank=True, help_text="Biografia do profissional")
    experience_years = models.IntegerField(default=0, help_text="Anos de experiência")
    specialties = models.TextField(blank=True, help_text="Especialidades (separadas por vírgula)")
    certifications = models.TextField(blank=True, help_text="Certificações e qualificações")
    portfolio_url = models.URLField(blank=True, help_text="Link do portfólio")
    linkedin_url = models.URLField(blank=True, help_text="Perfil do LinkedIn")
    website_url = models.URLField(blank=True, help_text="Website pessoal")
    
    # Business information
    business_name = models.CharField(max_length=200, blank=True, help_text="Nome da empresa/negócio")
    cnpj = models.CharField(max_length=18, blank=True, help_text="CNPJ (se aplicável)")
    business_hours = models.TextField(blank=True, help_text="Horário de funcionamento")
    service_radius = models.IntegerField(default=10, help_text="Raio de atendimento em km")
    
    # Professional status
    is_verified = models.BooleanField(default=False, help_text="Profissional verificado")
    is_premium = models.BooleanField(default=False, help_text="Conta premium")
    is_available = models.BooleanField(default=True, help_text="Disponível para novos trabalhos")
    
    # Statistics
    total_jobs = models.IntegerField(default=0)
    completed_jobs = models.IntegerField(default=0)
    response_time_hours = models.IntegerField(default=24, help_text="Tempo médio de resposta em horas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    @property
    def completion_rate(self):
        """Calcula a taxa de conclusão de trabalhos"""
        if self.total_jobs > 0:
            return round((self.completed_jobs / self.total_jobs) * 100, 1)
        return 0
    
    @property
    def specialties_list(self):
        """Retorna lista de especialidades"""
        if self.specialties:
            return [s.strip() for s in self.specialties.split(',') if s.strip()]
        return []

class PortfolioItem(models.Model):
    """Modelo para itens do portfólio do profissional"""
    professional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200, help_text="Título do trabalho")
    description = models.TextField(help_text="Descrição do trabalho realizado")
    category = models.CharField(max_length=50, choices=Service.CATEGORY_CHOICES)
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    completion_date = models.DateField(help_text="Data de conclusão")
    client_name = models.CharField(max_length=100, blank=True, help_text="Nome do cliente (opcional)")
    project_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Destacar no perfil")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completion_date', '-created_at']
    
    def __str__(self):
        return f"{self.professional.username} - {self.title}"

class ProfessionalAvailability(models.Model):
    """Modelo para disponibilidade do profissional"""
    WEEKDAY_CHOICES = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    professional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['professional', 'weekday']
        ordering = ['weekday', 'start_time']
    
    def __str__(self):
        return f"{self.professional.username} - {self.get_weekday_display()}: {self.start_time}-{self.end_time}"

class PaymentMethod(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('bank_transfer', 'Transferência Bancária'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    card_number_last4 = models.CharField(max_length=4, blank=True)
    cardholder_name = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_type}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    professional = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateTimeField()
    address = models.TextField()
    notes = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Service details for custom services
    service_name = models.CharField(max_length=200, blank=True, help_text="Nome do serviço solicitado")
    service_description = models.TextField(blank=True, help_text="Descrição detalhada do serviço")
    service_category = models.CharField(max_length=50, blank=True, help_text="Categoria do serviço")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.service:
            return f"Pedido {self.id} - {self.service.name} para {self.customer.username}"
        elif self.professional:
            return f"Pedido {self.id} - Serviço Personalizado para {self.customer.username}"
        else:
            return f"Pedido {self.id} para {self.customer.username}"

class Sponsor(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='sponsors/', blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.name)

class CustomService(models.Model):
    CATEGORY_CHOICES = [
        ('repair', 'Reparo'),
        ('assembly', 'Montagem'),
        ('plumbing', 'Encanamento'),
        ('electrical', 'Elétrica'),
        ('cleaning', 'Limpeza'),
        ('painting', 'Pintura'),
        ('carpentry', 'Marcenaria'),
        ('gardening', 'Jardinagem'),
        ('pest_control', 'Controle de Pragas'),
        ('air_conditioning', 'Ar Condicionado'),
        ('locksmith', 'Chaveiro'),
        ('moving', 'Mudanças'),
        ('other', 'Outros'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço estimado do serviço")
    estimated_duration = models.DurationField(help_text="Tempo estimado para concluir o serviço", default=get_default_duration)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_services')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.provider.username}"
    
    @property
    def provider_rating(self):
        # For now, we'll return a fixed rating
        # In a real application, this would calculate the provider's average rating
        return 4.5
    
    @property
    def provider_rating_count(self):
        # For now, we'll return a fixed count
        # In a real application, this would count the number of reviews
        return 12


# Chat models
class Chat(models.Model):
    """Chat room between a customer and a professional"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_customer')
    professional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_professional')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chat between {self.customer.username} and {self.professional.username}"

class Message(models.Model):
    """Individual messages in a chat"""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('location', 'Location'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_ai_message = models.BooleanField(default=False)
    
    # For image messages
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    
    # For location messages
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        if self.is_ai_message:
            return f"AI Message: {self.content} at {self.timestamp}"
        elif self.sender:
            return f"Message from {self.sender.username} at {self.timestamp}"
        else:
            return f"System Message: {self.content} at {self.timestamp}"


class Review(models.Model):
    """Customer reviews for completed services"""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    professional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('order', 'customer')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.customer.username} for {self.professional.username} - {self.rating} stars"
    
    @property
    def rating_display(self):
        """Returns the display text for the rating"""
        return dict(self.RATING_CHOICES).get(self.rating, f"{self.rating} stars")


class ProfileChange(models.Model):
    """Track changes made to user profiles"""
    CHANGE_TYPES = [
        ('update', 'Update'),
        ('create', 'Create'),
        ('delete', 'Delete'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text='User whose profile was changed')
    field_name = models.CharField(max_length=100, help_text='Name of the field that was changed')
    old_value = models.TextField(blank=True, help_text='Previous value of the field')
    new_value = models.TextField(blank=True, help_text='New value of the field')
    change_type = models.CharField(max_length=10, choices=CHANGE_TYPES)
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text='IP address of the user who made the change')
    user_agent = models.TextField(blank=True, help_text='User agent of the browser used to make the change')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Profile Change'
        verbose_name_plural = 'Profile Changes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.field_name} - {self.change_type} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ServiceRequest(models.Model):
    """Model for service requests made by customers"""
    STATUS_CHOICES = [
        ('pending', 'Em análise'),
        ('accepted', 'Aceita'),
        ('rejected', 'Recusada'),
        ('in_progress', 'Em andamento'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_requests', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    custom_service = models.ForeignKey(CustomService, on_delete=models.CASCADE, null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CustomService.CATEGORY_CHOICES)
    scheduled_date = models.DateTimeField()
    
    address = models.TextField()
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Service Request #{self.id} - {self.title} by {self.customer.username}"
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = [
        ('service_request', 'Solicitação de Serviço'),
        ('service_accepted', 'Serviço Aceito'),
        ('service_rejected', 'Serviço Recusado'),
        ('message', 'Mensagem'),
        ('system', 'Sistema'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"



class Achievement(models.Model):
    """Model for user achievements/badges"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    points = models.PositiveIntegerField(default=10)
    category = models.CharField(max_length=50, choices=[
        ('service', 'Serviços'),
        ('community', 'Comunidade'),
        ('engagement', 'Engajamento'),
        ('milestone', 'Marco'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Model for tracking user achievements"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    target = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('user', 'achievement')
        verbose_name = 'User Achievement'
        verbose_name_plural = 'User Achievements'
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
    
    @property
    def is_earned(self):
        return self.progress >= self.target
    
    @property
    def percentage_complete(self):
        return min(100, round((self.progress / self.target) * 100)) if self.target > 0 else 0

class ServiceRequestModal(models.Model):
    """Modelo para solicitações de serviço via modal"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('contacted', 'Contatado'),
        ('scheduled', 'Agendado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Dados do usuário
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modal_service_requests')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_service_requests', null=True, blank=True)
    
    # Dados do serviço
    service = models.ForeignKey('CustomService', on_delete=models.SET_NULL, null=True, blank=True)
    service_name = models.CharField(max_length=200)
    service_description = models.TextField()
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Dados de contato
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    contact_cpf = models.CharField(max_length=14, blank=True)
    
    # Dados de endereço
    address_cep = models.CharField(max_length=9, blank=True)
    address_street = models.CharField(max_length=200, blank=True)
    address_number = models.CharField(max_length=10, blank=True)
    address_complement = models.CharField(max_length=100, blank=True)
    address_neighborhood = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_state = models.CharField(max_length=2, blank=True)
    
    # Dados de agendamento
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    preferred_period = models.CharField(max_length=20, blank=True, choices=[
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('flexivel', 'Flexível'),
    ])
    schedule_notes = models.TextField(blank=True)
    
    # Dados de pagamento
    payment_method = models.CharField(max_length=20, blank=True, choices=[
        ('dinheiro', 'Dinheiro'),
        ('cartao', 'Cartão'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência'),
    ])
    payment_notes = models.TextField(blank=True)
    
    # Detalhes específicos de pagamento
    card_type = models.CharField(max_length=20, blank=True, choices=[
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
        ('ambos', 'Ambos'),
    ])
    card_installments = models.IntegerField(default=1, blank=True)
    needs_change = models.BooleanField(default=False)
    client_money_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pix_identifier = models.CharField(max_length=50, blank=True)
    
    # Observações gerais
    notes = models.TextField(blank=True)
    
    # Status e datas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dados adicionais
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Notificações
    client_notified = models.BooleanField(default=False)
    provider_notified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Solicitação de Serviço (Modal)'
        verbose_name_plural = 'Solicitações de Serviço (Modal)'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['provider', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f'{self.contact_name} - {self.service_name} ({self.get_status_display()})'
    
    @property
    def is_pending(self):
        return self.status == 'pending'


class ServiceRequestSession(models.Model):
    """Modelo para gerenciar sessões do fluxo multi-etapa de solicitação"""
    session_key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    service_id = models.IntegerField()
    current_step = models.IntegerField(default=1)
    
    # Dados de cada etapa armazenados como JSON
    step1_data = models.JSONField(null=True, blank=True)  # Dados básicos
    step2_data = models.JSONField(null=True, blank=True)  # Agendamento
    step3_data = models.JSONField(null=True, blank=True)  # Pagamento
    
    # Controle de tempo
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sessão de Solicitação'
        verbose_name_plural = 'Sessões de Solicitação'
    
    def __str__(self):
        return f'Sessão {self.session_key} - Etapa {self.current_step}'
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at



class ContactMessage(models.Model):
    """Modelo para mensagens de contato enviadas pelo formulário"""
    STATUS_CHOICES = [
        ('new', 'Nova'),
        ('read', 'Lida'),
        ('replied', 'Respondida'),
        ('archived', 'Arquivada'),
    ]
    
    SUBJECT_CHOICES = [
        ('duvida', 'Dúvida'),
        ('suporte', 'Suporte Técnico'),
        ('sugestao', 'Sugestão'),
        ('reclamacao', 'Reclamação'),
        ('outro', 'Outro'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nome')
    email = models.EmailField(verbose_name='E-mail')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name='Assunto')
    message = models.TextField(verbose_name='Mensagem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Envio')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    admin_notes = models.TextField(blank=True, verbose_name='Notas do Administrador')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mensagem de Contato'
        verbose_name_plural = 'Mensagens de Contato'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f'{self.name} - {self.get_subject_display()} ({self.created_at.strftime("%d/%m/%Y %H:%M")})'
    
    def mark_as_read(self):
        """Marca a mensagem como lida"""
        if self.status == 'new':
            self.status = 'read'
            self.save()
    
    def mark_as_replied(self):
        """Marca a mensagem como respondida"""
        self.status = 'replied'
        self.save()


class APIMetric(models.Model):
    """
    Model for tracking API performance metrics.
    
    Records response times, status codes, and other metrics for each API request
    to enable performance monitoring and analytics.
    """
    endpoint = models.CharField(
        max_length=200,
        db_index=True,
        help_text="API endpoint path"
    )
    method = models.CharField(
        max_length=10,
        help_text="HTTP method (GET, POST, etc.)"
    )
    response_time = models.FloatField(
        help_text="Response time in milliseconds"
    )
    status_code = models.IntegerField(
        db_index=True,
        help_text="HTTP status code"
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who made the request"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the request was made"
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the client"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'API Metric'
        verbose_name_plural = 'API Metrics'
        indexes = [
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-response_time']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.response_time}ms)"
    
    @property
    def is_error(self):
        """Check if this request resulted in an error"""
        return self.status_code >= 400
    
    @property
    def is_slow(self, threshold=1000):
        """Check if this request was slow (default: > 1 second)"""
        return self.response_time > threshold
    
    @classmethod
    def cleanup_old_records(cls, days=30):
        """
        Delete records older than specified days.
        
        Args:
            days: Number of days to keep records (default: 30)
            
        Returns:
            int: Number of records deleted
        """
        from django.utils import timezone
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = cls.objects.filter(timestamp__lt=cutoff_date).delete()
        return deleted_count
    
    @classmethod
    def get_performance_stats(cls, hours=24):
        """
        Get performance statistics for the specified time window.
        
        Args:
            hours: Time window in hours
            
        Returns:
            dict: Performance statistics including avg, p95, p99, error rate
        """
        from django.utils import timezone
        from django.db.models import Avg, Count, Q
        import statistics
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        metrics = cls.objects.filter(timestamp__gte=cutoff_time)
        
        if not metrics.exists():
            return {
                'total_requests': 0,
                'avg_response_time': 0,
                'p95_response_time': 0,
                'p99_response_time': 0,
                'error_rate': 0,
                'requests_per_minute': 0
            }
        
        # Get response times for percentile calculations
        response_times = list(metrics.values_list('response_time', flat=True))
        response_times.sort()
        
        # Calculate percentiles
        p95_index = int(len(response_times) * 0.95)
        p99_index = int(len(response_times) * 0.99)
        
        total_requests = metrics.count()
        error_count = metrics.filter(status_code__gte=400).count()
        
        return {
            'total_requests': total_requests,
            'avg_response_time': round(sum(response_times) / len(response_times), 2),
            'p95_response_time': round(response_times[p95_index] if p95_index < len(response_times) else response_times[-1], 2),
            'p99_response_time': round(response_times[p99_index] if p99_index < len(response_times) else response_times[-1], 2),
            'error_rate': round((error_count / total_requests) * 100, 2) if total_requests > 0 else 0,
            'requests_per_minute': round(total_requests / (hours * 60), 2)
        }
    
    @classmethod
    def get_slowest_endpoints(cls, limit=10, hours=24):
        """
        Get the slowest endpoints by average response time.
        
        Args:
            limit: Number of endpoints to return
            hours: Time window in hours
            
        Returns:
            QuerySet: Slowest endpoints with statistics
        """
        from django.utils import timezone
        from django.db.models import Avg, Count, Max
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return (cls.objects
                .filter(timestamp__gte=cutoff_time)
                .values('endpoint', 'method')
                .annotate(
                    avg_response_time=Avg('response_time'),
                    max_response_time=Max('response_time'),
                    request_count=Count('id')
                )
                .order_by('-avg_response_time')[:limit])
    
    @classmethod
    def get_error_stats(cls, hours=24):
        """
        Get error statistics by endpoint and status code.
        
        Args:
            hours: Time window in hours
            
        Returns:
            QuerySet: Error statistics
        """
        from django.utils import timezone
        from django.db.models import Count
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return (cls.objects
                .filter(timestamp__gte=cutoff_time, status_code__gte=400)
                .values('endpoint', 'status_code')
                .annotate(error_count=Count('id'))
                .order_by('-error_count'))
    
    @classmethod
    def get_endpoint_stats(cls, hours=24):
        """
        Get comprehensive statistics for all endpoints.
        
        Args:
            hours: Time window in hours
            
        Returns:
            QuerySet: Endpoint statistics
        """
        from django.utils import timezone
        from django.db.models import Avg, Count, Max, Min, Q
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return (cls.objects
                .filter(timestamp__gte=cutoff_time)
                .values('endpoint', 'method')
                .annotate(
                    total_requests=Count('id'),
                    avg_response_time=Avg('response_time'),
                    min_response_time=Min('response_time'),
                    max_response_time=Max('response_time'),
                    error_count=Count('id', filter=Q(status_code__gte=400)),
                    success_count=Count('id', filter=Q(status_code__lt=400))
                )
                .order_by('-total_requests'))


class RateLimitRecord(models.Model):
    """
    Model for tracking rate limit usage.
    
    Stores historical data about rate limit hits for monitoring and analytics.
    Old records are automatically cleaned up to prevent database bloat.
    """
    identifier = models.CharField(
        max_length=100, 
        db_index=True,
        help_text="User ID or IP address"
    )
    endpoint = models.CharField(
        max_length=200,
        help_text="API endpoint path"
    )
    request_count = models.IntegerField(
        default=0,
        help_text="Number of requests in this window"
    )
    limit = models.IntegerField(
        help_text="Rate limit for this identifier"
    )
    window_start = models.DateTimeField(
        db_index=True,
        help_text="Start of the rate limit window"
    )
    window_end = models.DateTimeField(
        help_text="End of the rate limit window"
    )
    exceeded = models.BooleanField(
        default=False,
        help_text="Whether the limit was exceeded"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rate Limit Record'
        verbose_name_plural = 'Rate Limit Records'
        indexes = [
            models.Index(fields=['identifier', 'endpoint', 'window_start']),
            models.Index(fields=['exceeded', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        # Ensure unique records per identifier, endpoint, and window
        unique_together = ('identifier', 'endpoint', 'window_start')
    
    def __str__(self):
        status = "EXCEEDED" if self.exceeded else "OK"
        return f"{self.identifier} - {self.endpoint} - {status} ({self.request_count}/{self.limit})"
    
    @classmethod
    def cleanup_old_records(cls, days=7):
        """
        Delete records older than specified days.
        
        Args:
            days: Number of days to keep records (default: 7)
            
        Returns:
            int: Number of records deleted
        """
        from django.utils import timezone
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = cls.objects.filter(created_at__lt=cutoff_date).delete()
        return deleted_count
    
    @classmethod
    def get_top_offenders(cls, limit=10, hours=24):
        """
        Get identifiers with most rate limit violations.
        
        Args:
            limit: Number of top offenders to return
            hours: Time window in hours
            
        Returns:
            QuerySet: Top offenders with violation counts
        """
        from django.utils import timezone
        from django.db.models import Count
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return (cls.objects
                .filter(exceeded=True, created_at__gte=cutoff_time)
                .values('identifier')
                .annotate(violation_count=Count('id'))
                .order_by('-violation_count')[:limit])
    
    @classmethod
    def get_endpoint_stats(cls, hours=24):
        """
        Get rate limit statistics by endpoint.
        
        Args:
            hours: Time window in hours
            
        Returns:
            QuerySet: Endpoint statistics
        """
        from django.utils import timezone
        from django.db.models import Count, Avg, Max
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return (cls.objects
                .filter(created_at__gte=cutoff_time)
                .values('endpoint')
                .annotate(
                    total_requests=Count('id'),
                    violations=Count('id', filter=models.Q(exceeded=True)),
                    avg_requests=Avg('request_count'),
                    max_requests=Max('request_count')
                )
                .order_by('-violations'))


class BatchOperation(models.Model):
    """
    Model for tracking batch operations.
    
    Allows processing multiple operations in a single request and tracks
    the progress and status of each batch operation.
    
    Requirements: 7.1, 7.4
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('partial', 'Parcialmente Concluído'),
    ]
    
    OPERATION_TYPE_CHOICES = [
        ('order_update', 'Atualização de Pedidos'),
        ('professional_approval', 'Aprovação de Profissionais'),
        ('service_update', 'Atualização de Serviços'),
        ('user_update', 'Atualização de Usuários'),
        ('bulk_delete', 'Exclusão em Lote'),
        ('custom', 'Operação Customizada'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='batch_operations',
        help_text="User who initiated the batch operation"
    )
    operation_type = models.CharField(
        max_length=50,
        choices=OPERATION_TYPE_CHOICES,
        help_text="Type of batch operation"
    )
    total_operations = models.IntegerField(
        help_text="Total number of operations in this batch"
    )
    completed_operations = models.IntegerField(
        default=0,
        help_text="Number of successfully completed operations"
    )
    failed_operations = models.IntegerField(
        default=0,
        help_text="Number of failed operations"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current status of the batch operation"
    )
    result_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed results for each operation in the batch"
    )
    error_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Details of any errors that occurred"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the batch operation was created"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the batch operation started processing"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the batch operation completed"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Batch Operation'
        verbose_name_plural = 'Batch Operations'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['operation_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"Batch {self.id} - {self.get_operation_type_display()} ({self.get_status_display()})"
    
    @property
    def progress_percentage(self):
        """Calculate the progress percentage of the batch operation"""
        if self.total_operations == 0:
            return 0
        processed = self.completed_operations + self.failed_operations
        return round((processed / self.total_operations) * 100, 2)
    
    @property
    def success_rate(self):
        """Calculate the success rate of completed operations"""
        processed = self.completed_operations + self.failed_operations
        if processed == 0:
            return 0
        return round((self.completed_operations / processed) * 100, 2)
    
    @property
    def is_complete(self):
        """Check if the batch operation is complete"""
        return self.status in ['completed', 'failed', 'partial']
    
    @property
    def duration_seconds(self):
        """Calculate the duration of the batch operation in seconds"""
        if not self.started_at:
            return None
        end_time = self.completed_at if self.completed_at else timezone.now()
        return (end_time - self.started_at).total_seconds()
    
    def start_processing(self):
        """Mark the batch operation as started"""
        from django.utils import timezone
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def complete_operation(self, success=True):
        """
        Increment the counter for completed or failed operations.
        
        Args:
            success: Whether the operation succeeded
        """
        if success:
            self.completed_operations += 1
        else:
            self.failed_operations += 1
        
        # Update status if all operations are processed
        processed = self.completed_operations + self.failed_operations
        if processed >= self.total_operations:
            from django.utils import timezone
            self.completed_at = timezone.now()
            
            if self.failed_operations == 0:
                self.status = 'completed'
            elif self.completed_operations == 0:
                self.status = 'failed'
            else:
                self.status = 'partial'
        
        self.save(update_fields=['completed_operations', 'failed_operations', 'status', 'completed_at'])
    
    def add_result(self, operation_index, result_data):
        """
        Add result data for a specific operation.
        
        Args:
            operation_index: Index of the operation in the batch
            result_data: Result data to store
        """
        if self.result_data is None:
            self.result_data = {}
        
        self.result_data[str(operation_index)] = result_data
        self.save(update_fields=['result_data'])
    
    def add_error(self, operation_index, error_message):
        """
        Add error details for a specific operation.
        
        Args:
            operation_index: Index of the operation in the batch
            error_message: Error message to store
        """
        if self.error_details is None:
            self.error_details = {}
        
        self.error_details[str(operation_index)] = error_message
        self.save(update_fields=['error_details'])
    
    @classmethod
    def cleanup_old_records(cls, days=90):
        """
        Delete completed batch operations older than specified days.
        
        Args:
            days: Number of days to keep records (default: 90)
            
        Returns:
            int: Number of records deleted
        """
        from django.utils import timezone
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = cls.objects.filter(
            status__in=['completed', 'failed', 'partial'],
            completed_at__lt=cutoff_date
        ).delete()
        return deleted_count
    
    @classmethod
    def get_user_stats(cls, user, days=30):
        """
        Get batch operation statistics for a user.
        
        Args:
            user: User instance
            days: Time window in days
            
        Returns:
            dict: Statistics including total, completed, failed operations
        """
        from django.utils import timezone
        from django.db.models import Sum
        
        cutoff_date = timezone.now() - timedelta(days=days)
        operations = cls.objects.filter(user=user, created_at__gte=cutoff_date)
        
        if not operations.exists():
            return {
                'total_batches': 0,
                'total_operations': 0,
                'completed_operations': 0,
                'failed_operations': 0,
                'success_rate': 0,
                'avg_batch_size': 0
            }
        
        stats = operations.aggregate(
            total_operations=Sum('total_operations'),
            completed_operations=Sum('completed_operations'),
            failed_operations=Sum('failed_operations')
        )
        
        total_processed = (stats['completed_operations'] or 0) + (stats['failed_operations'] or 0)
        success_rate = 0
        if total_processed > 0:
            success_rate = round(((stats['completed_operations'] or 0) / total_processed) * 100, 2)
        
        # Calculate average batch size manually
        total_ops = stats['total_operations'] or 0
        batch_count = operations.count()
        avg_batch_size = round(total_ops / batch_count, 2) if batch_count > 0 else 0
        
        return {
            'total_batches': batch_count,
            'total_operations': total_ops,
            'completed_operations': stats['completed_operations'] or 0,
            'failed_operations': stats['failed_operations'] or 0,
            'success_rate': success_rate,
            'avg_batch_size': avg_batch_size
        }


