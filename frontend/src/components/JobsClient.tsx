"use client";

import { useEffect, useState } from "react";
import { ArrowUpRight, Download, MapPin, RefreshCw, SearchCheck, Sparkles } from "lucide-react";
import { AppShell } from "./AppShell";
import { DraftReviewPanel, type ResumeDraft } from "./DraftReviewPanel";
import { EmptyState, Score } from "./Ui";
import { api, downloadUrl } from "@/lib/api";

type Job = { id: number; title: string; company: string; location: string; posted_date: string; source_url: string; experience_required: string; required_skills: string[]; cloud_platform: string; role_type: string; match_score: number; recommendation: string; job_description: string; status: string };
type GeneratedResume = { id: number; download_url: string };

export function JobsClient() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selected, setSelected] = useState<Job | null>(null);
  const [draft, setDraft] = useState<ResumeDraft | null>(null);
  const [resume, setResume] = useState<GeneratedResume | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const load = () => api<Job[]>("/jobs").then(setJobs).catch((error) => setMessage(error.message));
  useEffect(() => {
    void load();
  }, []);
  const fetchJobs = async () => { setBusy(true); await api("/jobs/fetch", { method: "POST" }).then(load).catch((error) => setMessage(error.message)); setBusy(false); };
  const analyze = async (job: Job) => { setBusy(true); try { const result = await api<{ match_score: number }>(`/jobs/${job.id}/analyze`, { method: "POST" }); setMessage(`${job.company} was re-analyzed: ${result.match_score}% evidence-based match.`); await load(); } catch (error) { setMessage(error instanceof Error ? error.message : "Could not analyze this role."); } finally { setBusy(false); } };
  const generate = async (job: Job) => {
    setBusy(true); setDraft(null); setResume(null); setMessage("");
    try {
      const created = await api<ResumeDraft>(`/jobs/${job.id}/generate-resume`, { method: "POST" });
      setDraft(created);
      setMessage(`Draft created for ${job.company}. Review the evidence-backed edits below before approving the final resume.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not generate resume draft.");
    } finally {
      setBusy(false);
    }
  };
  const approve = async () => {
    if (!draft) return;
    setBusy(true); setMessage("");
    try {
      const approved = await api<GeneratedResume>(`/resume-drafts/${draft.id}/approve`, { method: "POST" });
      setResume(approved);
      setDraft(null);
      setMessage("Verified DOCX saved to your library.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Approval failed.");
    } finally {
      setBusy(false);
    }
  };
  const apply = async (job: Job) => {
    if (job.status === "Applied") {
      setMessage(`${job.company} is already added to your tracker.`);
      return;
    }
    try {
      await api("/applications", {
        method: "POST",
        body: JSON.stringify({
          job_id: job.id,
          company: job.company,
          role_title: job.title,
          job_link: job.source_url,
          status: "Applied",
          applied_date: new Date().toISOString().slice(0, 10),
        }),
      });
      setMessage(`${job.company} added to your tracker.`);
      load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not update tracker.");
    }
  };
  return (
    <AppShell title="Curated job feed" eyebrow="Job discovery" action={<button onClick={fetchJobs} disabled={busy} className="flex items-center gap-2 rounded-full bg-white px-4 py-2 text-xs text-black"><RefreshCw size={14} className={busy ? "animate-spin" : ""} /> Refresh feed</button>}>
      {message && <div className="mb-6 rounded-2xl border border-[#89aacc]/30 bg-[#89aacc]/10 px-5 py-3 text-sm text-[#c7dbef]">{message}</div>}
      {draft && <div className="mb-6"><DraftReviewPanel draft={draft} onApprove={approve} busy={busy} /></div>}
      {resume && <div className="mb-6 rounded-2xl border border-emerald-200/20 bg-emerald-200/10 px-5 py-4"><a href={downloadUrl(resume.download_url)} className="flex items-center justify-center gap-2 rounded-full bg-white py-3 text-sm text-black"><Download size={16} /> Download verified DOCX</a></div>}
      {!jobs.length ? <EmptyState title="Your focused feed is ready to begin." text="Use Refresh feed to load the local sample roles. Real Greenhouse and Lever handlers can be added to the source service later." /> :
      <div className="grid gap-5">
        {jobs.map((job) => <article key={job.id} className="grid gap-6 rounded-[2rem] border border-stroke bg-surface p-6 md:grid-cols-[auto_1fr_auto] md:items-center md:p-8">
          <Score value={job.match_score} />
          <div><div className="flex flex-wrap items-center gap-2"><span className="rounded-full border border-stroke bg-bg px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-muted">{job.role_type}</span><span className="rounded-full border border-stroke bg-bg px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-muted">{job.cloud_platform}</span></div><h2 className="mt-4 font-display text-3xl italic md:text-4xl">{job.title}</h2><p className="mt-2 text-sm text-white/75">{job.company}</p><div className="mt-3 flex flex-wrap gap-4 text-xs text-muted"><span className="flex items-center gap-1.5"><MapPin size={13} />{job.location}</span><span>{job.experience_required}</span><span>Posted {job.posted_date}</span></div></div>
          <div className="flex flex-wrap gap-2 md:max-w-56 md:justify-end"><button onClick={() => setSelected(job)} className="rounded-full border border-stroke px-4 py-2 text-xs">View details</button><button onClick={() => analyze(job)} disabled={busy} className="rounded-full border border-stroke px-4 py-2 text-xs"><SearchCheck className="mr-1 inline" size={13} /> Re-score</button><button onClick={() => generate(job)} className="rounded-full bg-white px-4 py-2 text-xs text-black">Generate resume</button><button onClick={() => apply(job)} aria-label="Mark applied" className="rounded-full border border-stroke px-4 py-2 text-xs text-muted">{job.status === "Applied" ? "Applied" : "Mark applied"}</button></div>
        </article>)}
      </div>}
      {selected && <div className="fixed inset-0 z-[100] grid place-items-center bg-black/75 p-4 backdrop-blur-md" onClick={() => setSelected(null)}><div className="thin-scrollbar max-h-[88vh] w-full max-w-3xl overflow-y-auto rounded-[2rem] border border-stroke bg-surface p-7 md:p-10" onClick={(event) => event.stopPropagation()}><div className="flex items-start justify-between gap-5"><div><p className="text-[10px] uppercase tracking-[0.3em] text-muted">{selected.company}</p><h2 className="mt-3 font-display text-4xl italic">{selected.title}</h2></div><button onClick={() => setSelected(null)} className="rounded-full border border-stroke px-3 py-1 text-xs">Close</button></div><p className="mt-7 whitespace-pre-wrap text-sm leading-7 text-white/70">{selected.job_description}</p><div className="mt-7 flex flex-wrap gap-2">{selected.required_skills.map((skill) => <span className="rounded-full border border-stroke bg-bg px-3 py-1.5 text-xs" key={skill}>{skill}</span>)}</div><div className="mt-8 flex flex-wrap gap-3"><a href={selected.source_url} target="_blank" rel="noreferrer" className="flex items-center gap-2 rounded-full border border-stroke px-5 py-3 text-sm">Source link <ArrowUpRight size={14} /></a><button onClick={() => generate(selected)} className="flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm text-black"><Sparkles size={14} /> Generate resume</button></div></div></div>}
    </AppShell>
  );
}
