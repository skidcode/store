import type { Category } from "./category.type";

export type Product = {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: number;
  stock: number;
  category: Category | null;
  image?: string;
};
