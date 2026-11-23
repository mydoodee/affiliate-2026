import { NextResponse } from "next/server";
import { isAdminAuthenticated } from "@/lib/auth";
import { initAndSeedDb } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function POST() {
  if (!(await isAdminAuthenticated())) {
    return NextResponse.json({ ok: false, message: "กรุณาเข้าสู่ระบบแอดมินก่อน" }, { status: 401 });
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
