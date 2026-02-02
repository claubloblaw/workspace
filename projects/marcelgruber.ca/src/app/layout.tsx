import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Marcel Gruber - Enterprise Web & AI Systems Architect",
  description: "11 years shipping enterprise web. 3x Sitecore Technology MVP. Building AI systems that actually work. Calgary-based architect specializing in Sitecore, .NET, WordPress, and agentic AI.",
  keywords: "Marcel Gruber, Sitecore MVP, Enterprise Web Development, AI Consultant, Agentic AI, WordPress Development, .NET Developer, Calgary",
  authors: [{ name: "Marcel Gruber" }],
  openGraph: {
    title: "Marcel Gruber - Enterprise Web & AI Systems Architect",
    description: "I don't just talk about AI — I build with it. 11 years shipping enterprise web, now making AI actually work for businesses.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
