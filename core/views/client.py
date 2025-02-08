import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods

# Configuración del logger para registrar eventos o errores en la vista
logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def index(request):

    context = {}  # Diccionario de contexto para pasar variables a la plantilla html

    if request.method == "POST":
        try:
            # form = MiFormulario(request.POST)
            # if form.is_valid():
            #     form.save()
            #     messages.success(request, "Datos guardados correctamente.")
            #     return redirect(reverse("index"))
            # else:
            #     messages.error(request, "Se encontraron errores en el formulario.")
            pass
        except Exception as e:
            # Registro del error con detalle y traza completa para facilitar la depuración
            logger.error("Error al procesar la petición POST en la vista index: %s", e, exc_info=True)

            messages.error(request, "Ocurrió un error interno. Por favor, inténtalo de nuevo más tarde.")
            return redirect(reverse("index"))

    # Ejemplo de agregar datos al contexto para la plantilla
    context['data'] = "Información de ejemplo"

    return render(request, "core/client/index.html", context)