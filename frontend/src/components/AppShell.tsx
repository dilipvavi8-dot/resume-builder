"use client";

import { Activity, BriefcaseBusiness, FileSearch, Files, LayoutDashboard, Menu, ShieldCheck, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { BrandMark } from "./BrandMark";
import { NotificationBell } from "./NotificationBell";

const links = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/jobs", label: "Job feed", icon: BriefcaseBusiness },
  { href: "/manual-jd", label: "Analyze JD", icon: FileSearch },
  { href: "/resumes", label: "Resumes", icon: Files },
  { href: "/tracker", label: "Tracker", icon: Sparkles },
  { href: "/monitor", label: "Monitor", icon: Activity },
  { href: "/approvals", label: "Review queue", icon: ShieldCheck },
];

export function AppShell({ title, eyebrow, children, action }: { title: string; eyebrow: string; children: React.ReactNode; action?: React.ReactNode }) {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen bg-bg text-text-primary">
      <aside className={`fixed inset-y-0 left-0 z-50 w-72 border-r border-stroke bg-bg/95 p-6 backdrop-blur-xl transition-transform lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="mb-12 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3"><BrandMark /><span className="font-display text-2xl italic">Rolecraft</span></Link>
          <button className="lg:hidden" onClick={() => setOpen(false)} aria-label="Close menu"><X size={20} /></button>
        </div>
        <nav className="space-y-2">
          {links.map(({ href, label, icon: Icon }) => (
            <Link key={href} href={href} onClick={() => setOpen(false)} className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition ${path === href ? "bg-white text-black" : "text-muted hover:bg-surface hover:text-white"}`}>
              <Icon size={17} /> {label}
            </Link>
          ))}
        </nav>
        <div className="absolute inset-x-6 bottom-6 rounded-3xl border border-stroke bg-surface p-5">
          <p className="mb-2 text-[10px] uppercase tracking-[0.3em] text-muted">Local first</p>
          <p className="text-sm leading-6 text-white/80">Your resume, job data, and generated files stay on this machine.</p>
        </div>
      </aside>
      <main className="min-h-screen lg:pl-72">
        <header className="sticky top-0 z-40 flex items-center justify-between border-b border-stroke bg-bg/80 px-5 py-4 backdrop-blur-xl md:px-10 lg:px-12">
          <div className="flex items-center gap-4">
            <button className="rounded-full border border-stroke p-2 lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu"><Menu size={18} /></button>
            <div><p className="text-[10px] uppercase tracking-[0.3em] text-muted">{eyebrow}</p><h1 className="font-display text-2xl italic md:text-3xl">{title}</h1></div>
          </div>
          <div className="flex items-center gap-3"><NotificationBell />{action}</div>
        </header>
        <div className="p-5 md:p-10 lg:p-12">{children}</div>
      </main>
    </div>
  );
}
