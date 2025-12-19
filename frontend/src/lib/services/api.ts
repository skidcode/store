const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");

const getAuthHeader = () => {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

async function request<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeader(),
    ...(options.headers || {}),
  } as Record<string, string>;

  const res = await fetch(url, { ...options, headers, credentials: "include" });

  if (!res.ok) {
    let detail: any;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    throw new Error(
      typeof detail === "string" ? detail : detail?.detail || "Request failed"
    );
  }

  if (res.status === 204) {
    return null as T;
  }

  return (await res.json()) as T;
}

export const api = {
  // Auth
  login: (payload: { username: string; password: string }) =>
    request("/auth/login/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  register: (payload: Record<string, any>) =>
    request("/auth/register/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  me: () => request("/auth/me/"),

  // Products
  getProducts: (params: URLSearchParams = new URLSearchParams()) =>
    request(`/products/?${params.toString()}`),
  getProduct: (id: number | string) => request(`/products/${id}/`),

  // Cart
  getCart: () => request("/cart/"),
  addToCart: (payload: { product_id: number; quantity: number }) =>
    request("/cart/add/", { method: "POST", body: JSON.stringify(payload) }),
  updateCartItem: (itemId: number, quantity: number) =>
    request(`/cart/${itemId}/update/`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),
  removeCartItem: (itemId: number) =>
    request(`/cart/${itemId}/remove/`, { method: "DELETE" }),
  clearCart: () => request("/cart/clear/", { method: "DELETE" }),

  // Orders
  createOrder: (payload: { shipping_address: string }) =>
    request("/my/orders/create_order/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  payOrder: (orderId: number, payload: { success_url?: string; cancel_url?: string }) =>
    request(`/my/orders/${orderId}/pay/`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
