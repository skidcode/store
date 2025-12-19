import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "../store";
import type { User, Product, Cart, Order } from "@types";

const baseUrl = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");

export const apiSlice = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl,
    prepareHeaders: (headers, { getState }) => {
      const state = getState() as RootState;
      const token =
        state.auth.token ||
        (typeof window !== "undefined"
          ? localStorage.getItem("token")
          : null);
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      headers.set("Content-Type", "application/json");
      return headers;
    },
  }),
  tagTypes: ["Products", "Cart", "Orders"],
  endpoints: (builder) => ({
    // Auth
    login: builder.mutation<{ access: string; refresh?: string }, { username: string; password: string }>({
      query: (body) => ({
        url: "/auth/login/",
        method: "POST",
        body,
      }),
    }),
    register: builder.mutation<{ detail: string }, { username: string; password: string; email: string }>({
      query: (body) => ({
        url: "/auth/register/",
        method: "POST",
        body,
      }),
    }),
    me: builder.query<User, void>({
      query: () => "/auth/me/",
    }),

    // Products
    getProducts: builder.query<{ results?: Product[]; count?: number } | Product[], string | void>({
      query: (queryString) => `/products/${queryString ? `?${queryString}` : ""}`,
      providesTags: ["Products"],
    }),
    getProduct: builder.query<Product, number | string>({
      query: (id) => `/products/${id}/`,
      providesTags: (_result, _err, id) => [{ type: "Products", id }],
    }),

    // Cart
    getCart: builder.query<Cart, void>({
      query: () => "/cart/",
      providesTags: ["Cart"],
    }),
    addToCart: builder.mutation<
      { detail: string },
      { product_id: number; quantity: number }
    >({
      query: (body) => ({
        url: "/cart/add/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Cart"],
    }),
    updateCartItem: builder.mutation<
      { detail: string },
      { itemId: number; quantity: number }
    >({
      query: ({ itemId, quantity }) => ({
        url: `/cart/${itemId}/update/`,
        method: "PATCH",
        body: { quantity },
      }),
      invalidatesTags: ["Cart"],
    }),
    removeCartItem: builder.mutation<{ detail: string }, number>({
      query: (itemId) => ({
        url: `/cart/${itemId}/remove/`,
        method: "DELETE",
      }),
      invalidatesTags: ["Cart"],
    }),
    clearCart: builder.mutation<{ detail: string }, void>({
      query: () => ({
        url: "/cart/clear/",
        method: "DELETE",
      }),
      invalidatesTags: ["Cart"],
    }),

    // Orders
    createOrder: builder.mutation<Order, { shipping_address: string }>({
      query: (body) => ({
        url: "/my/orders/create_order/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Cart", "Orders"],
    }),
    payOrder: builder.mutation<
      { checkout_url: string; session_id: string },
      { orderId: number; success_url?: string; cancel_url?: string }
    >({
      query: ({ orderId, ...body }) => ({
        url: `/my/orders/${orderId}/pay/`,
        method: "POST",
        body,
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useMeQuery,
  useGetProductsQuery,
  useGetProductQuery,
  useGetCartQuery,
  useAddToCartMutation,
  useUpdateCartItemMutation,
  useRemoveCartItemMutation,
  useClearCartMutation,
  useCreateOrderMutation,
  usePayOrderMutation,
} = apiSlice;
