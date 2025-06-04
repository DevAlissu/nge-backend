# myapp/views.py
from rest_framework import status, serializers
from rest_framework import  viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.db.models import F
from django.contrib.auth.models import AnonymousUser

from rest_framework.decorators import api_view



from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response

from django.http import JsonResponse
import logging
import datetime

logger = logging.getLogger(__name__)


# myapp/views.py
from rest_framework import generics
from .models import (
    CustomUser, 
    Equipament, EquipamentLine,
    Product, ProductionLine,ProductItem, ReportEffiency,
    Section,TypeSection,
    Monitoring, 
    HistoricalMeasurement,
    DeviceIot,
    AssociationIot,
    Mensuration,
    Achievement,
    ProductLoja, SectionHistoryMensurement,SectionHistoryMensurement,

    Mission, MissionProgress, MissionProgress, 
    Quiz, MissionQuiz,MissionQuiz, ResponseQuiz,UserResponse,
    Claim, 
    Reward, ReportEffiency,Setor, Compra, ItemCompra, DeviceIotEvent, ParametersMinitoring
    
    )
from .serializers import (
    CustomUserReadSerializer,
    EquipamentSerializer, EquipamentLineSerializer,
    ProductSerializer, ProductItemSerializer,ProductionLineSerializer,
    SectionSerializer, ReportEffiencySerializer,TypeSectionSerializer,
    MonitoringSerializer,
    HistoricalMeasurementSerializer,
    DeviceIotSerializer, MensurationSerializer, AssociationIotSerializer,
    AchivementSerializer,
    ClaimSerializer,
    RewardSerializer,
    MissionSerializer, 
    MissionProgressSerializer, 
    MissionProgress, UserMissionsSerializer, AssociateMissionsToUserSerializer,MissionUsersSerializer,
    MissionQuizSerializer,
    ReportEffiencySerializer,
    QuizSerializer,SertorSerializer, UserResponseSerializer, MultipleUserResponseSerializer,
   
    CompraSerializer, ProductLojaSerializer, CriarCompraSerializer,SectionHistoryMensurementSerializer,ParameterMonitoringSerializer
    

    

    
)

from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin, IsOperador, IsGerente


#View para cadastrar um usuário no Banco
'''
Segue formato do JSON 
{
  "username": "userName",
  "email": "userName@email.com",
  "password": "senha",
  "name": "Name",
  "role": "ADMIN"
}
'''

TYPE_SECTION_EQUIPAMENT = "EQUIPAMENTO"
TYPE_SECTION_SETOR = "SETOR"
TYPE_SECTION_LINE = 'LINHA'
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Gera o token JWT
        token = super().get_token(user)
        
        # Adiciona claims personalizados ao token
        token['id'] = user.id  # Adiciona o ID do usuário ao token
        token['role'] = user.role
        token['name'] = user.name
        return token

    def validate(self, attrs):
        # Valida as credenciais e gera a resposta padrão
        data = super().validate(attrs)
        
        # Adiciona dados personalizados à resposta
        data['id'] = self.user.id  # Adiciona o ID do usuário à resposta
        data['role'] = self.user.role
        data['name'] = self.user.name
        #data['avatar_url'] = self.user.avatar_url if self.user.avatar_url is not None else 'DEFAULT_AVATAR_URL'
        data['email'] = self.user.email
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
Rota para Listar todos os usuários
Papel ADMIN
'''
class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserReadSerializer
    permission_classes = [AllowAny]

class UserByEmailAPIView(APIView):
    """
    View para buscar usuário pelo e-mail sem usar `get_object_or_404`.
    """

    #permission_classes = [IsAuthenticated, IsAdmin ]

    def get(self, request):
        email = request.query_params.get('email', '').strip()
        if not email:
            return Response(
                {"detail": "O parâmetro 'email' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Busca ignorando case
        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            return Response(
                {"detail": f"Nenhum usuário encontrado com o e-mail '{email}'."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        


'''
View Para Missões e Usuario'''

class UserMissionsView(APIView):
    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserMissionsSerializer(user)
        return Response(serializer.data)
    
class AssociateMissionsToUserView(APIView):
    def post(self, request):
        serializer = AssociateMissionsToUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'detail': 'Missões associadas com sucesso.', 'user_id': user.id})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MissionUsersView(APIView):
    def get(self, request, mission_id):
        try:
            mission = Mission.objects.get(id=mission_id)
        except Mission.DoesNotExist:
            return Response({'detail': 'Missão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MissionUsersSerializer(mission)
        return Response(serializer.data)

'''
 FINAL
'''
class EquipamentViewSet(viewsets.ModelViewSet):
    #permission_classes = [AllowAny]
    queryset = Equipament.objects.all()
    serializer_class = EquipamentSerializer

    def create(self, request, *args, **kwargs):
        # Copia os dados da requisição para poder modificar
        data = request.data.copy()
        # Obtém o ID do setor se existir nos dados
        product_line_id = data.get('production_line')
        
        if product_line_id:
            try:
                # Busca o setor no banco de dados
                line = ProductionLine.objects.get(pk=product_line_id)
                # Concatena o nome do setor ao nome da linha de produção
                data['name'] = f"{line.name}-{data.get('name', '')}"
            except Setor.DoesNotExist:
                pass
        else:
          
            return Response({"error": "Linha de Produção é obrigatório"}, status=status.HTTP_400_BAD_REQUEST) # Mantém o nome original se o setor não existir
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProductViewSet(viewsets.ModelViewSet):
    #permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():  # Garante que todas as operações sejam atômicas
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            section_pai = serializer.save()  # Salva a seção principal
            secoes_filhas = []  # Lista para armazenar as seções filhas criadas

            try:
                # 🔹 Se a seção criada for um SETOR, cria as LINHAS e depois os EQUIPAMENTOS
                if section_pai.type_section and section_pai.type_section.name.upper() == TYPE_SECTION_SETOR :
                    linhas = ProductionLine.objects.filter(setor=section_pai.setor)
                    type_line = TypeSection.objects.filter(name=TYPE_SECTION_LINE).first()

                    for i, linha in enumerate(linhas):
                        section_linha = Section.objects.create(
                            name=f"{linha.name}",
                            description=f"",
                            secticon_parent=section_pai,  # O pai da linha é o SETOR
                            is_monitored=False,
                            type_section=type_line,
                            DeviceIot=None,
                            productionLine=linha,
                            equipament=None,
                            setor=section_pai.setor,  # O setor continua o mesmo
                        )
                        secoes_filhas.append(section_linha)
                        print(f"✅ Seção de LINHA criada: {section_linha.name}")

                        # Criar os equipamentos associados à LINHA (passando a seção da LINHA como pai)
                        self._criar_secoes_equipamentos(section_linha, linha, secoes_filhas)

                # 🔹 Se a seção criada for uma LINHA sem setor, cria apenas os EQUIPAMENTOS dessa linha
                elif section_pai.type_section and section_pai.type_section.name == TYPE_SECTION_LINE:
                    if section_pai.productionLine:  # Verifica se a linha tem uma produção associada
                        self._criar_secoes_equipamentos(section_pai, section_pai.productionLine, secoes_filhas)
                    else:
                        print("⚠️ A seção do tipo LINHA não tem uma productionLine associada.")
                

            except Exception as e:
                print(f"❌ERRO ao criar seções filhas: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Retorna a seção criada e todas as seções filhas geradas
            return Response(
                {
                    "message": "Seção criada com sucesso!",
                    "section_pai": SectionSerializer(section_pai).data,
                    "sections_filhas": SectionSerializer(secoes_filhas, many=True).data,
                },
                status=status.HTTP_201_CREATED
            )


    def _criar_secoes_equipamentos(self, section_linha, linha, secoes_filhas):
        """Cria seções de equipamentos associadas a uma linha."""
        equipamentos = Equipament.objects.filter(production_line=linha)
        type_equipament = TypeSection.objects.filter(name=TYPE_SECTION_EQUIPAMENT).first()

        for j, equipamento in enumerate(equipamentos):
            section_equipamento = Section.objects.create(
                name=f"{equipamento.name}",
                description=f"",
                secticon_parent=section_linha,  # O pai agora é a seção da LINHA
                is_monitored=False,
                type_section=type_equipament,
                DeviceIot=None,
                productionLine=equipamento.production_line,
                equipament=equipamento,
                setor=section_linha.setor,  # Mantemos o setor da linha (ou None se não houver setor)
            )
            secoes_filhas.append(section_equipamento)
            print(f"✅ Seção de EQUIPAMENTO criada: {section_equipamento.name}")

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():  # Garante que todas as operações sejam atômicas
            section = self.get_object()  # Obtém a seção a ser deletada

            try:
                # Exclui recursivamente as subseções
                self._delete_subsections(section)

                # Exclui a seção principal
                section.delete()

                return Response({"message": "Seção e suas subseções excluídas com sucesso!"}, status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                print(f"❌ ERRO ao deletar seção: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _delete_subsections(self, section):
        """Deleta recursivamente as subseções (linhas e equipamentos)."""
        subsections = Section.objects.filter(secticon_parent=section)

        for subsection in subsections:
            # Chamada recursiva para deletar subseções aninhadas
            self._delete_subsections(subsection)

            # Deleta a subseção
            print(f"🗑️ Deletando subseção: {subsection.name}")
            subsection.delete() 
   
    

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtém a seção pai
        serializer = self.get_serializer(instance)

        # Obtém todas as seções filhas diretas dessa seção pai
        secoes_filhas = Section.objects.filter(secticon_parent=instance)
        secoes_filhas_serializadas = SectionSerializer(secoes_filhas, many=True).data

        # Criar estrutura para armazenar todas as relações
        estrutura = {
            "section_pai": serializer.data,
            "sections_filhas": [],
        }

        for secao_filha in secoes_filhas:
            secao_filha_data = SectionSerializer(secao_filha).data
            
            # Buscar seções filhas das linhas associadas à seção filha (se houver)
            sub_secoes = Section.objects.filter(secticon_parent=secao_filha)
            sub_secoes_serializadas = SectionSerializer(sub_secoes, many=True).data

            # Adicionar equipamentos associados a cada sub-seção (se houver)
            for sub_secao in sub_secoes:
                equipamentos = Section.objects.filter(secticon_parent=sub_secao, type_section__name=TYPE_SECTION_EQUIPAMENT)
                equipamentos_serializados = SectionSerializer(equipamentos, many=True).data
                sub_secao_data = SectionSerializer(sub_secao).data
                sub_secao_data["equipamentos"] = equipamentos_serializados
                sub_secoes_serializadas.append(sub_secao_data)

            secao_filha_data["sub_secoes"] = sub_secoes_serializadas
            estrutura["sections_filhas"].append(secao_filha_data)

        return Response(estrutura)     

class ParameterMonitoringViewSet(viewsets.ModelViewSet):
    #permission_classes = [AllowAny]
    queryset = ParametersMinitoring.objects.all()
    serializer_class = ParameterMonitoringSerializer

class TypeSectionViewSet(viewsets.ModelViewSet):
    #permission_classes = [AllowAny]
    queryset = TypeSection.objects.all()
    serializer_class = TypeSectionSerializer    


class MonitoringViewSet(viewsets.ModelViewSet):
    #permission_classes = [AllowAny]
    queryset = Monitoring.objects.all()
    serializer_class = MonitoringSerializer


class MonitoringActiveViewSet(viewsets.ReadOnlyModelViewSet):  # Alterado para ReadOnlyModelViewSet
    """
    ViewSet para listar (GET) monitoramentos que possuem missões associadas.
    Permite apenas operações de leitura.
    """
    serializer_class = MonitoringSerializer
    
    def get_queryset(self):
        # Retorna apenas monitoramentos com pelo menos uma missão associada
        return Monitoring.objects.filter(mission__isnull=False).distinct()

class MonitoringActiveCountViewSet(viewsets.ViewSet):
    """
    ViewSet que retorna APENAS a contagem de monitoramentos com missões associadas
    Formato de resposta: {"count": 5}
    """
    def list(self, request):
        count = Monitoring.objects.filter(mission__isnull=False).distinct().count()
        return Response({count})

class HistoricalMeasurementViewSet(viewsets.ModelViewSet):
    #permission_classes = [AllowAny]
    queryset = HistoricalMeasurement.objects.all()
    serializer_class = HistoricalMeasurementSerializer

class DeviceIotViewSet(viewsets.ModelViewSet):    
    queryset = DeviceIot.objects.all()
    serializer_class = DeviceIotSerializer

    @action(detail=False, methods=['get'])
    def get_by_device_name(self, request):
        device_name = request.query_params.get('deviceName', None)
        if not device_name:
            return Response(
                {"error": "O parâmetro 'deviceName' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        devices = self.queryset.filter(deviceName=device_name)
        serializer = self.get_serializer(devices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_by_dev_eui(self, request):
        dev_eui = request.query_params.get('devEui', None)
        if not dev_eui:
            return Response(
                {"error": "O parâmetro 'devEui' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            device = self.queryset.get(devEui=dev_eui)
            serializer = self.get_serializer(device)
            return Response(serializer.data)
        except DeviceIot.DoesNotExist:
            return Response(
                {"error": "Dispositivo não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

class MensurationViewSet(viewsets.ModelViewSet):    
    #permission_classes = [AllowAny]
    queryset = Mensuration.objects.all()
    serializer_class = MensurationSerializer


class AssociationIotViewSet(viewsets.ModelViewSet):    
    #permission_classes = [AllowAny]
    queryset = AssociationIot.objects.all()
    serializer_class = AssociationIotSerializer

class AchivementViewSet(viewsets.ModelViewSet):    
    #permission_classes = [AllowAny]
    queryset = Achievement.objects.all()
    serializer_class = AchivementSerializer
    
class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.all()    
    serializer_class = ClaimSerializer

class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()        
    serializer_class = RewardSerializer


class ProductItemViewSet(viewsets.ModelViewSet):
    queryset = ProductItem.objects.all()        
    serializer_class = ProductItemSerializer

   

class MissionQuizViewSet(viewsets.ModelViewSet):
    queryset = MissionQuiz.objects.all()        
    serializer_class = MissionQuizSerializer


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()        
    serializer_class = QuizSerializer

class ReportEffiencyViewSet(viewsets.ModelViewSet):
    queryset = ReportEffiency.objects.all()        
    serializer_class = ReportEffiencySerializer

class ProductItemViewSet(viewsets.ModelViewSet):
    queryset = ProductItem.objects.all()        
    serializer_class = ProductItemSerializer

class MissionProgressViewSet(viewsets.ModelViewSet):
    queryset = MissionProgress.objects.all()        
    serializer_class = MissionProgressSerializer

class ProductionLineViewSet(viewsets.ModelViewSet):
    queryset = ProductionLine.objects.all()        
    serializer_class = ProductionLineSerializer

    def create(self, request, *args, **kwargs):
        # Copia os dados da requisição para poder modificar
        data = request.data.copy()
        # Obtém o ID do setor se existir nos dados
        setor_id = data.get('setor')
        
        if setor_id:
            try:
                # Busca o setor no banco de dados
                setor = Setor.objects.get(pk=setor_id)
                # Concatena o nome do setor ao nome da linha de produção
                data['name'] = f"{setor.name} → {data.get('name', '')}"
            except Setor.DoesNotExist:
                pass
        else:
            return Response({"error": "Setor é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
                
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class EquipamentLineViewSet(viewsets.ModelViewSet):
    queryset = EquipamentLine.objects.all()        
    serializer_class = EquipamentLineSerializer

class MissionProgressViewSet(viewsets.ModelViewSet):
    queryset = MissionProgress.objects.all()        
    serializer_class = MissionProgressSerializer


class ReportEffiencyViewSet(viewsets.ModelViewSet):
    queryset = ReportEffiency.objects.all()        
    serializer_class = ReportEffiencySerializer
class MissionProgressViewSet(viewsets.ModelViewSet):
    queryset = MissionProgress.objects.all()        
    serializer_class = MissionProgressSerializer

class MissionQuizViewSet(viewsets.ModelViewSet):
    queryset = MissionQuiz.objects.all()        
    serializer_class = MissionQuizSerializer

class SetorViewSet(viewsets.ModelViewSet):
    queryset = Setor.objects.all()        
    serializer_class = SertorSerializer 
    

''' VIEWS CUSTOMIZADAS'''




class RankingView(APIView):
    def get(self, request, format=None):
        # Recupera todos os usuários com role 'GAME'
        users = CustomUser.objects.all().filter(role='GAME')
        ranking_data = []
        # Para cada usuário, calcula a soma dos pontos das conquistas
        for user in users:
            achievements = Achievement.objects.filter(user_achievement=user)
            total_points = sum(achievement.points for achievement in achievements)
            ranking_data.append({
                'user_id': user.id,
                'name': user.name,
                'role': user.role,
                'total_points': total_points
            })

        # Ordena o ranking por total_points (do maior para o menor)
        ranking_data.sort(key=lambda x: x['total_points'], reverse=True)
        # Retorna o ranking como JSON
        return JsonResponse(ranking_data, safe=False)
 

class ProfileUserView(APIView):
    def rankingLocal(self):
        # Recupera todos os usuários com role 'GAME'
        users = CustomUser.objects.all().filter(role='GAME')
        ranking_data = []

        # Para cada usuário, calcula a soma dos pontos das conquistas
        for user in users:
            achievements = Achievement.objects.filter(user_achievement=user)
            total_points = sum(achievement.quantity_xp for achievement in achievements)
            pontos_coletados = user.total_xp
            nivel = user.nivel
            total_nansen_coins = user.total_nansen_coins
            ranking_data.append({
                'user_id': user.id,
                'name': user.name,
                'role': user.role,
                'pontos_coletados': pontos_coletados,
                'nivel': nivel,
                'total_nansen_coins': total_nansen_coins,
                'total_points': total_points
            })

        # Ordena o ranking por total_points (do maior para o menor)
        ranking_data.sort(key=lambda x: x['total_points'], reverse=True)
        return ranking_data  # Retorna a lista ordenada

    def get(self, request, user_id, format=None):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Recupera as conquistas do usuário
        achievements = Achievement.objects.filter(user_achievement=user)
        user_serializer = CustomUserSerializer(user)
        achievements_serializer = AchivementSerializer(achievements, many=True)

        # Obtém o ranking local
        pontos_user = self.rankingLocal()

        # Filtra o total de pontos do usuário específico
        total_pontos = next(
            (user['total_points'] for user in pontos_user if user["user_id"] == user_id),
            0  # Valor padrão caso o usuário não seja encontrado no ranking
        )

        # Monta a resposta
        response_data = {
            "user": user_serializer.data,
            
            "achievements": achievements_serializer.data,
            "total_points": total_pontos  # Adiciona o total de pontos à resposta
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class EquipamentByProductionLineView(APIView):
    def get(self, request, production_line_id):
        try:
            production_line = ProductionLine.objects.get(id=production_line_id)
            equipaments = Equipament.objects.filter(production_line=production_line)
            serializer = EquipamentSerializer(equipaments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductionLine.DoesNotExist:
            return Response({"error": "Production Line not found"}, status=status.HTTP_404_NOT_FOUND)
        
class EquipamentBySectionView(APIView):
    
    def get(self, request, section_id, *args, **kwargs):
        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=status.HTTP_404_NOT_FOUND)

        if section.type_section.name == "LINHA":
            productionLine = section.productionLine
            equipaments = Equipament.objects.filter(production_line=productionLine)
            serializer = EquipamentSerializer(equipaments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Section is not a production line"}, status=status.HTTP_400_BAD_REQUEST)

        
    

class QuizCreateView(APIView):
    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizDeleteView(APIView):
    def delete(self, request, quiz_id):
        # Busca o quiz ou retorna 404 se não existir
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Deleta o quiz (as questões serão deletadas em cascata automaticamente)
        quiz.delete()
        
        return Response(
            {"message": "Quiz e suas questões foram deletados com sucesso"},
            status=status.HTTP_204_NO_CONTENT
        )
class UserResponseView(APIView):
    permission_classes = [AllowAny]  # Somente usuários logados podem responder

    def post(self, request):
        serializer = UserResponseSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Resposta salva com sucesso!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class MultipleUserResponseView(APIView):
    permission_classes = [IsAuthenticated]  # Somente usuários autenticados

    def post(self, request):
        serializer = MultipleUserResponseSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Respostas salvas com sucesso!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

    
class QuizListView(ListAPIView):
    """Lista todos os quizzes"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class QuizDetailView(RetrieveAPIView):
    """Busca um quiz pelo ID"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    lookup_field = "id"  # Busca pelo ID

class QuizOperationsView(APIView):
    """
    View para atualizar (PUT) ou deletar (DELETE) um Quiz por ID.
    """
    def get_object(self, quiz_id):
        return get_object_or_404(Quiz, id=quiz_id)

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)  # Retorna o JSON completo
    def put(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        serializer = QuizSerializer(quiz, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, quiz_id):
        quiz = self.get_object(quiz_id)
        quiz.delete()
        return Response(
            {"message": "Quiz deletado com sucesso"},
            status=status.HTTP_204_NO_CONTENT
        )

'''
 LOJA
'''

class ProductLojaViewSet(viewsets.ModelViewSet):
    queryset = ProductLoja.objects.all()
    serializer_class = ProductLojaSerializer
class LojaViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['post'], url_path='comprar')
    def comprar(self, request):
        serializer = CriarCompraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
           
        data = serializer.validated_data
        
        with transaction.atomic():
            compra = Compra.objects.create(user_id=data['user_id'])
            
            itens = []
            # Agrupa quantidades por produto
            product_quantities = {}
            for item in data['produtos']:
                product_id = item['product_id']
                product_quantities[product_id] = product_quantities.get(product_id, 0) + item['quantidade']
            
            # Cria itens e atualiza estoque
            for product_id, quantidade in product_quantities.items():
                product = data['products_dict'][product_id]
                
                itens.append(ItemCompra(
                    compra=compra,
                    product=product,
                    quantidade=quantidade,
                    preco_unitario=product.price
                ))
                
                ProductLoja.objects.filter(id=product_id).update(
                    quantity=F('quantity') - quantidade
                )

                
                
                
            
            ItemCompra.objects.bulk_create(itens)
        
        return Response(CompraSerializer(compra).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='minhas-compras/(?P<user_id>\d+)')
    def minhas_compras(self, request, user_id=None):
        compras = Compra.objects.filter(user_id=user_id).prefetch_related('itens__product')
        serializer = CompraSerializer(compras, many=True)
        return Response(serializer.data)
    
'''
MISSÃO

'''

class MissionProgressAPI(APIView):

    def get(self, request, mission_id):
        # Verifica se é um usuário anônimo
        if isinstance(request.user, AnonymousUser):
            return Response({
                "mission_id": mission_id,
                "current_progress": 0,
                "status": "Não autenticado",
                "message": "Faça login para rastrear seu progresso"
            }, status=200)
        
        # Usuário autenticado
        progress = request.user.get_mission_progress(mission_id)
        
        if progress:
            return Response({
                "mission_id": mission_id,
                "current_progress": progress.current_progress,
                "status": progress.status
            })
        
        return Response({
            "mission_id": mission_id,
            "current_progress": 0,
            "status": "Não iniciada"
        })
    

'''
Integração com HARDWARE
'''
@api_view(['POST'])
def hardware_receive(request):
    # Verifica 'event=up' na URL
    if request.query_params.get('event') != 'up':
        logger.warning("Tentativa de acesso sem parâmetro event=up")
        return Response({"error": "event=up é obrigatório na URL"}, status=400)

    # Extrai campo deviceInfo

    device_info = request.data.get('deviceInfo')

    if device_info:
        logger.warning(f"Campo 'deviceInfo' > : {device_info}")
    logger.warning(f"Medição salva: {device_info}")   

    # Extrai 'object' do JSON
    object_data = request.data.get('object')
    if not object_data:
        logger.warning("Campo 'object' não encontrado no body")
        return Response({"error": "'object' é obrigatório no body"}, status=400)
    
    logger.warning(f"Campo 'Object' >>> : {object_data}")

    # Pega 'energia_ativa_kWh' do JSON (nome deve bater com o model!)
    energia_ativa = object_data.get('energia_ativa_kWh')

    try:

        # 1. Busca o último registro da section (id=1)
        ultimo_registro = SectionHistoryMensurement.objects.filter(
            section_id=1
        ).order_by('-id').first()
        
        # 2. Calcula o novo intervalo
        novo_interval = (ultimo_registro.interval + 10) if ultimo_registro else 10


        
        # 3

        event = DeviceIotEvent.objects.create(
            tenantId=device_info.get('tenantId'),
            tenantName=device_info.get('tenantName'),
            applicationId=device_info.get('applicationId'),
            applicationName=device_info.get('applicationName'),
            deviceProfileId=device_info.get('deviceProfileId'),
            deviceProfileName=device_info.get('deviceProfileName'),
            deviceName=device_info.get('deviceName'),
            devEui=device_info.get('devEui'),
            deviceClassEnabled=device_info.get('deviceClassEnabled'),

            energia_ativa_kWh=object_data.get('energia_ativa_kWh'),
            tensao_fase_A=object_data.get('tensao_fase_A'),
            tensao_fase_B=object_data.get('tensao_fase_B'),
            tipo_medidor=object_data.get('tipo_medidor'),
            corrente_fase_B=object_data.get('corrente_fase_B'),
            corrente_fase_A=object_data.get('corrente_fase_A'),
            tags=device_info.get('tags')
            
        )

        if event:
            # 4. Salva a nova medição
            historico = SectionHistoryMensurement.objects.create(

                tenantId=event.tenantId,
                tenantName=event.tenantName,
                applicationId=event.applicationId,
                applicationName=event.applicationName,
                deviceProfileId=event.deviceProfileId,
                deviceProfileName=event.deviceProfileName,
                deviceName=event.deviceName,
                devEui=event.devEui,
                deviceClassEnabled=event.deviceClassEnabled,

                energia_ativa_kWh=event.energia_ativa_kWh,
                tensao_fase_A=event.tensao_fase_A,
                tensao_fase_B=event.tensao_fase_B,
                tipo_medidor=event.tipo_medidor,
                corrente_fase_B=event.corrente_fase_B,
                corrente_fase_A=event.corrente_fase_A,
                # Campo corrigido (kWh maiúsculo)
                interval=novo_interval,
                section=Section.objects.get(id=1)
            )

            if historico:
                event.is_sended = True
                event.save()
       

        logger.info(f"Medição salva: {historico}")
        return Response({"device": device_info, "object": object_data}, status=200)
    

    except Section.DoesNotExist:
        logger.error("Section com id=1 não encontrada")
        return Response({"error": "Section inválida"}, status=400)

    except Exception as e:  # Garante que 'e' está definida
        logger.error(f"Erro ao salvar medição: {str(e)}")
        return Response({"error": "Falha ao salvar dados","event": device_info}, status=500)



class SectionHistoryMensurementViewSet(viewsets.ModelViewSet):
   
    queryset = SectionHistoryMensurement.objects.all()
    serializer_class = SectionHistoryMensurementSerializer

    filterset_fields = ['section']  # Filtra por ?section=<id>

    # Não é necessário sobrescrever perform_create/update/destroy
    # pois o model já cuida da atualização automaticamente via save()

    # Opcional: Filtro personalizado se precisar de lógica adicional
    def get_queryset(self):
        queryset = super().get_queryset()
        section_id = self.request.query_params.get('section_id')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        return queryset