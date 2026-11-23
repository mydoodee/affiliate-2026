import { NextRequest, NextResponse } from "next/server";
import { initAndSeedDb } from "@/lib/db";

export const dynamic = "force-dynamic";

function checkAdmin(req: NextRequest): boolean {
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) return true; // If no ADMIN_PASSWORD set yet, allow initial setup
  const supplied = req.headers.get("x-admin-password") || "";
  return supplied === expected;
}

export async function POST(req: NextRequest) {
  if (!checkAdmin(req)) {
    return NextResponse.json({ ok: false, message: "รหัสผ่านแอดมินไม่ถูกต้อง" }, { status: 401 });
  }
  try {
    const result = await initAndSeedDb();
    return NextResponse.json(result, { status: result.ok ? 200 : 400 });
  } catch (err) {
    return NextResponse.json(
      { ok: false, message: err instanceof Error ? err.message : "Database error" },
      { status: 500 }
    );
  }
}
