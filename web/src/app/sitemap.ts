import type { MetadataRoute } from "next";
import { getProducts } from "@/lib/db";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = "https://mybabman-picks.vercel.app";
  const products = await getProducts();

  return [
    { url: baseUrl, lastModified: new Date(), changeFrequency: "daily", priority: 1 },
    { url: `${baseUrl}/travel`, lastModified: new Date(), changeFrequency: "daily", priority: 0.9 },
    ...products.map((p) => ({
      url: `${baseUrl}/p/${encodeURIComponent(p.code)}`,
      lastModified: new Date(),
      changeFrequency: "weekly" as const,
      priority: 0.8,
    })),
  ];
}
