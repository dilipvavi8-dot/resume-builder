"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { ArrowUpRight, BriefcaseBusiness, Check, FileSearch, Files, RefreshCw, Send, Upload, type LucideIcon } from "lucide-react";
import { AppShell } from "./AppShell";
import { api } from "@/lib/api";
import Link from "next/link";

type Summary = { total_jobs: number; todays_jobs: number; strong_matches: number; medium_matches: number; low_matches: number; generated_resumes: number; applications: number };
type ResumeProfile = { id: string; name: string; filename: string; active: boolean };

export function DashboardClient() {
  const [data, setData] = useState<Summary | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [resumeName, setResumeName] = useState("");
  const [resumeProfiles, setResumeProfiles] = useState<ResumeProfile[]>([]);
  const load = () => api<Summary>("/dashboard/summary").then(setData).catch((error) => setMessage(error.message));
  useEffect(() => {
    void load();
  }, []);
  const loadResumeProfiles = async () => {
    const profiles = await api<ResumeProfile[]>("/resume/profiles");
    setResumeProfiles(profiles);
    setResumeName(profiles.find((profile) => profile.active)?.filename || "");
  };
  useEffect(() => {
    api<ResumeProfile[]>("/resume/profiles")
      .then((profiles) => {
        setResumeProfiles(profiles);
        setResumeName(profiles.find((profile) => profile.active)?.filename || "");
      })
      .catch(() => undefined);
  }, []);
  const fetchJobs = async () => {
    setBusy(true); setMessage("");
    try {
      const result = await api<{ jobs_saved: number; duplicates_removed: number }>("/jobs/fetch", { method: "POST" });
      setMessage(`${result.jobs_saved} new roles saved, ${result.duplicates_removed} existing roles refreshed.`);
      load();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Fetch failed."); }
    finally { setBusy(false); }
  };
  const uploadResume = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    setBusy(true);
    setMessage("");
    try {
      const resume = await api<{ filename: string }>("/resume/master/upload", { method: "POST", body });
      setResumeName(resume.filename);
      await loadResumeProfiles();
      setMessage("Resume added to the local library and selected as the main resume.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Resume upload failed.");
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  };
  const selectResume = async (profileId: string) => {
    setBusy(true);
    setMessage("");
    try {
      const resume = await api<ResumeProfile>(`/resume/profiles/${profileId}/select`, { method: "POST" });
      setResumeName(resume.filename);
      await loadResumeProfiles();
      setMessage(`${resume.name} is now the main resume used for matching and generation.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not select resume.");
    } finally {
      setBusy(false);
    }
  };
  const stats: [string, number | string, LucideIcon][] = [
    ["Jobs today", data?.todays_jobs ?? "—", BriefcaseBusiness],
    ["Strong matches", data?.strong_matches ?? "—", ArrowUpRight],
    ["Resume versions", data?.generated_resumes ?? "—", Files],
    ["Applications", data?.applications ?? "—", Send],
  ];
  return (
    <AppShell title="Career command center" eyebrow="Overview" action={<button onClick={fetchJobs} disabled={busy} aria-label="Fetch jobs" className="gradient-border flex items-center gap-2 rounded-full bg-white p-3 text-xs text-black disabled:opacity-50 sm:px-4 sm:py-2"><RefreshCw size={14} className={busy ? "animate-spin" : ""} /><span className="hidden sm:inline">Fetch jobs</span></button>}>
      {message && <div className="mb-6 rounded-2xl border border-[#89aacc]/30 bg-[#89aacc]/10 px-5 py-3 text-sm text-[#c7dbef]">{message}</div>}
      <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map(([label, value, Icon]) => <article key={String(label)} className="rounded-3xl border border-stroke bg-surface p-6"><Icon size={18} className="text-[#89aacc]" /><p className="mt-8 font-display text-5xl italic">{String(value)}</p><p className="mt-2 text-xs uppercase tracking-[0.2em] text-muted">{String(label)}</p></article>)}
      </section>
      <section className="mt-10 grid gap-5 xl:grid-cols-[1.45fr_.55fr]">
        <div className="relative min-h-[400px] overflow-hidden rounded-[2rem] border border-stroke bg-surface p-8 md:p-10">
          <div className="absolute right-[-6rem] top-[-7rem] size-80 rounded-full bg-blue-400/10 blur-3xl" />
          <p className="text-[10px] uppercase tracking-[0.3em] text-muted">Today&apos;s focus</p>
          <h2 className="mt-5 max-w-xl font-display text-5xl italic leading-[1.02] md:text-6xl">Find the role where your experience compounds.</h2>
          <p className="mt-6 max-w-lg text-sm leading-7 text-muted">Fetch a fresh set of focused sample roles, compare them with your master resume, and choose where to invest your energy.</p>
          <div className="absolute inset-x-8 bottom-8 flex flex-wrap gap-3 md:inset-x-10"><Link href="/jobs" className="rounded-full bg-white px-5 py-3 text-sm text-black">Review job feed</Link><Link href="/manual-jd" className="rounded-full border border-stroke px-5 py-3 text-sm">Paste a job description</Link></div>
        </div>
        <div className="space-y-5">
          <label className="group block cursor-pointer rounded-[2rem] border border-stroke bg-surface p-7 transition hover:border-white/20">
            <input type="file" accept=".docx,.pdf,.txt" className="hidden" onChange={uploadResume} />
            {resumeName ? <Check className="text-emerald-300" /> : <Upload className="text-[#89aacc]" />}
            <p className="mt-8 font-display text-3xl italic">{resumeName ? "Master resume ready" : "Upload master resume"}</p>
            <p className="mt-3 truncate text-sm leading-6 text-muted">{resumeName || "DOCX, PDF, or TXT. Uploads are retained in the local library."}</p>
          </label>
          {resumeProfiles.length > 1 && <div className="rounded-[2rem] border border-stroke bg-surface p-7">
            <label htmlFor="main-resume" className="text-[10px] uppercase tracking-[0.3em] text-muted">Main resume</label>
            <select id="main-resume" value={resumeProfiles.find((profile) => profile.active)?.id || ""} onChange={(event) => void selectResume(event.target.value)} disabled={busy} className="mt-4 w-full rounded-2xl border border-stroke bg-bg px-4 py-3 text-sm outline-none focus:border-[#89aacc]">
              {resumeProfiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.name}</option>)}
            </select>
            <p className="mt-3 text-xs leading-5 text-muted">Matching and tailored resumes use the selected profile.</p>
          </div>}
          <Link href="/manual-jd" className="group block rounded-[2rem] border border-stroke bg-surface p-7 transition hover:border-white/20"><FileSearch className="text-[#89aacc]" /><p className="mt-12 font-display text-3xl italic">Analyze any JD</p><p className="mt-3 text-sm leading-6 text-muted">Skills, experience, gaps, and match score in one view.</p></Link>
          <div className="rounded-[2rem] border border-stroke bg-surface p-7"><p className="text-[10px] uppercase tracking-[0.3em] text-muted">Match distribution</p><div className="mt-7 space-y-4">{[["Strong", data?.strong_matches ?? 0, "bg-emerald-300"], ["Medium", data?.medium_matches ?? 0, "bg-[#89aacc]"], ["Develop", data?.low_matches ?? 0, "bg-amber-200"]].map(([label, value, color]) => <div key={String(label)} className="flex items-center justify-between text-sm"><span className="flex items-center gap-3"><i className={`size-2 rounded-full ${color}`} />{label}</span><span className="text-muted">{value}</span></div>)}</div></div>
        </div>
      </section>
    </AppShell>
  );
}
