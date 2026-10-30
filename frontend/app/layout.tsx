import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "BTC Signal & Paper Trading Engine",
  description: "A keyless Bitcoin signal research dashboard with local paper execution."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
