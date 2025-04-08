from django.contrib import admin
from django.utils.html import format_html
from .models import NetworkNode, Product, Employee


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1


class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', 'city', 'country', 'supplier_link', 'debt', 'level')
    list_filter = ('city', 'country', 'node_type', 'level')
    inlines = [ProductInline, EmployeeInline]
    actions = ['clear_debt']

    def supplier_link(self, obj):
        if obj.supplier:
            url = f"/admin/electronics_network/networknode/{obj.supplier.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "-"

    supplier_link.short_description = 'Поставщик'

    def clear_debt(self, request, queryset):
        queryset.update(debt=0)

    clear_debt.short_description = "Очистить задолженность у выбранных объектов"


admin.site.register(NetworkNode, NetworkNodeAdmin)
admin.site.register(Product)
admin.site.register(Employee)