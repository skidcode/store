# Store — Full Stack E-commerce Platform

A modern e-commerce application built with **Django REST Framework (backend)** and **React (frontend)**.  
Includes authentication, product management, shopping cart, orders, and Stripe payments.

**Available in:**  
[English](README.md) · [Español](README.es.md)

---

## Features

### Authentication

- JWT authentication (login, register, refresh)
- Protected routes (backend & frontend)
- Admin and standard user roles (planned)

### Products

- Product catalog with categories
- Slugs, images, price, stock management
- Filtering, search, pagination (planned)

### Shopping Cart

- Add / update / remove items
- Cart linked to authenticated user
- Automatic creation of user cart

### Orders

- Create order from cart
- Order items snapshot (unit price + quantity)
- Cancel order (if pending)
- Admin order listing with filtering

### Payments (Stripe)

- Stripe Checkout (planned)
- Stripe webhook to confirm payments (planned)
- Order status update to PAID (planned)

### Admin Features

- Global order listing (completed)
- Filters using django-filter (completed)
- Order status update (planned)
- Sales dashboard (planned)

---

## Project Architecture

Store/
│
├── backend/ # Django + DRF backend
│ ├── accounts/ # Authentication logic
│ ├── products/ # Product models & endpoints
│ ├── orders/ # Cart, orders, admin filters
│ ├── backend/ # Core settings & URLs
│ └── ...
│
├── frontend/ # React (Vite or CRA)
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

- React (Vite recommended)
- React Router
- Context API or Zustand/Redux
- Uses REST API to communicate with backend

### **Backend**

- Django 5
- Django REST Framework
- JWT Auth (SimpleJWT)
- django-filter
- Pillow

### **Database**

- SQLite (development)
- PostgreSQL (production recommended)

### **External Services**

- Stripe for payment processing

---
