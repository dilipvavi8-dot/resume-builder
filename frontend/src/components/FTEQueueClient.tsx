"use client";

import { ArrowUpRight, Check, Inbox, X } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "./AppShell";
import { EmptyState, Score } from "./Ui";
import { api } from "@/lib/api";

type Approval = { id: number; job_id: number; score: number; status: string; reason: string; company: string; title: string; location: string; source_url: string };

export function FTEQueueClient() {
  const [items, setItems] = useState<Approval[]>([]);
  const [message, setMessage] = useState("");
  const load = () => api<Approval[]>("/fte-approvals").then(setItems).catch((error) => setMessage(error.message));
  useEffect(() => { void load(); }, []);
  const decide = async (id: number, decision: "approved" | "rejected") => {
    try { await api(`/fte-approvals/${id}/decision`, { method: "POST", body: JSON.stringify({ decision }) }); setMessage(decision === "approved" ? "Marked ready for your manual application." : "Role archived from the review queue."); await load(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Unable to update this review."); }
  };
  const pending = items.filter((item) => item.status === "pending");
  return <AppShell title="Full-time review queue" eyebrow="Approval required"><section className="rounded-[2rem] border border-amber-200/20 bg-amber-200/10 p-7 md:p-9"><div className="flex items-start gap-4"><Inbox className="mt-1 text-amber-100" /><div><p className="text-[10px] uppercase tracking-[0.3em] text-amber-100/70">Human decision point</p><h2 className="mt-3 font-display text-4xl italic">High-match full-time roles wait for your decision.</h2><p className="mt-4 max-w-2xl text-sm leading-7 text-amber-50/75">Approval only marks the role ready for you to apply. Rolecraft will not store portal credentials, sign in, or submit applications.</p></div></div></section>{message && <p className="mt-6 rounded-2xl border border-[#89aacc]/30 bg-[#89aacc]/10 px-5 py-3 text-sm text-[#c7dbef]">{message}</p>}<section className="mt-7 space-y-5">{!pending.length ? <EmptyState title="No approvals waiting." text="FTE listings scoring 90% or higher appear here after a feed refresh or re-analysis." /> : pending.map((item) => <article key={item.id} className="grid gap-5 rounded-[2rem] border border-stroke bg-surface p-7 md:grid-cols-[auto_1fr_auto] md:items-center"><Score value={item.score} /><div><p className="text-[10px] uppercase tracking-[0.25em] text-muted">{item.location || "Location not provided"}</p><h2 className="mt-2 font-display text-3xl italic">{item.title}</h2><p className="mt-2 text-sm text-white/75">{item.company}</p></div><div className="flex flex-wrap gap-2 md:justify-end"><a href={item.source_url} target="_blank" rel="noreferrer" className="flex items-center gap-2 rounded-full border border-stroke px-4 py-2 text-xs">Review source <ArrowUpRight size={13} /></a><button onClick={() => void decide(item.id, "rejected")} className="flex items-center gap-2 rounded-full border border-stroke px-4 py-2 text-xs text-muted"><X size={13} /> Archive</button><button onClick={() => void decide(item.id, "approved")} className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-xs text-black"><Check size={13} /> Approve</button></div></article>)}</section></AppShell>;
}
