"use client";
import { useEffect, useState } from "react";
import { ExternalLink } from "lucide-react";
import { AppShell } from "./AppShell";
import { EmptyState } from "./Ui";
import { api } from "@/lib/api";

type Application = { id: number; company: string; role_title: string; job_link: string; status: string; applied_date: string; recruiter_name: string; follow_up_date: string; notes: string };
const statuses = ["Not Applied", "Applied", "Recruiter Contacted", "Interview Scheduled", "Rejected", "Offer", "Follow Up Needed"];
export function TrackerClient() {
  const [items, setItems] = useState<Application[]>([]);
  const [error, setError] = useState("");
  const load = () => api<Application[]>("/applications").then(setItems).catch((reason) => setError(reason.message));
  useEffect(() => {
    void load();
  }, []);
  const update = async (id: number, status: string) => {
    try {
      await api(`/applications/${id}`, { method: "PUT", body: JSON.stringify({ status }) });
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update application status.");
    }
  };
  return <AppShell title="Application tracker" eyebrow="Follow through">{error && <p className="mb-6 text-sm text-amber-200">{error}</p>}{!items.length ? <EmptyState title="No applications tracked yet." text="Mark a job as applied from the feed and it will appear here for follow-ups, recruiter notes, and status updates." /> : <div className="overflow-hidden rounded-[2rem] border border-stroke bg-surface"><div className="hidden grid-cols-[1.2fr_1.6fr_1fr_1fr_auto] gap-5 border-b border-stroke px-7 py-4 text-[10px] uppercase tracking-[0.2em] text-muted md:grid"><span>Company</span><span>Role</span><span>Status</span><span>Applied</span><span>Link</span></div>{items.map((item) => <div key={item.id} className="grid gap-4 border-b border-stroke px-6 py-6 last:border-0 md:grid-cols-[1.2fr_1.6fr_1fr_1fr_auto] md:items-center md:gap-5 md:px-7"><strong className="text-sm">{item.company}</strong><span className="text-sm text-white/75">{item.role_title}</span><select value={item.status} onChange={(event) => update(item.id, event.target.value)} className="rounded-full border border-stroke bg-bg px-3 py-2 text-xs outline-none">{statuses.map((status) => <option key={status}>{status}</option>)}</select><span className="text-xs text-muted">{item.applied_date || "—"}</span><a href={item.job_link} target="_blank" rel="noreferrer" className="grid size-9 place-items-center rounded-full border border-stroke text-muted hover:text-white"><ExternalLink size={14} /></a></div>)}</div>}</AppShell>;
}
