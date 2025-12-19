"use client";

import Link from "next/link";
import {  Button, Card } from "@components/ui";
import { useGetProductsQuery } from "@lib/services/apiSlice";

export default function HomePage() {
  const { data, isLoading, isError } = useGetProductsQuery();
  const products = Array.isArray(data) ? data : data?.results || [];

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-5xl px-4 py-10">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-500">Tienda</p>
            <h1 className="text-2xl font-semibold text-slate-900">Productos</h1>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" as="a" href="/login">
              Ingresar
            </Button>
            <Button as="a" href="/register">
              Crear cuenta
            </Button>
          </div>
        </header>

        {isLoading && <p className="text-slate-500">Cargando productos...</p>}
        {isError && <p className="text-red-600">Error al cargar productos.</p>}

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <Card key={product.id} className="flex flex-col">
              <div className="flex-1 p-4">
                <p className="text-sm text-slate-500">{product.category?.name || "Sin categoría"}</p>
                <h2 className="mt-1 text-lg font-semibold text-slate-900">{product.name}</h2>
                <p className="mt-2 text-slate-700 line-clamp-3">{product.description}</p>
              </div>
              <div className="border-t border-slate-100 p-4">
                <p className="text-lg font-semibold text-slate-900">${product.price}</p>
                <div className="mt-3 flex gap-2">
                  <Link href={`/product/${product.id}`} className="flex-1">
                    <Button variant="secondary" className="w-full">
                      Ver detalle
                    </Button>
                  </Link>
                  <Link href="/cart">
                    <Button variant="ghost">Carrito</Button>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}
