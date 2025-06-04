# myapp/serializers.py
from rest_framework import serializers

from django.conf import settings

from .models import (
    CustomUser, 
    Setor,
    Equipament, 
    EquipamentLine,
    Product, 
    ProductItem,
    Achievement,
    Monitoring, 
    HistoricalMeasurement, 
    Section, DeviceIot, TypeSection,
    Mensuration, 
    AssociationIot, 
    Achievement, 
    Mission,
    Claim,
    Reward,
    Mission,
    Quiz, ResponseQuiz,
    MissionQuiz,
    ProductionLine,
    ProductItem,
    MissionProgress,
    MissionQuiz, ReportEffiency, Setor , Question, UserResponse,
    ProductLoja, Compra, ItemCompra,
    DeviceIotEvent, SectionHistoryMensurement, ParametersMinitoring

)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from datetime import datetime



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'password','total_xp','total_nansen_coins','nivel', 'role','avatar_url','avatar']
        extra_kwargs = {'password': {'write_only': True}}


    def get_avatar(self, obj):
            request = self.context.get('request')
            
            # Verifica se há uma foto específica ou usa a padrão
            if obj.avatar_url and not obj.avatar_url.name.endswith('user_default.png'):
                avatar = obj.avatar_url.url
            else:
                avatar = f"{settings.MEDIA_URL}user_photos/user_default.png"
            
            # Retorna URL completa se houver request, caso contrário retorna relativa
            return request.build_absolute_uri(avatar) if request else avatar
    def create(self, validated_data):
        # Remove campos específicos para evitar o erro de múltiplos valores
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Cria o usuário com os campos específicos e os demais dados adicionais
        return CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            **validated_data  # Passa os campos restantes como extra_fields
        )

class CustomUserReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'role','avatar_url', 'avatar']  # Lista apenas os campos que queremos exibir


        def get_avatar(self, obj):
            request = self.context.get('request')
            
            # Verifica se há uma foto específica ou usa a padrão
            if obj.avatar_url and not obj.avatar_url.name.endswith('user_default.png'):
                avatar = obj.avatar_url.url
            else:
                avatar = f"{settings.MEDIA_URL}user_photos/user_default.png"
            
            # Retorna URL completa se houver request, caso contrário retorna relativa
            return request.build_absolute_uri(avatar) if request else avatar
class MissionSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.all(),
        required=False,
        allow_empty=True,
        write_only=True  # <- Isso oculta no output!
    )

    class Meta:
        model = Mission
        fields = "__all__" 

    def create(self, validated_data):
        users = validated_data.pop('users', [])
        mission = Mission.objects.create(**validated_data)
        mission.users.set(users)
        return mission

    def update(self, instance, validated_data):
        users = validated_data.pop('users', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if users is not None:
            instance.users.set(users)

        instance.save()
        return instance

class UserMissionsSerializer(serializers.ModelSerializer):
    missions = MissionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'missions']

class MissionUsersSerializer(serializers.ModelSerializer):
    users = CustomUserReadSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = ['id', 'name', 'description', 'users']

class AssociateMissionsToUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    mission_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

    def validate(self, data):
        user_id = data.get("user_id")
        mission_ids = data.get("mission_ids")

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")

        missions = Mission.objects.filter(id__in=mission_ids)
        if missions.count() != len(mission_ids):
            raise serializers.ValidationError("Uma ou mais missões não foram encontradas.")

        data["user"] = user
        data["missions"] = missions
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        missions = self.validated_data["missions"]
        user.missions.add(*missions) # ou .add(*missions) se quiser somar
        return user





class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model= Setor 
        fields = "__all__"

class EquipamentSerializer(serializers.ModelSerializer):
    class Meta:
        model= Equipament 
        fields = "__all__"  

class EquipamentLineSerializer(serializers.ModelSerializer):
    class Meta: 
        model= EquipamentLine 
        fields = "__all__"  


class ResponseQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseQuiz
        fields = ["id","text", "is_correct"]

class QuestionSerializer(serializers.ModelSerializer):
    responses = ResponseQuizSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id","text", "responses"]

    def create(self, validated_data):
        responses_data = validated_data.pop("responses")
        question = Question.objects.create(**validated_data)
        
        for response_data in responses_data:
            ResponseQuiz.objects.create(question=question, **response_data)
        
        return question

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ["id", "name", "description", "questions"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            responses_data = question_data.pop("responses")
            question = Question.objects.create(quiz=quiz, **question_data)

            for response_data in responses_data:
                ResponseQuiz.objects.create(question=question, **response_data)

        return quiz
    
    def update(self, instance, validated_data):
        # Atualiza dados básicos do Quiz
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Atualiza questões e respostas (se existirem no payload)
        if 'questions' in validated_data:
            questions_data = validated_data.pop('questions')
            self._update_questions(instance, questions_data)

        return instance

    def _update_questions(self, quiz, questions_data):
        current_question_ids = set(quiz.questions.values_list('id', flat=True))
        updated_question_ids = set()

        for question_data in questions_data:
            question_id = question_data.get('id', None)
            
            # Question existe? Atualiza. Não existe? Cria nova.
            if question_id and quiz.questions.filter(id=question_id).exists():
                question = quiz.questions.get(id=question_id)
                question.text = question_data.get('text', question.text)
                question.save()
                self._update_responses(question, question_data.get('responses', []))
            else:
                question = Question.objects.create(quiz=quiz, text=question_data['text'])
                self._create_responses(question, question_data.get('responses', []))
            
            updated_question_ids.add(question.id)

        # Remove questões não enviadas no payload
        quiz.questions.exclude(id__in=updated_question_ids).delete()

    def _update_responses(self, question, responses_data):
        current_response_ids = set(question.responses.values_list('id', flat=True))
        updated_response_ids = set()

        for response_data in responses_data:
            response_id = response_data.get('id', None)
            
            if response_id and question.responses.filter(id=response_id).exists():
                response = question.responses.get(id=response_id)
                response.text = response_data.get('text', response.text)
                response.is_correct = response_data.get('is_correct', response.is_correct)
                response.save()
            else:
                ResponseQuiz.objects.create(question=question, **response_data)
            
            if 'id' in response_data:
                updated_response_ids.add(response_data['id'])

        # Remove respostas não enviadas no payload
        question.responses.exclude(id__in=updated_response_ids).delete()

    def _create_responses(self, question, responses_data):
        for response_data in responses_data:
            ResponseQuiz.objects.create(question=question, **response_data)
    
class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ["question", "selected_response"]

    def validate_selected_response(self, value):
        """Garante que a resposta pertence à pergunta correta"""
        question_id = self.initial_data.get("question")
        if not ResponseQuiz.objects.filter(id=value.id, question_id=question_id).exists():
            raise serializers.ValidationError("Essa resposta não pertence à pergunta informada.")
        return value

class MultipleUserResponseSerializer(serializers.Serializer):
    responses = UserResponseSerializer(many=True)

    def create(self, validated_data):
        """Salva múltiplas respostas de uma vez"""
        request = self.context.get("request")  # Pegamos o usuário autenticado
        user = request.user
        responses_data = validated_data["responses"]
        
        user_responses = []
        for response_data in responses_data:
            response_data["user"] = user  # Associa o usuário autenticado
            user_responses.append(UserResponse(**response_data))

        return UserResponse.objects.bulk_create(user_responses)  # Salva todas as respostas de uma vez
    

class MissionQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model= MissionQuiz 
        fields = "__all__"
             
class SertorSerializer(serializers.ModelSerializer):
    class Meta:
        model= Setor 
        fields = "__all__"

class MissionProgressSerializer(serializers.ModelSerializer):
    class Meta: 
        model= MissionProgress 
        fields = "__all__"


class EquipamentLineSerializer(serializers.ModelSerializer):
    class Meta: 
        model= EquipamentLine 
        fields = "__all__"

class ProductItemSerializer(serializers.ModelSerializer):
    class Meta: 
        model= ProductItem 
        fields = "__all__"


class ProductionLineSerializer(serializers.ModelSerializer):
    class Meta: 
        model= ProductionLine 
        fields = "__all__"
class ReportEffiencySerializer(serializers.ModelSerializer):
    class Meta: 
        model= ReportEffiency    
        fields = "__all__" 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model= Product 
        fields =['id', 'name', 'description','photo', 'photo_url']

        def get_photo_url(self, obj):
            request = self.context.get('request')
            
            # Verifica se há uma foto específica ou usa a padrão
            if obj.photo and not obj.photo.name.endswith('default_avatar.png'):
                photo_url = obj.photo.url
            else:
                photo_url = f"{settings.MEDIA_URL}product_photos/default_avatar.png"
            
            # Retorna URL completa se houver request, caso contrário retorna relativa
            return request.build_absolute_uri(photo_url) if request else photo_url

class MonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model= Monitoring 
        fields = "__all__"


class HistoricalMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model= HistoricalMeasurement 
        fields = "__all__"
class DeviceIotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceIot
        fields = ['id', 'name', 'devEui']
class SectionSerializer(serializers.ModelSerializer):

    device_iots = DeviceIotSerializer(many=True, read_only=True)
    device_iots_ids = serializers.PrimaryKeyRelatedField(
        queryset=DeviceIot.objects.all(),
        many=True,
        write_only=True,
        source='device_iots'
    )
    class Meta:
        model= Section 
        fields = "__all__"

class ParameterMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model= ParametersMinitoring
        fields = "__all__"


class TypeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model= TypeSection  
        fields = "__all__"


class MensurationSerializer(serializers.ModelSerializer):
    class Meta:
        model= Mensuration 
        fields = "__all__"

class AssociationIotSerializer(serializers.ModelSerializer):
    class Meta:
        model= AssociationIot 
        fields = "__all__"
              
class AchivementSerializer(serializers.ModelSerializer):
    class Meta:
        model= Achievement 
        fields = "__all__"

class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model= Claim 
        fields = "__all__"

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model= Reward 
        fields = "__all__"


class SectionHistoryMensurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionHistoryMensurement
        fields = '__all__'

'''
LOJA
'''

class ProductLojaSerializer(serializers.ModelSerializer):
    disponivel = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductLoja
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'image', 
            'quantity',
            'disponivel'
        ]
        read_only_fields = ['disponivel']
    
    def get_disponivel(self, obj):
        """Indica se o produto está disponível para compra (estoque > 0)"""
        return obj.quantity > 0

class ProductLojaDetailSerializer(ProductLojaSerializer):
    vendas_totais = serializers.SerializerMethodField()
    
    class Meta(ProductLojaSerializer.Meta):
        fields = ProductLojaSerializer.Meta.fields + ['vendas_totais']
    
    def get_vendas_totais(self, obj):
        """Retorna o total de unidades vendidas deste produto"""
        from django.db.models import Sum
        return obj.compra_set.aggregate(
            total_vendido=Sum('quantidade')
        )['total_vendido'] or 0
class ItemCompraSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    valor_total = serializers.SerializerMethodField()

    class Meta:
        model = ItemCompra
        fields = ['id', 'product', 'product_name', 'quantidade', 
                 'preco_unitario', 'valor_total']

    def get_valor_total(self, obj):
        return obj.valor_total

class CompraSerializer(serializers.ModelSerializer):
    itens = ItemCompraSerializer(many=True)
    valor_total = serializers.SerializerMethodField()

    class Meta:
        model = Compra
        fields = ['id', 'user', 'itens', 'data_compra', 'valor_total']

    def get_valor_total(self, obj):
        return sum(item.valor_total for item in obj.itens.all())

class CriarCompraSerializer(serializers.Serializer):
    produtos = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            allow_empty=False
        )
    )
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        """
        Valida se o usuário existe e retorna o objeto user
        """
        try:
            user = CustomUser.objects.get(id=value)
            if not user.is_active:
                raise serializers.ValidationError("Conta de usuário desativada")
            return user
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Nenhum usuário encontrado com este ID")

    def validate(self, data):
        # Extrai todos os IDs de produtos únicos
        produtos_ids = list({item['product_id'] for item in data['produtos']})
        products = ProductLoja.objects.filter(id__in=produtos_ids)
        
        # Cria um dicionário para acesso rápido
        products_dict = {p.id: p for p in products}
        
        if len(products_dict) != len(produtos_ids):
            missing_ids = set(produtos_ids) - set(products_dict.keys())
            raise serializers.ValidationError(
                f"Produtos não encontrados: IDs {missing_ids}"
            )
        
        # Verifica estoque considerando quantidades somadas
        product_quantities = {}
        for item in data['produtos']:
            product_id = item['product_id']
            product_quantities[product_id] = product_quantities.get(product_id, 0) + item['quantidade']
        
        for product_id, total_quantity in product_quantities.items():
            product = products_dict[product_id]
            if product.quantity < total_quantity:
                raise serializers.ValidationError(
                    f"Estoque insuficiente para {product.name} (Disponível: {product.quantity}, Solicitado: {total_quantity})"
                )
        
        data['products_dict'] = products_dict
        return data
    

'''
Integração com HARDWARE
'''
