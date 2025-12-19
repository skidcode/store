# Roadmap del Proyecto — Store / E-commerce

Este roadmap reúne todas las tareas del proyecto clasificadas por módulos.  
Cada ítem representa una funcionalidad concreta del backend, frontend o DevOps.  
Solo debés marcar cada casilla a medida que avances.

---

# 1. Usuarios & Autenticación (Backend)

- [x] Crear app `accounts`
- [x] Registro de usuarios con email y password
- [x] Login con JWT (SimpleJWT)
- [x] Refresh token
- [ ] Endpoint para actualizar datos del usuario
- [ ] Endpoint para cambiar password
- [ ] Endpoint para gestionar direcciones del usuario
- [ ] Roles (admin / user)
- [ ] Endpoint para listar usuarios (solo admin)

---

# 2. Productos (Backend)

- [x] Crear app `products`
- [x] Modelo de producto
- [x] Categorías de productos
- [x] Slug automático
- [x] Imagen de producto (Pillow)
- [x] CRUD básico de productos
- [ ] Búsqueda por nombre
- [ ] Filtros por categoría
- [ ] Filtros por precio (min / max)
- [ ] Filtro por disponibilidad (stock > 0)
- [ ] Paginación
- [ ] CRUD completo de productos para admin

---

# 3. Carrito (Backend)

- [x] Modelo `Cart`
- [x] Modelo `CartItem`
- [x] Obtener carrito del usuario
- [x] Agregar producto al carrito
- [x] Actualizar cantidad
- [x] Eliminar item
- [x] Vaciar carrito
- [ ] Carrito anónimo (opcional)

---

# 4. Órdenes (Backend)

- [x] Crear orden desde el carrito
- [x] Copiar productos del carrito a `OrderItem`
- [x] Estado inicial: `PENDING`
- [x] Cancelar orden (solo si está PENDING)
- [x] Listar órdenes del usuario
- [x] Ver detalle de una orden individual
- [ ] Restar stock después del pago
- [x] Estado SHIPPED
- [x] Estado DELIVERED
- [ ] Reembolsos (opcional)
- [ ] Historial completo de cambios de estado (opcional)

---

# 5. Administración (Backend)

- [x] Listar todas las órdenes (admin)
- [x] Filtros avanzados con django-filter
- [x] Filtros por usuario
- [x] Cambiar estado de una orden (admin)
- [ ] Exportar órdenes a CSV / Excel
- [ ] Dashboard admin:
  - [x] Ventas por día
  - [ ] Productos más vendidos
  - [x] Órdenes por estado

---

# 6. Pagos (Stripe)

- [x] Crear sesión de pago (Stripe Checkout)
- [ ] Redirección automática al checkout (frontend)
- [x] Webhook de Stripe
- [x] Verificar firma del webhook
- [x] Marcar orden como `PAID`
- [x] Guardar fecha `paid_at`
- [x] Guardar `stripe_session_id`
- [ ] Página de pago exitoso (frontend)
- [ ] Página de pago fallido (frontend)

---

# 7. Frontend (React)

### Autenticación

- [ ] Registro
- [ ] Login
- [ ] Guardar token JWT
- [ ] Logout
- [ ] Proteger rutas privadas

### Productos

- [ ] Listado de productos
- [ ] Filtros
- [ ] Buscador
- [ ] Detalle de producto
- [ ] Imágenes

### Carrito

- [ ] Ver carrito
- [ ] Agregar productos
- [ ] Actualizar cantidad
- [ ] Eliminar item
- [ ] Total dinámico
- [ ] Botón de “proceder al pago”

### Órdenes

- [ ] Listado de órdenes del usuario
- [ ] Detalle de orden
- [ ] Cancelar orden
- [ ] Mostrar estado en tiempo real

### Admin (Frontend)

- [ ] Lista global de órdenes
- [ ] Filtros
- [ ] Cambiar estado
- [ ] Panel de productos

---

# 8. DevOps

- [ ] Dockerizar backend
- [ ] Dockerizar frontend
- [ ] Archivo `docker-compose.yml`
- [ ] Variables de entorno .env
- [ ] Deployment backend (Railway / Render / AWS)
- [ ] Deployment frontend (Netlify / Vercel)
- [ ] CI/CD con GitHub Actions

---

# 9. Extras Futuro

- [ ] Wishlist / Favoritos
- [ ] Sistema de cupones
- [ ] Opiniones / valoraciones de productos
- [ ] Emails automáticos (orden creada / pagada)
- [ ] Multi-moneda
- [ ] Multi-idioma
- [ ] API pública con rate limiting
- [ ] App móvil (React Native)

---

# Notas

Este roadmap se actualiza a medida que se completa trabajo en backend y frontend.  
Usarlo como referencia para nuevas tareas, issues en GitHub o proyectos Kanban.
