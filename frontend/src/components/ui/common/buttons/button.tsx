"use client";

import clsx from "clsx";
import type {
  AnchorHTMLAttributes,
  ButtonHTMLAttributes,
  ElementType,
  ReactNode,
} from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "sm" | "md" | "lg";
type As = "button" | "a";

type ButtonProps<T extends As> = {
  as?: T;
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
  className?: string;
} & (T extends "a"
  ? AnchorHTMLAttributes<HTMLAnchorElement>
  : ButtonHTMLAttributes<HTMLButtonElement>);

const base =
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-60 disabled:cursor-not-allowed";

const variants: Record<ButtonVariant, string> = {
  primary: "bg-slate-900 text-white hover:bg-slate-800 focus-visible:outline-slate-900",
  secondary:
    "bg-white text-slate-900 border border-slate-200 hover:bg-slate-50 focus-visible:outline-slate-200",
  ghost: "text-slate-900 hover:bg-slate-100 focus-visible:outline-slate-200",
};

const sizes: Record<ButtonSize, string> = {
  sm: "text-sm px-3 py-2",
  md: "text-sm px-4 py-2.5",
  lg: "text-base px-5 py-3",
};

export function Button<T extends As = "button">({
  as,
  variant = "primary",
  size = "md",
  className,
  children,
  ...rest
}: ButtonProps<T>) {
  const Comp = (as || "button") as ElementType;

  return (
    <Comp className={clsx(base, variants[variant], sizes[size], className)} {...rest}>
      {children}
    </Comp>
  );
}
