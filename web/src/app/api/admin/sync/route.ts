import { NextResponse } from "next/server";
import { isAdminAuthenticated } from "@/lib/auth";
import { getSyncStatus, runFullProductSync } from "@/lib/sync";

export const dynamic = "force-dynamic";

export async function GET() {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "Unauthorized" }, { status: 401 });
  }
  const status = await getSyncStatus();
  return NextResponse.json({ ok: true, status });
}

export async function POST() {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "Unauthorized" }, { status: 401 });
  }
  const result = await runFullProductSync("manual");
  return NextResponse.json(result, { status: result.ok ? 200 : 400 });
}
