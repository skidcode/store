"use client";

import { store } from "@lib";
import { Provider } from "react-redux";

type Props = {
  children: React.ReactNode;
};

export function Providers({ children }: Props) {
  return <Provider store={store}>{children}</Provider>;
}
