"""Catálogo inicial de servicios y paquetes de THC Contabilidad.

Se siembra una sola vez, cuando se crea una base de datos nueva. El usuario
puede editar, eliminar o agregar cualquier entrada desde el POS. Los nombres se
usan como clave para que sembrar dos veces no duplique productos.
"""

from __future__ import annotations

# Cada entrada: nombre, categoría, tipo, precio en centavos, etiqueta de precio
# (por ejemplo "Desde"), destacado y descripción.
SERVICIOS: tuple[dict, ...] = (
    # ------------------------------------------------------------- Páginas web
    {
        "nombre": "Landing page básica", "categoria": "Páginas web",
        "precio_cents": 7_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Página sencilla para presentar un negocio, proyecto o servicio, con información de contacto.",
    },
    {
        "nombre": "Landing page personalizada", "categoria": "Páginas web",
        "precio_cents": 10_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Página con diseño personalizado, estructura visual propia y animaciones sutiles.",
    },
    {
        "nombre": "Página web de 3 secciones", "categoria": "Páginas web",
        "precio_cents": 13_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Sitio con inicio, servicios y contacto.",
    },
    {
        "nombre": "Página web de 5 secciones", "categoria": "Páginas web",
        "precio_cents": 18_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Sitio más completo con información, servicios, galería y contacto.",
    },
    {
        "nombre": "Página web empresarial", "categoria": "Páginas web",
        "precio_cents": 25_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Sitio personalizado para negocios que necesitan una presencia digital más completa.",
    },
    {
        "nombre": "Portafolio personal", "categoria": "Páginas web",
        "precio_cents": 10_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Sitio para mostrar proyectos, habilidades, experiencia y formas de contacto.",
    },
    {
        "nombre": "Página para emprendimiento", "categoria": "Páginas web",
        "precio_cents": 14_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Sitio para presentar una marca, sus productos o servicios y sus canales de contacto.",
    },
    # ----------------------------------------------- Catálogos y comercio digital
    {
        "nombre": "Menú digital con QR", "categoria": "Catálogos y comercio digital",
        "precio_cents": 5_500_000, "etiqueta": "", "destacado": 0,
        "notas": "Menú online para restaurantes, cafeterías y negocios de comida.",
    },
    {
        "nombre": "Catálogo básico", "categoria": "Catálogos y comercio digital",
        "precio_cents": 8_500_000, "etiqueta": "", "destacado": 0,
        "notas": "Catálogo digital para mostrar productos con imágenes, nombres y precios.",
    },
    {
        "nombre": "Catálogo por categorías", "categoria": "Catálogos y comercio digital",
        "precio_cents": 11_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Productos organizados en categorías para facilitar la navegación.",
    },
    {
        "nombre": "Catálogo con filtros", "categoria": "Catálogos y comercio digital",
        "precio_cents": 15_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Catálogo con opciones para filtrar y encontrar productos fácilmente.",
    },
    {
        "nombre": "Tienda virtual básica", "categoria": "Catálogos y comercio digital",
        "precio_cents": 20_000_000, "etiqueta": "", "destacado": 0,
        "notas": "Tienda online con productos y una estructura básica para recibir pedidos.",
    },
    {
        "nombre": "Carrito de compras", "categoria": "Catálogos y comercio digital",
        "precio_cents": 5_000_000, "etiqueta": "Adicional desde", "destacado": 0,
        "notas": "Funcionalidad para agregar y gestionar productos antes de realizar un pedido.",
    },
    {
        "nombre": "Pedidos por WhatsApp", "categoria": "Catálogos y comercio digital",
        "precio_cents": 2_500_000, "etiqueta": "Adicional desde", "destacado": 0,
        "notas": "Permite preparar pedidos y enviarlos directamente a WhatsApp.",
    },
    # ------------------------------------------------- Sistemas y funcionalidades
    {
        "nombre": "Formulario personalizado", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 2_500_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Formularios para recopilar información, solicitudes o mensajes.",
    },
    {
        "nombre": "Sistema de reservas básico", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 10_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Permite que los clientes soliciten citas o reservas.",
    },
    {
        "nombre": "Sistema de reservas avanzado", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 18_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Sistema con funcionalidades adicionales para gestionar reservas.",
    },
    {
        "nombre": "Panel administrativo", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 15_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Interfaz para administrar información y contenido de un sitio.",
    },
    {
        "nombre": "Sistema de inventario", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 18_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Herramienta para registrar y gestionar productos y existencias.",
    },
    {
        "nombre": "Registro de clientes", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 13_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Sistema para almacenar y consultar información de clientes.",
    },
    {
        "nombre": "Automatizaciones sencillas", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 6_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Automatización de tareas repetitivas y procesos básicos.",
    },
    {
        "nombre": "Integración de API", "categoria": "Sistemas y funcionalidades",
        "precio_cents": 7_000_000, "etiqueta": "Desde", "destacado": 0,
        "notas": "Conexión con servicios externos para ampliar las funcionalidades de un proyecto.",
    },
    # ---------------------------------------------------------------- Adicionales
    {
        "nombre": "Rediseño de página web", "categoria": "Adicionales",
        "precio_cents": 6_000_000, "etiqueta": "Desde", "destacado": 0, "notas": "",
    },
    {
        "nombre": "Modificación de secciones", "categoria": "Adicionales",
        "precio_cents": 1_500_000, "etiqueta": "Desde", "destacado": 0, "notas": "",
    },
    {
        "nombre": "Animaciones personalizadas", "categoria": "Adicionales",
        "precio_cents": 2_500_000, "etiqueta": "Desde", "destacado": 0, "notas": "",
    },
    {
        "nombre": "Integración de mapas", "categoria": "Adicionales",
        "precio_cents": 1_500_000, "etiqueta": "Desde", "destacado": 0, "notas": "",
    },
    {
        "nombre": "Integración de WhatsApp", "categoria": "Adicionales",
        "precio_cents": 1_000_000, "etiqueta": "Desde", "destacado": 0, "notas": "",
    },
    {
        "nombre": "Adaptación responsive", "categoria": "Adicionales",
        "precio_cents": 3_500_000, "etiqueta": "Desde", "destacado": 0, "notas": "",
    },
    {
        "nombre": "Carga de productos", "categoria": "Adicionales",
        "precio_cents": 100_000, "etiqueta": "por producto", "destacado": 0, "notas": "",
    },
    {
        "nombre": "Mantenimiento mensual", "categoria": "Adicionales",
        "precio_cents": 3_500_000, "etiqueta": "Desde", "destacado": 0, "notas": "",
    },
)

PAQUETES: tuple[dict, ...] = (
    {
        "nombre": "STARTER", "categoria": "Paquetes",
        "precio_cents": 9_000_000, "etiqueta": "", "destacado": 0,
        "notas": ("Una página de presentación · Información del negocio · "
                  "Diseño adaptable a celulares · Botón de contacto por WhatsApp · "
                  "Una ronda de ajustes"),
    },
    {
        "nombre": "BUSINESS", "categoria": "Paquetes",
        "precio_cents": 16_000_000, "etiqueta": "", "destacado": 1,
        "notas": ("Hasta 4 secciones · Diseño personalizado · Galería de imágenes · "
                  "Sección de servicios o tarifas · Integración de WhatsApp · "
                  "Dos rondas de ajustes"),
    },
    {
        "nombre": "PROFESSIONAL", "categoria": "Paquetes",
        "precio_cents": 25_000_000, "etiqueta": "", "destacado": 0,
        "notas": ("Hasta 6 secciones · Diseño personalizado · Galería y catálogo básico · "
                  "Animaciones · Formularios · Integraciones sencillas · "
                  "Dos rondas de ajustes"),
    },
)


def entries() -> tuple[dict, ...]:
    """Devuelve el catálogo completo: servicios individuales y paquetes."""
    servicios = ({**item, "tipo": "Servicio"} for item in SERVICIOS)
    paquetes = ({**item, "tipo": "Paquete"} for item in PAQUETES)
    return (*servicios, *paquetes)
