"use client";

import { useEffect, useMemo, useState } from "react";
import { Download, FileText, Trash2 } from "lucide-react";
import { AppShell } from "./AppShell";
import { EmptyState, Score } from "./Ui";
import { api, downloadUrl } from "@/lib/api";

type Resume = {
  id: number;
  resume_name: string;
  company: string;
  role_title: string;
  match_score: number;
  requirement_coverage: number;
  truthfulness_score: number;
  generation_status: string;
  pdf_path: string | null;
  created_at: string;
};

export function ResumesClient() {
  const [items, setItems] = useState<Resume[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const load = () => api<Resume[]>("/resumes").then((resumes) => {
    setItems(resumes);
    setSelected((current) => current.filter((id) => resumes.some((item) => item.id === id)));
  }).catch((reason) => setError(reason.message));

  useEffect(() => { void load(); }, []);
  const allSelected = useMemo(() => items.length > 0 && selected.length === items.length, [items, selected]);
  const toggle = (id: number) => setSelected((current) => current.includes(id) ? current.filter((value) => value !== id) : [...current, id]);
  const toggleAll = () => setSelected(allSelected ? [] : items.map((item) => item.id));
  const removeSelected = async () => {
    if (!selected.length || !window.confirm(`Delete ${selected.length} selected generated resume${selected.length === 1 ? "" : "s"}? This removes their local DOCX files and cannot be undone.`)) return;
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await api<{ deleted_versions: number; deleted_files: number }>("/resumes", { method: "DELETE", body: JSON.stringify({ resume_ids: selected }) });
      setMessage(`Deleted ${result.deleted_versions} generated resume${result.deleted_versions === 1 ? "" : "s"} and ${result.deleted_files} local file${result.deleted_files === 1 ? "" : "s"}.`);
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not delete the selected resumes."); }
    finally { setBusy(false); }
  };

  return <AppShell title="Resume library" eyebrow="Version history">
    {(error || message) && <p className={`mb-6 rounded-2xl border px-5 py-3 text-sm ${error ? "border-amber-200/30 bg-amber-200/10 text-amber-100" : "border-emerald-200/20 bg-emerald-200/10 text-emerald-100"}`}>{error || message}</p>}
    {!items.length ? <EmptyState title="No tailored versions yet." text="Analyze a job description or select a role from the feed, then generate a verified DOCX. Every version remains available here." /> : <>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-stroke bg-surface px-5 py-3">
        <label className="flex cursor-pointer items-center gap-3 text-sm text-white/80"><input type="checkbox" checked={allSelected} onChange={toggleAll} className="size-4 accent-white" /> Select all ({items.length})</label>
        <button onClick={removeSelected} disabled={!selected.length || busy} className="flex items-center gap-2 rounded-full border border-red-300/30 bg-red-300/10 px-4 py-2 text-xs text-red-100 disabled:cursor-not-allowed disabled:opacity-40"><Trash2 size={14} />{busy ? "Deleting…" : `Delete selected${selected.length ? ` (${selected.length})` : ""}`}</button>
      </div>
      <div className="grid gap-5">{items.map((item) => <article key={item.id} className="flex flex-col gap-5 rounded-[2rem] border border-stroke bg-surface p-6 md:flex-row md:items-center md:p-8">
        <label className="flex cursor-pointer items-center self-start pt-2" aria-label={`Select ${item.resume_name}`}><input type="checkbox" checked={selected.includes(item.id)} onChange={() => toggle(item.id)} className="size-4 accent-white" /></label>
        <div className="grid size-14 shrink-0 place-items-center rounded-2xl bg-bg"><FileText className="text-[#89aacc]" /></div>
        <div className="min-w-0 flex-1"><p className="truncate font-display text-2xl italic">{item.resume_name}</p><p className="mt-2 text-sm text-muted">{item.company || "Manual JD"} / {item.role_title} / {new Date(item.created_at).toLocaleDateString()}</p><div className="mt-3 flex flex-wrap gap-2 text-[11px]"><span className="rounded-full border border-stroke bg-bg px-3 py-1 text-muted">JD coverage {item.requirement_coverage || 0}%</span><span className="rounded-full border border-stroke bg-bg px-3 py-1 text-muted">Truthfulness {item.truthfulness_score || 0}%</span><span className="rounded-full border border-stroke bg-bg px-3 py-1 capitalize text-muted">{item.generation_status || "legacy"}</span></div></div>
        <Score value={item.match_score} /><a href={downloadUrl(`/resumes/${item.id}/download`)} className="flex items-center justify-center gap-2 rounded-full bg-white px-5 py-3 text-sm text-black"><Download size={15} /> DOCX</a>
      </article>)}</div>
    </>}
  </AppShell>;
}
