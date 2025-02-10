from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Genero, Material, Categoria, Producto, Multimedia,
    Realista, Vibrador, Lubricante, Digital, Carrito, ItemCarrito,
    Estado, Compra, HistorialCompra
)

# Registro personalizado para el modelo User
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # Configuración de los campos a mostrar y editar
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    # Configuración del formulario para crear nuevos usuarios
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'phone_number', 'is_staff')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

# Registra el resto de los modelos en el administrador
admin.site.register(Genero)
admin.site.register(Material)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Multimedia)
admin.site.register(Realista)
admin.site.register(Vibrador)
admin.site.register(Lubricante)
admin.site.register(Digital)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Estado)
admin.site.register(Compra)
admin.site.register(HistorialCompra)
