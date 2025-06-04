# myapp/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    RegisterView, 
    UserListView, 
    UserByEmailAPIView, 
    EquipamentViewSet, 
    ProductViewSet, ProductItemViewSet,
    ProductionLineViewSet,ReportEffiencyViewSet,
    MissionProgressViewSet, MissionQuizViewSet, QuizViewSet,
    SectionViewSet, 
    MonitoringViewSet,
    HistoricalMeasurementViewSet,
    DeviceIotViewSet,
    AssociationIotViewSet,
    MensurationViewSet  ,
    AchivementViewSet,
    UserMissionsView, AssociateMissionsToUserView, MissionUsersView,
    MissionViewSet,
    ClaimViewSet, 
    RewardViewSet,
    MissionProgressAPI,
    LojaViewSet,
    ProductLojaViewSet,
    MonitoringActiveCountViewSet,
    RankingView, SetorViewSet, TypeSectionViewSet, ProfileUserView, EquipamentByProductionLineView,
    QuizCreateView, QuizDeleteView, QuizOperationsView, QuizDetailView,QuizListView,UserResponseView, MultipleUserResponseView, EquipamentBySectionView,
    hardware_receive, SectionHistoryMensurementViewSet, ParameterMonitoringViewSet

    
    

    
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CustomTokenObtainPairView
from rest_framework import routers


router = routers.DefaultRouter()


router.register(r"equipaments", EquipamentViewSet)
router.register(r"products", ProductViewSet)
router.register(r"sections", SectionViewSet)
router.register(r'monitorings', MonitoringViewSet)

router.register(r"historical_measurements", HistoricalMeasurementViewSet)
router.register(r"device_iots", DeviceIotViewSet)  
router.register(r"association_iots", AssociationIotViewSet)
router.register(r"mensurations", MensurationViewSet) 
router.register(r"achivements", AchivementViewSet)
router.register(r"missions", MissionViewSet)
router.register(r"claims", ClaimViewSet)
router.register(r"rewards", RewardViewSet)
router.register(r"parameters_monitoring", ParameterMonitoringViewSet)

router.register(r"product_items", ProductItemViewSet)
router.register(r"production_lines", ProductionLineViewSet)
router.register(r"report_effiencies", ReportEffiencyViewSet)
router.register(r"mission_progress", MissionProgressViewSet)
#router.register(r"quizs", QuizViewSet) 
router.register(r"mission_quiz", MissionQuizViewSet)
router.register(r"setors", SetorViewSet)
router.register(r"type_sections", TypeSectionViewSet)
#router.register(r'monitoring-active', MonitoringActiveCountViewSet, basename='monitoring-active')
router.register(r'monitoring-active-count', MonitoringActiveCountViewSet, basename='monitoring-active-count')


router.register(r'products_loja', ProductLojaViewSet, basename='product_loja')

router.register(r'loja',LojaViewSet, basename='loja')

router.register(r'section-measurements', SectionHistoryMensurementViewSet)



urlpatterns = [

    path('',include(router.urls)),
    path('quizz/create/', QuizCreateView.as_view(), name='quiz-create'),
    path('quizzes/<int:quiz_id>/', QuizOperationsView.as_view(), name='quiz-operations'),
    path("quizzes/", QuizListView.as_view(), name="quiz_list"),
    path("quizzes/<int:id>/", QuizDetailView.as_view(), name="quiz_detail"),
    path("quizz/answer/", UserResponseView.as_view(), name="user_quiz_answer"),
    path("quizz/submit-answers/", MultipleUserResponseView.as_view(), name="submit_quiz_answers"),
    path('register/', RegisterView.as_view(), name='register'),
    path('ranking/', RankingView.as_view(), name='ranking'),
    path('profile_game/<int:user_id>/', ProfileUserView.as_view(), name='profile-user'),
   
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user_list'),  
    path('users/by-email/', UserByEmailAPIView.as_view(), name='by-email'),
    path('equipaments-by-production-line/<int:production_line_id>/', EquipamentByProductionLineView.as_view(), name='equipaments-by-production-line'),
    path('equipaments-by-section/<int:section_id>/', EquipamentBySectionView.as_view(), name='equipaments-by-section'),
    path('users/<int:user_id>/missions/', UserMissionsView.as_view(), name='user-missions'),
    path('users/associate-missions/', AssociateMissionsToUserView.as_view(), name='associate-missions'),
    path('missions/<int:mission_id>/users/', MissionUsersView.as_view(), name='mission-users'),
    path('missions/<int:mission_id>/progress/', MissionProgressAPI.as_view()),
    
    #Integração com HARDWARE
    path('hardware-receive/', hardware_receive, name='hardware-receive'),
    
]
