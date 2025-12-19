import type { Product } from "./product.type";

export type OrderItem = {
  id: number;
  order: number;
  product: Product;
  quantity: number;
  unit_price: number;
};

export type Order = {
  id: number;
  user: number;
  status: "PENDING" | "PAID" | "CANCELLED" | "SHIPPED" | "DELIVERED";
  total_amount: string;
  shipping_address: string;
  created_at: string;
  paid_at: string | null;
  items: OrderItem[];
  stripe_session_id?: string;
};
