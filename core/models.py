from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=17, blank=True) # validators should be a list
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-date_joined"]

class Genero(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Género"
        verbose_name_plural = "Géneros"
        ordering = ["nombre"]

class Material(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ["nombre"]

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    mas_vendido = models.BooleanField(default=False)
    es_destacado = models.BooleanField(default=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

class Multimedia(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='multimedia')
    archivo = models.FileField(upload_to='productos/multimedia/')
    tipo = models.CharField(max_length=10, choices=[('imagen', 'Imagen'), ('video', 'Video')])
    
    def __str__(self):
        return f"{self.tipo} de {self.producto.nombre}"

class Realista(Producto):
    longitud = models.DecimalField(max_digits=5, decimal_places=2)
    diametro = models.DecimalField(max_digits=5, decimal_places=2)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Realista"
        verbose_name_plural = "Realistas"

class Vibrador(Producto):
    longitud = models.DecimalField(max_digits=5, decimal_places=2)
    diametro = models.DecimalField(max_digits=5, decimal_places=2)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    pilas = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Vibrador"
        verbose_name_plural = "Vibradores"

class Lubricante(Producto):
    tipo = models.CharField(max_length=50)
    base = models.CharField(max_length=50)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Lubricante"
        verbose_name_plural = "Lubricantes"

class Digital(Producto):
    url_pago = models.URLField()

    class Meta:
        verbose_name = "Digital"
        verbose_name_plural = "Digitales"

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="carrito")

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Carrito de {self.usuario.email}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en el carrito de {self.carrito.usuario.email}"

class Estado(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Estado de Pedido"
        verbose_name_plural = "Estados de Pedido"
        ordering = ["nombre"]

class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="compras")
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Compra #{self.id} de {self.usuario.email} - Estado: {self.estado}"
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha"]

class HistorialCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Compra #{self.compra.id}"

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()

    def __str__(self):
        return f"Mensaje de {self.nombre} - {self.email}"

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ["-id"]

class Testimonio(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    imagen = models.ImageField(upload_to='testimonios/', blank=True)
    testimonio = models.TextField()

    def __str__(self):
        return f"Testimonio de {self.nombre} - {self.email}"

    class Meta:
        verbose_name = "Testimonio"
        verbose_name_plural = "Testimonios"
        ordering = ["-id"]