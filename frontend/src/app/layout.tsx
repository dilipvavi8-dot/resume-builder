import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rolecraft | Local Career Workspace",
  description: "Find stronger-fit roles, understand the gap, and craft a better resume locally.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
