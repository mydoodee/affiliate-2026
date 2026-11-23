import { AdminClient } from "@/components/AdminClient";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { getClickStats, getProducts } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function AdminPage() {
  const [stats, products] = await Promise.all([getClickStats(), getProducts()]);
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <AdminClient initialStats={stats} initialProducts={products} />
      </main>
      <Footer />
    </div>
  );
}
