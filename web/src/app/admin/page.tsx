import { AdminClient } from "@/components/AdminClient";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { isAdminAuthenticated } from "@/lib/auth";
import { getClickStats, getProducts, getTravelDeals } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function AdminPage() {
  const authed = await isAdminAuthenticated();
  const [stats, products, travelDeals] = authed
    ? await Promise.all([getClickStats(), getProducts(), getTravelDeals()])
    : [
        {
          connected: false,
          totalProducts: 0,
          totalTravelDeals: 0,
          shopeeClicks: 0,
          lazadaClicks: 0,
          travelClicks: 0,
        },
        [],
        [],
      ];

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <AdminClient
          initialAuthed={authed}
          initialStats={stats}
          initialProducts={products}
          initialTravelDeals={travelDeals}
        />
      </main>
      <Footer />
    </div>
  );
}
