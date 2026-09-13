import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "FilmFund Africa — De l'idée au financement de votre projet audiovisuel",
  description:
    "FilmFund Africa aide les réalisateurs, scénaristes et producteurs africains à structurer leurs projets, générer leurs documents avec l'IA et trouver des financements adaptés.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className="antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
