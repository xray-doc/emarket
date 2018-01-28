from django.contrib import admin
from .models import *



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

# @admin.register(Processor,
#                 Operational_system,
#                 Diagonal,
#                 ScreenResolution,
#                 BuiltInMemory,
#                 Ram
#                 )
# class ProductCharacteristicsAdmin(admin.ModelAdmin):
#     pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
    inlines = [ProductImageInline]

    # class Meta:
    #     model = Product


# class Operational_systemAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Operational_system._meta.fields]
#
#
#     class Meta:
#         model = Operational_system
# admin.site.register(Operational_system, Operational_systemAdmin)
#
#
# class DiagonalAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Diagonal._meta.fields]
#
#     class Meta:
#         model = Diagonal
# admin.site.register(Diagonal, DiagonalAdmin)
#
#
# class ScreenResolutionAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in ScreenResolution._meta.fields]
#
#     class Meta:
#         model = ScreenResolution
# admin.site.register(ScreenResolution, ScreenResolutionAdmin)
#
#
# class BuiltInMemoryAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in BuiltInMemory._meta.fields]
#
#     class Meta:
#         model = BuiltInMemory
# admin.site.register(BuiltInMemory, BuiltInMemoryAdmin)
#
#
# class RamAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Ram._meta.fields]
#
#     class Meta:
#         model = Ram
# admin.site.register(Ram, RamAdmin)
#
#
# class ProcessorAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Processor._meta.fields]
#
#     class Meta:
#         model = Processor
# admin.site.register(Processor, ProcessorAdmin)
#
#
