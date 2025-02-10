import logging
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from django.conf import settings
import mercadopago # type: ignore
from ..models import Producto, Carrito, ItemCarrito, Compra, HistorialCompra, Categoria, Digital, Testimonio
from ..forms import ContactoForm

# Configuración del logger para registrar eventos o errores en la vista
logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def index(request):
    context = {
        'productos_mas_vendidos': Producto.objects.filter(mas_vendido=True),
        'productos_destacados': Producto.objects.filter(es_destacado=True),
        'categorias': Categoria.objects.all(),
        'productos_digitales': Digital.objects.filter(es_destacado=True),
        'testimonios': Testimonio.objects.all(),
        'form': ContactoForm()
    }
    
    if request.method == "POST":
        try:
            form = ContactoForm(request.POST) # type: ignore
            if form.is_valid():
                form.save()
                context['form'] = form
                messages.success(request, "Datos guardados correctamente.")
                return redirect(reverse("index"))
            else:
                messages.error(request, "Se encontraron errores en el formulario.")
        except Exception as e:
            # Registro del error con detalle y traza completa para facilitar la depuración
            logger.error("Error al procesar la petición POST en la vista index: %s", e, exc_info=True)

            messages.error(request, "Ocurrió un error interno. Por favor, inténtalo de nuevo más tarde.")
            return redirect(reverse("index"))

    return render(request, "core/client/index.html", context)


@require_http_methods(["POST"])
def agregar_al_carrito(request: HttpRequest, producto_id: int) -> HttpResponse:
    """
    Agrega un producto al carrito del usuario. Si el producto ya está en el carrito, aumenta la cantidad.
    """
    usuario = request.user
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    
    if not created:
        item.cantidad += 1
    else:
        item.cantidad = 1
    
    item.save()
    messages.success(request, f"{producto.nombre} agregado al carrito.")
    return redirect(reverse("ver_carrito"))

@require_http_methods(["POST"])
def actualizar_item_carrito(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Actualiza la cantidad de un producto en el carrito.
    """
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    nueva_cantidad = int(request.POST.get("cantidad", 1))
    
    if nueva_cantidad > 0:
        item.cantidad = nueva_cantidad
        item.save()
        messages.success(request, "Cantidad actualizada correctamente.")
    else:
        messages.error(request, "La cantidad debe ser mayor a cero.")
    
    return redirect(reverse("ver_carrito"))

@require_http_methods(["POST"])
def eliminar_item_carrito(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Elimina un producto del carrito.
    """
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    messages.success(request, "Producto eliminado del carrito.")
    return redirect(reverse("ver_carrito"))

@require_http_methods(["GET"])
def ver_carrito(request: HttpRequest) -> HttpResponse:
    """
    Muestra los productos en el carrito del usuario.
    """
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related("producto")
    return render(request, "carrito/ver.html", {"items": items})

def verify_payment_token(token: str) -> bool:
    """
    Función de verificación del token de pago.
    En producción, esta función debería integrarse con la API del proveedor de pagos
    (por ejemplo, Stripe, PayPal, etc.) para validar la autenticidad y vigencia del token.
    Para efectos de demostración, se asume que el token válido es 'VALID_TOKEN'.
    """
    return token == "VALID_TOKEN"

@require_http_methods(["POST"])
def finalizar_compra(request: HttpRequest) -> HttpResponse:
    """
    Procesa de forma segura la compra de los productos en el carrito.
    
    Medidas de seguridad implementadas:
      - Se verifica que la conexión sea HTTPS mediante request.is_secure().
      - Se exige la presencia y validación de un token de pago.
      - Se utiliza transaction.atomic() para garantizar la integridad de la operación.
      - Se manejan y registran las excepciones de manera exhaustiva.
    
    Retorna:
      - HttpResponse: Redirección a la vista del historial de compras en caso de éxito, o
                      de vuelta al carrito en caso de error.
    """
    # Verificar que la conexión sea segura
    if not request.is_secure():
        messages.error(request, "La conexión debe ser segura (HTTPS) para realizar pagos.")
        return redirect(reverse("ver_carrito"))
    
    # Verificar la existencia y validez del token de pago
    payment_token = request.POST.get("payment_token")
    if not payment_token:
        messages.error(request, "Token de pago no proporcionado.")
        return redirect(reverse("ver_carrito"))
    
    if not verify_payment_token(payment_token):
        messages.error(request, "La verificación del pago ha fallado.")
        return redirect(reverse("ver_carrito"))
    
    usuario = request.user
    carrito = get_object_or_404(Carrito, usuario=usuario)
    
    if not carrito.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect(reverse("ver_carrito"))
    
    try:
        with transaction.atomic():
            # Se crea la compra; el estado 'completado' se asigna sólo si el pago es verificado
            compra = Compra.objects.create(usuario=usuario, estado='completado')
            
            # Se registra cada producto en el historial de la compra
            for item in carrito.items.all():
                HistorialCompra.objects.create(
                    compra=compra,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio
                )
            
            # Se vacía el carrito tras finalizar la compra
            carrito.items.all().delete()
            messages.success(request, "Compra realizada con éxito.")
    except Exception as e:
        logger.error("Error al finalizar la compra: %s", e, exc_info=True)
        messages.error(request, "No se pudo completar la compra. Inténtalo de nuevo.")
        return redirect(reverse("ver_carrito"))
    
    return redirect(reverse("historial_compras"))

@require_http_methods(["POST"])
def finalizar_compra_mercadopago(request: HttpRequest) -> HttpResponse:
    """
    Procesa la compra creando una preferencia de Mercado Pago y redirigiendo al usuario
    a la página de checkout de Mercado Pago.
    
    Medidas de seguridad implementadas:
      - Se fuerza el uso de HTTPS (request.is_secure()).
      - Uso de transacciones atómicas para garantizar la consistencia en la base de datos.
      - Manejo exhaustivo de excepciones y logging.
      - Creación de la preferencia de pago con back_urls para manejar el flujo de retorno.
    """
    # Verificar que la conexión sea segura (HTTPS)
    if not request.is_secure():
        messages.error(request, "La conexión debe ser segura (HTTPS) para realizar pagos.")
        return redirect(reverse("ver_carrito"))
    
    usuario = request.user
    carrito = get_object_or_404(Carrito, usuario=usuario)
    
    if not carrito.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect(reverse("ver_carrito"))
    
    # Inicializar el SDK de Mercado Pago con el token configurado en settings
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    
    # Preparar los ítems para la preferencia a partir del contenido del carrito
    items = []
    for item in carrito.items.all():
        items.append({
            "title": item.producto.nombre,
            "quantity": item.cantidad,
            "unit_price": float(item.producto.precio)
        })
    
    # Construir la preferencia con URLs de retorno
    preference_data = {
        "items": items,
        "back_urls": {
            "success": request.build_absolute_uri(reverse("pago_exitoso")),
            "failure": request.build_absolute_uri(reverse("pago_fallido")),
            "pending": request.build_absolute_uri(reverse("pago_pendiente")),
        },
        "auto_return": "approved"
    }
    
    try:
        # Crear la preferencia de pago en Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        init_point = preference["init_point"]
    except Exception as e:
        logger.error("Error creando la preferencia de Mercado Pago: %s", e, exc_info=True)
        messages.error(request, "Error al procesar el pago. Inténtalo de nuevo.")
        return redirect(reverse("ver_carrito"))
    
    # Registrar la compra en la base de datos (estado pendiente hasta confirmación de pago)
    try:
        with transaction.atomic():
            compra = Compra.objects.create(usuario=usuario, estado="pendiente")
            for item in carrito.items.all():
                HistorialCompra.objects.create(
                    compra=compra,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio
                )
            # Vaciar el carrito tras la creación de la compra
            carrito.items.all().delete()
    except Exception as e:
        logger.error("Error al registrar la compra: %s", e, exc_info=True)
        messages.error(request, "Error al registrar la compra. Inténtalo de nuevo.")
        return redirect(reverse("ver_carrito"))
    
    # Redirigir al usuario a la página de pago de Mercado Pago
    return redirect(init_point)

@require_http_methods(["GET"])
def ver_historial_compras(request: HttpRequest) -> HttpResponse:
    """
    Muestra el historial de compras del usuario.
    """
    compras = Compra.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, "compras/historial.html", {"compras": compras})