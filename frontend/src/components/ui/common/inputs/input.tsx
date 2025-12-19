"use client";

import clsx from "clsx";
import type { InputHTMLAttributes } from "react";

type Props = InputHTMLAttributes<HTMLInputElement>;

export function Input({ className, ...rest }: Props) {
  return (
    <input
      className={clsx(
        "w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200",
        className
      )}
      {...rest}
    />
  );
}
