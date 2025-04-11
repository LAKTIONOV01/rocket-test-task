from django.contrib import admin
from django.utils.html import format_html
from .models import NetworkNode, Product, Employee
from django.db import transaction
from django.contrib import messages


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1



@admin.action(description="Очистить задолженность перед поставщиком")
def clear_debt(modeladmin, request, queryset):
    try:
        if queryset.count() > 20:  # Если объектов больше 20 → асинхронная очистка
            from .tasks import async_clear_debt
            node_ids = list(queryset.values_list('id', flat=True))
            async_clear_debt.delay(node_ids)
            modeladmin.message_user(
                request,
                f"Запущена фоновая очистка задолженности для {len(node_ids)} объектов",
                messages.SUCCESS
            )
        else:  # Для 20 и меньше → синхронная очистка
            with transaction.atomic():
                count = queryset.update(debt=0)
            modeladmin.message_user(
                request,
                f"Задолженность очищена для {count} объектов",
                messages.SUCCESS
            )
    except Exception as e:
        modeladmin.message_user(
            request,
            f"Ошибка: {str(e)}",
            messages.ERROR
        )

class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', 'city', 'country', 'supplier_link', 'debt', 'level')
    list_filter = ('city', 'country', 'node_type', 'level')
    inlines = [ProductInline, EmployeeInline]
    actions = [clear_debt]


    def supplier_link(self, obj):
        if obj.supplier:
            url = f"/admin/main/networknode/{obj.supplier.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "-"

    supplier_link.short_description = 'Поставщик'



admin.site.register(NetworkNode, NetworkNodeAdmin)
admin.site.register(Product)
admin.site.register(Employee)