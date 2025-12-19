# Store — Plataforma E-commerce Full Stack

Una aplicación moderna de comercio electrónico construida con **Django REST Framework (backend)** y **React (frontend)**.  
Incluye autenticación, gestión de productos, carrito de compras, órdenes y pagos con Stripe.

**Disponible en:**

## Readme

➤ English version:  
[English](README.md)

## Roadmap

➤ Full roadmap is available here:  
[Español](ROADMAP.md)

➤ Spanish version:  
[English](ROADMAP.es.md)

---

## Funcionalidades

### Autenticación

- Autenticación JWT (login, registro, refresh)
- Rutas protegidas (backend y frontend)
- Roles de administrador y usuario estándar (planificado)

### Productos

- Catálogo de productos con categorías
- Slugs, imágenes, precio y manejo de stock
- Filtros, búsqueda y paginación (planificado)

### Carrito de Compras

- Agregar / actualizar / eliminar productos
- Carrito asociado al usuario autenticado
- Creación automática del carrito

### Órdenes

- Crear orden desde el carrito
- Snapshot de items de la orden (precio unitario + cantidad)
- Cancelar orden (si está pendiente)
- Listado de órdenes para administrador con filtros

### Pagos (Stripe)

- Stripe Checkout (planificado)
- Webhook de Stripe para confirmar pagos (planificado)
- Actualización del estado de la orden a PAID (planificado)

### Funcionalidades de Administrador

- Listado global de órdenes (completado)
- Filtros usando django-filter (completado)
- Actualización de estado de órdenes (planificado)
- Dashboard de ventas (planificado)

---

## Arquitectura del Proyecto

```
Store/
+-- backend/               # Django + DRF backend
�   +-- accounts/          # L�gica de autenticaci�n
�   +-- products/          # Modelos y endpoints de productos
�   +-- orders/            # Carrito, �rdenes, filtros admin
�   +-- backend/           # Configuraci�n principal y URLs
�   +-- ...
+-- frontend/              # React (Next.js + Tailwind)
    +-- src/
        +-- app/
        +-- components/
        +-- styles/

README.md
README.es.md
ROADMAP.md
ROADMAP.es.md
```

### **Frontend**

- React con Next.js (App Router)
- Tailwind CSS para estilos
- Estado con Context API o Zustand/Redux
- Comunicación con backend vía API REST

### **Backend**

- Django 5
- Django REST Framework
- Autenticación JWT (SimpleJWT)
- django-filter
- Pillow

### **Base de Datos**

- SQLite (desarrollo)
- PostgreSQL (recomendado para producción)

### **Servicios Externos**

- Stripe para procesamiento de pagos

---

## Configuración Backend (local)

- Python 3.11+ con virtualenv recomendado.
- Instalar dependencias: `pip install -r backend/requirements.txt`
- Variables de entorno: crea `backend/.env` con `STRIPE_SECRET_KEY` y `STRIPE_WEBHOOK_SECRET`.
- Ejecutar servidor: `cd backend && python manage.py runserver`


