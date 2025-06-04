# myapp/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator

from django.conf import settings

import datetime


import uuid


class Setor(models.Model):
    name = models.TextField(max_length=255,null=False, blank=False)
    description = models.TextField(max_length=500, null=True, default=None)
    estimated_consumption = models.FloatField(null=False, blank=False)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    def __str__(self):
        return self.name
    

class Section(models.Model):
    name = models.TextField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=255, null=True, blank=False)
    real_consumption = models.FloatField(null=False, blank=False, default=0)

    is_monitored = models.BooleanField(default=False)

    monitoring = models.ForeignKey(
        "Monitoring",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    setor = models.ForeignKey(
        "Setor",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    productionLine = models.ForeignKey(
        "ProductionLine",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    # Correção: Apenas um equipamento por seção
    equipament = models.ForeignKey(
        "Equipament",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="sections"
    )

    device_iots = models.ManyToManyField(
        "DeviceIot",
        blank=True,
        null=True,
        related_name="sections"
    )

    type_section = models.ForeignKey(
        "TypeSection",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
    )

    secticon_parent = models.ForeignKey(
        "Section",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    def __str__(self):
        return self.name

class ParametersMinitoring(models.Model):
    id = models.AutoField(primary_key=True) 
    name = models.TextField(max_length=255,null=True, blank=True)
    max_temperature = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0)])
    min_temperature = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0)])
    max_humidity = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0)])
    min_humidity = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0)])
    max_luminosity = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0)])
    min_luminosity = models.FloatField(null=False, blank=False, validators=[MinValueValidator(0)])

    section = models.ForeignKey(
        "Section",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
class SectionHistoryMensurement(models.Model): 

    # Device Information Fields
    tenantId = models.UUIDField(null=True, default=None)
    tenantName = models.CharField(max_length=100, null=True, default=None)
    applicationId = models.UUIDField(null=True, default=None)
    applicationName = models.CharField(max_length=100, null=True, default=None)
    deviceProfileId = models.UUIDField(null=True, default=None)
    deviceProfileName = models.CharField(max_length=100, null=True, default=None)
    deviceName = models.CharField(max_length=100, null=True)
    devEui = models.CharField(max_length=16, unique=False, null=True)
    deviceClassEnabled = models.CharField(max_length=10, null=True)
    tags = models.JSONField(default=dict, blank=True)
    
    # Measurement Data Fields
    #Consumo
    
    energia_ativa_kWh = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tensao_fase_A = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    tipo_medidor = models.CharField(max_length=20, null=True)
    corrente_fase_B = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    tensao_fase_B = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    corrente_fase_A = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    energia_ativa_kWh = models.FloatField(null=False, blank=False, default=0) 
    interval = models.IntegerField(null=False, blank=False, default=0)
    section = models.ForeignKey(
        "Section",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    def save(self, *args, **kwargs):
        # Primeiro salva o objeto
        super().save(*args, **kwargs)
        
        # Se houver uma section associada, atualiza o consumo real
        if self.section:
            self.update_section_consumption()

    def update_section_consumption(self):
        """Calcula e atualiza a soma total na Section relacionada"""
        total = SectionHistoryMensurement.objects.filter(
            section=self.section
        ).aggregate(
            total=Sum('energia_ativa_kWh')
        )['total'] or 0.0
        
        self.section.real_consumption = total
        self.section.save()
 

class TypeSection(models.Model):
    name = models.TextField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(null=False, auto_now_add=True)

    def __str__(self):
        return self.name

class HistoricalMeasurement(models.Model):
    total_consumption = models.FloatField(null=False, blank=False)
    start_date =models.DateTimeField(null=False, auto_now_add=True)
    end_date = models.DateTimeField(null=False, auto_now_add=True)

    monitoring = models.ForeignKey(
        "Monitoring",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

class Equipament(models.Model):
    name = models.TextField(max_length=255,null=False, blank=False)
    description = models.TextField(max_length=500, null=True, default=None)
    power = models.FloatField(null=False, blank=False, default=0)
    tension = models.FloatField(null=False, blank=False, default=0)
    energy_consumption = models.FloatField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    max_consumption = models.FloatField(null=False, blank=False, default=0)
    min_consumption = models.FloatField(null=False, blank=False, default=0)

    production_line = models.ForeignKey(
        "ProductionLine",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
  

class EquipamentLine(models.Model):
    create_at = models.DateTimeField(null=False, auto_now_add=True)
    productionLine = models.ForeignKey(
        "ProductionLine",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    equipament = models.ForeignKey(
        "Equipament",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
class AssociationIot(models.Model):
    date_association = models.DateTimeField(null=False, auto_now_add=True)
    monitoring = models.ForeignKey(
        "Monitoring",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    device_iot = models.ForeignKey(
        "DeviceIot",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    section = models.ForeignKey(
        "Section",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

class Mensuration(models.Model):
    date_mensuration = models.DateTimeField(null=False, auto_now_add=True)
    value_mensuration = models.FloatField(null=False, blank=False)
    type_mensuration = models.TextField(max_length=255, null=False, blank=False)

    equipament = models.ForeignKey(
        "Equipament",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

    ProductItem = models.ForeignKey(
        "ProductItem",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

class DeviceIot(models.Model):

    class TypeDevice(models.TextChoices):
        NANSENSOR = 'Nansenson', 'Nansenson'
        NANSENIC = 'Nansenic', 'Nansenic'

    name = models.TextField(max_length=255,null=True, blank=True)
    is_available = models.BooleanField(default=False)
    type_device = models.TextField(max_length=255, choices=TypeDevice.choices, default=TypeDevice.NANSENIC)
    equipement = models.ForeignKey(
        "Equipament",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    deviceName = models.TextField(max_length=255,null=True, blank=True)
    devEui = models.TextField(max_length=255,null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.name} - ({self.devEui})"
class Product(models.Model):
    name = models.TextField(max_length=255,null=False, blank=False)
    description = models.TextField(max_length=500, null=True, default=None)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    photo = models.ImageField(upload_to='product_photos/', blank=True, default='product_photos/product-default.png')

    @property
    def photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return f"{settings.MEDIA_URL}product_photos/product-default.png"

class ProductItem(models.Model):
    name = models.TextField(max_length=255,null=False, blank=False)
    description = models.TextField(max_length=500, null=True, default=None)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    barcode = models.TextField(null=True, default=None)
    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )


class ProductionLine(models.Model):
    name = models.TextField(max_length=255,null=False, blank=False)
    description = models.TextField(max_length=500, null=True, default=None)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    value_mensuration_estimated = models.FloatField(null=False, blank=False)

    setor = models.ForeignKey(
        "Setor",        
        on_delete=models.SET_NULL,        
        null=True,        
        default=None
    )

    def __str__(self):
        return self.name

class ReportEffiency(models.Model):
    name = models.TextField(max_length=255,null=False, blank=False)
    
    consumption_total = models.FloatField(null=False, blank=False)
    production_total = models.FloatField(null=False, blank=False)
    efficiency = models.FloatField(null=False, blank=False)
    period = models.DateTimeField(null=False, auto_now_add=True)
    created_at = models.DateTimeField(null=False, auto_now_add=True)

    setor = models.ForeignKey(
        "Setor",        
        on_delete=models.SET_NULL,        
        null=True,        
        default=None
    )

# Gerenciador de usuários personalizado
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.ADMIN)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    ADMIN = 'ADMIN'
    LIDER = 'LIDER'
    GAME = 'GAME'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (LIDER, 'Lider'),
        (GAME, 'Game'),
    ]

    # Campos existentes
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=GAME)
    name = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.ImageField(
        upload_to='product_photos/',
        null=False,
        default='user_photos/user_default.png'
    )
    
    setor = models.ForeignKey(
        "Setor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    productionLine = models.ForeignKey(
        "ProductionLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Novos campos para o sistema de missões
    total_nansen_coins = models.FloatField(default=0)
    total_xp = models.FloatField(default=0)
    nivel = models.IntegerField(default=1)
    last_activity = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    @property
    def avatar(self):
        if self.avatar_url and hasattr(self.avatar_url, 'url'):
            return self.photo.url
        return f"{settings.MEDIA_URL}user_photos/user_default.png"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # Métodos para o sistema de missões
    def update_stats(self):
        """Atualiza as estatísticas baseadas nos achievements"""
        achievements = self.achievements.all()
        
        self.total_nansen_coins = achievements.aggregate(
            total=Sum('nansen_coins')
        )['total'] or 0
        
        self.total_xp = achievements.aggregate(
            total=Sum('quantity_xp')
        )['total'] or 0
        
        self.nivel = int(self.total_xp // 1000) + 1  # 1000 XP por nível
        self.save()

    @property
    def completed_missions(self):
        """Retorna queryset de missões completadas"""
        from .models import Mission  # Importe aqui para evitar circular imports
        return Mission.objects.filter(
            users_progress__user=self,
            users_progress__status='Finalizada'
        ).distinct()

    @property
    def current_missions(self):
        """Retorna missões em andamento"""
        from .models import Mission
        return Mission.objects.filter(
            users_progress__user=self,
            users_progress__status='Em Andamento'
        ).distinct()

    '''def get_mission_progress(self, mission_id):
        """Retorna o objeto MissionProgress para uma missão específica"""
        return self.missions_progress.filter(mission_id=mission_id).first()'''
    
    def get_mission_progress(self, mission_id, json_format=False):
        """Retorna o progresso em objeto ou JSON"""
        progress = self.missions_progress.filter(mission_id=mission_id).first()
        
        if not json_format:
            return progress
            
        if progress:
            return {
                'mission_id': mission_id,
                'current_progress': progress.current_progress,
                'status': progress.status,
                'last_updated': progress.updated_at.isoformat(),
                'reward': {
                    'nansen_coins': progress.mission.nansen_coins,
                    'xp': progress.mission.quantity_xp
                }
            }
        return None

# Modelo Mission com relacionamento N:N com CustomUser

class Monitoring(models.Model):
    class TypeMonitoting(models.TextChoices):
        NANSENSOR = 'Nansenson', 'Nansenson'
        NANSENIC = 'Nansenic', 'Nansenic'
    name = models.TextField(max_length=255,null=False, blank=False, default= "")
    description = models.TextField(max_length=500, null=False, blank=False) 
    estimated_consumption = models.FloatField(null=False, blank=False)
    #Esse campo pode ser null quando o tipo for nansensor
    total_consumption = models.FloatField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(null=False, auto_now_add=True)

    type_mmonitoring = models.CharField(
        max_length=15,
        choices=TypeMonitoting.choices,
        default=TypeMonitoting.NANSENSOR
    )

    is_active = models.BooleanField(default=False)
    is_active_monitoring = models.BooleanField(default=False)
    is_isolado = models.BooleanField(default=False)

    def __str__(self):
        return self.description

class Mission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pendente', 'Pendente'
        IN_PROGRESS = 'Em Andamento', 'Em Andamento'
        COMPLETED = 'Finalizada', 'Finalizada'

    
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    quantity_na = models.FloatField(default=0)
    energy_meta = models.FloatField(default=0)
    nansen_coins = models.FloatField(default=0)
    quantity_xp = models.FloatField(default=0)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    

    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    order_production = models.IntegerField(default=0)
    quantity_product= models.IntegerField(default=0)
    is_order_production = models.BooleanField(default=False)
    
    
    monitoring = models.ForeignKey(
        "Monitoring",
        on_delete=models.SET_NULL,
        null=True,
        blank=True, 
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    users = models.ManyToManyField("CustomUser", related_name="missions", null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.date_end.date() < self.date_start.date():
            raise ValidationError("Data de término não pode ser anterior à data de início")

    def update_global_status(self):
        """Atualiza o status da missão baseado nos progressos individuais"""
        progresses = self.users_progress.all()
        
        if not progresses.exists():
            self.status = self.Status.PENDING
            self.save()
            return
        
        total_users = self.users.count()
        completed = progresses.filter(status=MissionProgress.Status.COMPLETED).count()
        
        if completed == total_users:
            self.status = self.Status.COMPLETED
        elif completed > 0:
            self.status = self.Status.IN_PROGRESS
        else:
            self.status = self.Status.PENDING
            
        self.save()

class MissionProgress(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pendente', 'Pendente'
        IN_PROGRESS = 'Em Andamento', 'Em Andamento'
        COMPLETED = 'Finalizada', 'Finalizada'
        FAILED = 'Falhou', 'Falhou'  # Status exclusivo do progresso
    
    user = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        related_name='missions_progress'
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name='users_progress'
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    current_progress = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, default=None)
    ended_at = models.DateTimeField(null=True, default=None)

    class Meta:
        unique_together = ('user', 'mission')

    def __str__(self):
        return f"{self.user.username} - {self.mission.name} ({self.status})"

    def clean(self):
        if self.current_progress < 0 or self.current_progress > 100:
            raise ValidationError("Progresso deve estar entre 0 e 100%")
        
        if self.mission.date_end.date() < datetime.date.today() and self.status not in [self.Status.COMPLETED, self.Status.FAILED]:
            raise ValidationError("Missão expirada - atualize o status para Falhou")


    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Atualiza status baseado no progresso (exceto se já estiver como FAILED)
        if self.status != self.Status.FAILED:
            if self.current_progress >= 100:
                self.status = self.Status.COMPLETED
            elif self.current_progress > 0:
                self.status = self.Status.IN_PROGRESS
            else:
                self.status = self.Status.PENDING
        
        super().save(*args, **kwargs)
        
        # Atualizações pós-salvar
        if self.status == self.Status.COMPLETED:
            self.create_achievement()
        if self.status == self.Status.COMPLETED:
            self.user.update_stats()  # Atualiza estatísticas automaticamente
        self.mission.update_global_status()

    def create_achievement(self):
        """Cria um achievement quando a missão é completada"""
        Achievement.objects.create(
            user_achievement=self.user,
            mission=self.mission,
            description=f'Concluiu: {self.mission.name}',
            nansen_coins=self.mission.nansen_coins,
            quantity_xp=self.mission.quantity_xp,
            nivel=self.calculate_level()
        )
    
    def calculate_level(self):
        """Lógica personalizável para definir o nível"""
        return max(1, int(self.mission.quantity_xp / 1000))  # Exemplo: 1000 XP = nível 1

class Achievement(models.Model):
    user_achievement = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    description = models.TextField()
    nansen_coins = models.FloatField(default=0)
    quantity_xp = models.FloatField(default=0)
    nivel = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} (Nível {self.nivel})"

class Claim(models.Model):
    data_claim = models.DateTimeField(null=False, auto_now_add=True)
    description = models.TextField(max_length=255,null=False, blank=False)  
    user_claim = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    reward= models.ForeignKey(
        "Reward",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )

class Reward(models.Model):

    TIPO_REWARD_A = 'TIPO_REWARD_A'
    TIPO_REWARD_B = 'TIPO_REWARD_B'
    
    REWARD_CHOICES = [
        (TIPO_REWARD_A,'TIPO_REWARD_A'),
        (TIPO_REWARD_B, 'TIPO_REWARD_B'),
        
    ] 
    description = models.TextField(max_length=255,null=False, blank=False)
    points = models.FloatField(null=False, blank=False)
    type_reward = models.CharField(max_length=100, choices=REWARD_CHOICES)
    mission = models.ForeignKey(
        "Mission",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )


class MissionQuiz(models.Model):
    create_at = models.DateTimeField(null=False, auto_now_add=True)
    mission = models.ForeignKey(
        "Mission",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    quiz = models.ForeignKey(
        "Quiz",
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )


class Quiz(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.name

class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name="questions",

    )
    text = models.TextField(null=False, blank=False, default="")

    def __str__(self):
        return self.text

class ResponseQuiz(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="responses",
        null=True
    )
    text = models.CharField(max_length=255, null=False, blank=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correta' if self.is_correct else 'Errada'})"
    
class UserResponse(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_responses")
    question = models.ForeignKey("Question", on_delete=models.CASCADE, related_name="user_responses")
    selected_response = models.ForeignKey("ResponseQuiz", on_delete=models.CASCADE, related_name="user_responses")

    created_at = models.DateTimeField(auto_now_add=True)

    def is_correct(self):
        """Retorna se a resposta escolhida está correta."""
        return self.selected_response.is_correct

    def __str__(self):
        return f"{self.user.username} → {self.question.text} → {self.selected_response.text}"
    

    
'''
LOJA
''' 

class ProductLoja(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    quantity = models.IntegerField(default=0)

class Compra(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    data_compra = models.DateTimeField(auto_now_add=True)
    finalizada = models.BooleanField(default=True)

class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='itens', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductLoja, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def valor_total(self):
        return self.quantidade * self.preco_unitario
    
'''
Integração com HARDWARE
'''

class DeviceIotEvent(models.Model):
    id = models.AutoField(primary_key=True)  # PK explícita

    # Device Information Fields
    tenantId = models.UUIDField()
    tenantName = models.CharField(max_length=100)
    applicationId = models.UUIDField()
    applicationName = models.CharField(max_length=100)
    deviceProfileId = models.UUIDField()
    deviceProfileName = models.CharField(max_length=100)
    deviceName = models.CharField(max_length=100)
    devEui = models.CharField(max_length=16, unique=False)
    deviceClassEnabled = models.CharField(max_length=10)
    tags = models.JSONField(default=dict, blank=True)
    
    # Measurement Data Fields
    #Consumo
    
    energia_ativa_kWh = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tensao_fase_A = models.DecimalField(max_digits=6, decimal_places=2)
    tipo_medidor = models.CharField(max_length=20)
    corrente_fase_B = models.DecimalField(max_digits=6, decimal_places=2)
    tensao_fase_B = models.DecimalField(max_digits=6, decimal_places=2)
    corrente_fase_A = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_sended = models.BooleanField(default=False)
    

    class Meta:
        verbose_name = "Device Information"
        verbose_name_plural = "Devices Information"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['devEui']),
            models.Index(fields=['deviceName']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.deviceName} ({self.devEui})"
