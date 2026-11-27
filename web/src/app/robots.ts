import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: ["/", "/travel", "/p/"],
        disallow: ["/api/", "/go/"],
      },
    ],
    sitemap: "https://app.growkub.com/sitemap.xml",
  };
}
