"use client";

import { SaltProvider } from "@salt-ds/core";

export default function SaltAppProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SaltProvider density="medium" mode="light">
      {children}
    </SaltProvider>
  );
}
