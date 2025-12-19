# Project Roadmap — Store / E-commerce

This roadmap outlines all planned and completed tasks for the project.  
Each item belongs to a module (Backend, Frontend, DevOps) and can be checked off as development progresses.

---

# 1. Users & Authentication (Backend)

- [x] Create `accounts` app
- [x] User registration (email + password)
- [x] Login using JWT (SimpleJWT)
- [x] Refresh token support
- [ ] Update user profile endpoint
- [ ] Change password endpoint
- [ ] User shipping addresses
- [ ] User roles (admin / user)
- [ ] User listing endpoint (admin only)

---

# 2. Products (Backend)

- [x] Create `products` app
- [x] Product model
- [x] Product categories
- [x] Auto-generated slugs
- [x] Product image field (Pillow)
- [x] Basic CRUD for products
- [ ] Search by product name
- [ ] Category filtering
- [ ] Price range filtering
- [ ] Availability filtering (stock > 0)
- [ ] Pagination support
- [ ] Full admin product management

---

# 3. Shopping Cart (Backend)

- [x] `Cart` model
- [x] `CartItem` model
- [x] Get user cart endpoint
- [x] Add product to cart
- [x] Update item quantity
- [x] Remove item
- [x] Clear cart endpoint
- [ ] Anonymous cart (optional)

---

# 4. Orders (Backend)

- [x] Create order from cart
- [x] Copy cart items into order items
- [x] Initial order status: `PENDING`
- [x] Cancel order (only if PENDING)
- [x] List user orders
- [x] Order detail endpoint
- [ ] Reduce stock after successful payment
- [x] Order status: `SHIPPED`
- [x] Order status: `DELIVERED`
- [ ] Refunds (optional)
- [ ] Order status history (optional)

---

# 5. Admin Features (Backend)

- [x] List all orders (admin)
- [x] Advanced filtering with django-filter
- [x] Filter by user
- [x] Update order status (admin)
- [ ] Export orders to CSV / Excel
- [ ] Admin dashboard:
  - [x] Sales per day
  - [ ] Best-selling products
  - [x] Orders by status

---

# 6. Payments (Stripe)

- [x] Create Stripe Checkout session
- [ ] Redirect to Stripe payment page (frontend)
- [x] Stripe webhook implementation
- [x] Verify webhook signature
- [x] Mark order as `PAID`
- [x] Save `paid_at` timestamp
- [x] Save `stripe_session_id`
- [ ] Successful payment page (frontend)
- [ ] Failed payment page (frontend)

---

# 7. Frontend (React)

### Authentication

- [ ] Registration page
- [ ] Login page
- [ ] Store JWT token (localStorage)
- [ ] Logout functionality
- [ ] Protected routes

### Product Catalog

- [ ] Product list page
- [ ] Filters (category, price, etc.)
- [ ] Search bar
- [ ] Product details page
- [ ] Product images

### Cart

- [ ] Cart page
- [ ] Add to cart
- [ ] Update item quantity
- [ ] Remove item
- [ ] Live totals
- [ ] Proceed to checkout button

### Orders

- [ ] List user orders
- [ ] Order detail view
- [ ] Cancel order
- [ ] Real-time status updates

### Admin Panel

- [ ] Global order list
- [ ] Filters and sorting
- [ ] Update order status
- [ ] Product management dashboard

---

# 8. DevOps

- [ ] Dockerize backend
- [ ] Dockerize frontend
- [ ] `docker-compose.yml`
- [ ] Environment variables using `.env`
- [ ] Backend deployment (Railway / Render / AWS)
- [ ] Frontend deployment (Netlify / Vercel)
- [ ] GitHub Actions CI/CD

---

# 9. Future Enhancements

- [ ] Wishlist / Favorites
- [ ] Discount coupon system
- [ ] Product reviews and ratings
- [ ] Automated transactional emails
- [ ] Multi-currency support
- [ ] Multi-language support
- [ ] Public API with rate limiting
- [ ] Mobile app (React Native)

---

# Notes

This roadmap evolves as backend and frontend development progresses.  
Use it to create tasks, GitHub issues, or Kanban workboards.
