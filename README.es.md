# Store — Plataforma E-commerce Full Stack

Una aplicación moderna de comercio electrónico construida con **Django REST Framework (backend)** y **React (frontend)**.  
Incluye autenticación, gestión de productos, carrito de compras, órdenes y pagos con Stripe.

**Disponible en:**

## Readme

[English](README.md) · [Español](README.es.md)

## Roadmap

➤ Full roadmap is available here:  
[ROADMAP.md](ROADMAP.md)

➤ Spanish version:  
[ROADMAP.es.md](ROADMAP.es.md)

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

Store/
│
├── backend/ # Django + DRF backend
│ ├── accounts/ # Lógica de autenticación
│ ├── products/ # Modelos y endpoints de productos
│ ├── orders/ # Carrito, órdenes, filtros admin
│ ├── backend/ # Configuración principal y URLs
│ └── ...
│
├── frontend/ # React (Vite o CRA)
│ ├── src/
│ ├── components/
│ ├── pages/
│ └── ...
│
├── README.md
├── README.es.md
├── ROADMAP.md
└── ROADMAP.es.md

### **Frontend**

- React (recomendado con Vite)
- React Router
- Context API o Zustand/Redux
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
