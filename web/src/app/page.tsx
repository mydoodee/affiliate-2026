import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { StorefrontClient } from "@/components/StorefrontClient";
import { getProducts } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const products = await getProducts();

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <StorefrontClient products={products} />
      </main>
      <Footer />
    </div>
  );
}
