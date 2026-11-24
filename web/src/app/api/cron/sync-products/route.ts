import { NextRequest, NextResponse } from "next/server";
import { runFullProductSync } from "@/lib/sync";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const cronSecret = process.env.CRON_SECRET?.trim();
  const authHeader = req.headers.get("authorization") || "";

  if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ ok: false, message: "Unauthorized" }, { status: 401 });
  }

  const result = await runFullProductSync("cron");
  return NextResponse.json(result, { status: result.ok ? 200 : 500 });
}
