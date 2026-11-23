import { NextRequest, NextResponse } from "next/server";
import {
  ADMIN_COOKIE_NAME,
  signSessionToken,
  verifyCredentials,
} from "@/lib/auth";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const { username, password } = await req.json();
    if (!verifyCredentials(String(username || ""), String(password || ""))) {
      return NextResponse.json(
        { ok: false, message: "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง" },
        { status: 401 }
      );
    }
    const token = signSessionToken(String(username).trim());
    const res = NextResponse.json({ ok: true });
    res.cookies.set(ADMIN_COOKIE_NAME, token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 7 * 24 * 60 * 60,
    });
    return res;
  } catch {
    return NextResponse.json({ ok: false, message: "คำขอไม่ถูกต้อง" }, { status: 400 });
  }
}
