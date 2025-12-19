import type { Product } from "./product.type";

export type CartItem = {
  id: number;
  cart: number;
  product: Product;
  quantity: number;
};

export type Cart = {
  id: number;
  user: number;
  items: CartItem[];
};
