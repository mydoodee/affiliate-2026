import { AdminClient } from "@/components/AdminClient";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { isAdminAuthenticated } from "@/lib/auth";
import { getClickStats, getProducts, getTravelDeals } from "@/lib/db";
import { getSyncStatus } from "@/lib/sync";

export const dynamic = "force-dynamic";

export default async function AdminPage() {
  const authed = await isAdminAuthenticated();
  const [stats, products, travelDeals, syncStatus] = authed
    ? await Promise.all([
        getClickStats(),
        getProducts(),
        getTravelDeals(),
        getSyncStatus(),
      ])
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
        {
          shopeeConfigured: false,
          lazadaConfigured: false,
          lastSyncAt: null,
          lastSyncMessage: null,
        },
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
          initialSyncStatus={syncStatus}
        />
      </main>
      <Footer />
    </div>
  );
}
