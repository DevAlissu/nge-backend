from django.contrib import admin
from .models import (CustomUser, 
    Equipament, EquipamentLine,
    Product, ProductionLine,ProductItem, ReportEffiency,
    Section,TypeSection,
    Monitoring, 
    HistoricalMeasurement,
    DeviceIot,
    AssociationIot,
    Mensuration,
    Achievement,
    ProductLoja, Product,

    Mission, MissionProgress, MissionProgress, 
    Quiz, MissionQuiz,MissionQuiz, ResponseQuiz,UserResponse,
    Claim, 
    Reward, ReportEffiency,Setor, Compra, ItemCompra)

# Registro básico
#admin.site.register(CustomUser)
admin.site.register(ProductLoja)
admin.site.register(Compra)
admin.site.register(ItemCompra)
admin.site.register(Equipament)
admin.site.register(EquipamentLine)
#admin.site.register(Product)
admin.site.register(ProductionLine)
admin.site.register(ProductItem)
admin.site.register(ReportEffiency)
admin.site.register(Section)
admin.site.register(TypeSection)
admin.site.register(Monitoring)
admin.site.register(HistoricalMeasurement)
admin.site.register(DeviceIot)
admin.site.register(AssociationIot)
admin.site.register(Mensuration)
admin.site.register(Achievement)
admin.site.register(Mission)
admin.site.register(MissionProgress)
admin.site.register(Quiz)
admin.site.register(MissionQuiz)
admin.site.register(ResponseQuiz)
admin.site.register(UserResponse)
admin.site.register(Claim)
admin.site.register(Reward)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')



