"use client";

import { Activity, CheckCircle2, Clock3, RefreshCw, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "./AppShell";
import { api, API_URL } from "@/lib/api";

type Agent = { name: string; role: string; status: string; detail: string; created_at: string | null };

export function MonitorClient() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [message, setMessage] = useState("");
  const load = () => api<Agent[]>("/agents/status").then(setAgents).catch((error) => setMessage(error.message));
  useEffect(() => {
    void load();
    const ws = new WebSocket(API_URL.replace(/^http/, "ws") + "/ws/events");
    ws.onmessage = () => void load();
    const timer = window.setInterval(load, 15000);
    return () => { window.clearInterval(timer); ws.close(); };
  }, []);
  return <AppShell title="Pipeline monitor" eyebrow="Local agents" action={<button onClick={() => void load()} className="flex items-center gap-2 rounded-full border border-stroke px-4 py-2 text-xs"><RefreshCw size={14} /> Refresh</button>}>
    {message && <p className="mb-6 text-sm text-amber-200">{message}</p>}
    <section className="rounded-[2rem] border border-[#89aacc]/25 bg-[#89aacc]/5 p-7 md:p-9"><div className="flex flex-wrap items-start justify-between gap-6"><div><p className="text-[10px] uppercase tracking-[0.3em] text-[#bcd3e8]">Evidence-constrained pipeline</p><h2 className="mt-3 font-display text-4xl italic">Observe every decision, keep control of every application.</h2></div><ShieldCheck className="text-emerald-300" size={30} /></div><p className="mt-5 max-w-2xl text-sm leading-7 text-muted">Rolecraft analyzes descriptions, scores demonstrated evidence, tailors a DOCX, and checks it independently. It never logs into job boards or submits applications on your behalf.</p></section>
    <section className="mt-7 grid gap-5 lg:grid-cols-2">{agents.map((agent, index) => <article key={agent.name} className="rounded-[2rem] border border-stroke bg-surface p-7"><div className="flex items-start justify-between gap-4"><div className="grid size-11 place-items-center rounded-2xl border border-stroke bg-bg text-[#89aacc]"><Activity size={18} /></div><StatusBadge status={agent.status} /></div><p className="mt-8 text-[10px] uppercase tracking-[0.28em] text-muted">Step {index + 1}</p><h2 className="mt-2 font-display text-3xl italic">{agent.name}</h2><p className="mt-3 text-sm leading-6 text-muted">{agent.role}</p><div className="mt-7 rounded-2xl border border-stroke bg-bg p-4"><p className="text-sm text-white/85">{agent.detail}</p><p className="mt-2 flex items-center gap-1.5 text-xs text-muted"><Clock3 size={13} />{agent.created_at ? `Last event: ${new Date(agent.created_at + "Z").toLocaleString()}` : "No run recorded yet"}</p></div></article>)}</section>
  </AppShell>;
}

function StatusBadge({ status }: { status: string }) {
  const active = status === "working";
  const failure = status === "failed" || status === "needs_attention";
  return <span className={`rounded-full border px-3 py-1.5 text-xs capitalize ${active ? "border-[#89aacc]/30 bg-[#89aacc]/10 text-[#c7dbef]" : failure ? "border-amber-200/25 bg-amber-200/10 text-amber-100" : "border-emerald-300/20 bg-emerald-300/10 text-emerald-200"}`}>{status === "completed" ? <CheckCircle2 className="mr-1 inline" size={13} /> : null}{status.replace("_", " ")}</span>;
}
