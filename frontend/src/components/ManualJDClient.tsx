"use client";

import { ChangeEvent, useState } from "react";
import { CheckCircle2, Download, FileUp, SearchCheck, Sparkles, UserRoundPen } from "lucide-react";
import { AppShell } from "./AppShell";
import { DraftReviewPanel, type GenerationReport, type ResumeDraft } from "./DraftReviewPanel";
import { Score } from "./Ui";
import { api, downloadUrl } from "@/lib/api";

type ScoreBreakdown = { category: string; earned: number | null; possible: number; applicable: boolean };
type UpdatePlan = { baseline_weighted_score: number; target_score: number; target_status: string; missing_required: string[]; missing_preferred: string[]; weak_sections: string[]; strategy: string[]; client_gaps?: { client: string; existing_stack: string[]; missing_required: string[] }[] };
type Result = {
  id: number;
  required_skills: string[];
  preferred_skills: string[];
  matching_skills: string[];
  experience_required: string;
  resume_experience: string;
  cloud_platform: string;
  role_type: string;
  match_score: number;
  score_breakdown: ScoreBreakdown[];
  score_notes: string[];
  missing_keywords: string[];
  recommendation: string;
  resume_update_plan: UpdatePlan;
};
type GeneratedResume = {
  id: number;
  download_url: string;
  generation_report: GenerationReport;
};

export function ManualJDClient() {
  const [form, setForm] = useState({ title: "", company: "", location: "", jd_text: "" });
  const [result, setResult] = useState<Result | null>(null);
  const [draft, setDraft] = useState<ResumeDraft | null>(null);
  const [resume, setResume] = useState<GeneratedResume | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const update = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setForm({ ...form, [event.target.name]: event.target.value });
  const analyze = async () => {
    setBusy(true); setMessage(""); setDraft(null); setResume(null);
    try { setResult(await api<Result>("/manual-jd/analyze", { method: "POST", body: JSON.stringify(form) })); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Analysis failed."); }
    finally { setBusy(false); }
  };
  const generate = async () => {
    if (!result) return;
    setBusy(true); setMessage("");
    try { setDraft(await api<ResumeDraft>(`/manual-jd/generate-resume/${result.id}`, { method: "POST" })); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Generation failed."); }
    finally { setBusy(false); }
  };
  const approve = async () => {
    if (!draft) return;
    setBusy(true); setMessage("");
    try {
      const approved = await api<GeneratedResume>(`/resume-drafts/${draft.id}/approve`, { method: "POST" });
      setResume(approved);
      setDraft(null);
      setMessage("Verified DOCX saved to your library.");
    }
    catch (error) { setMessage(error instanceof Error ? error.message : "Approval failed."); }
    finally { setBusy(false); }
  };
  const readJDFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) setForm({ ...form, jd_text: await file.text() });
  };
  return (
    <AppShell title="Job description studio" eyebrow="Analyze JD">
      {message && <div className="mb-6 rounded-2xl border border-amber-300/20 bg-amber-300/10 px-5 py-3 text-sm text-amber-100">{message}</div>}
      <div className="grid gap-6 xl:grid-cols-[1fr_.9fr]">
        <section className="rounded-[2rem] border border-stroke bg-surface p-6 md:p-8">
          <div className="grid gap-4 md:grid-cols-2"><input name="title" value={form.title} onChange={update} placeholder="Job title" className="rounded-2xl border border-stroke bg-bg px-4 py-3 text-sm outline-none focus:border-[#89aacc]" /><input name="company" value={form.company} onChange={update} placeholder="Company" className="rounded-2xl border border-stroke bg-bg px-4 py-3 text-sm outline-none focus:border-[#89aacc]" /></div>
          <input name="location" value={form.location} onChange={update} placeholder="Location" className="mt-4 w-full rounded-2xl border border-stroke bg-bg px-4 py-3 text-sm outline-none focus:border-[#89aacc]" />
          <div className="relative mt-4"><textarea name="jd_text" value={form.jd_text} onChange={update} placeholder="Paste the complete job description here..." className="thin-scrollbar min-h-[430px] w-full resize-none rounded-3xl border border-stroke bg-bg p-5 text-sm leading-7 outline-none focus:border-[#89aacc]" /><label className="absolute bottom-4 right-4 flex cursor-pointer items-center gap-2 rounded-full border border-stroke bg-surface px-4 py-2 text-xs text-muted hover:text-white"><FileUp size={14} /> Load TXT<input type="file" accept=".txt" onChange={readJDFile} className="hidden" /></label></div>
          <button onClick={analyze} disabled={busy || !form.title || !form.jd_text} className="mt-5 flex w-full items-center justify-center gap-2 rounded-full bg-white py-3.5 text-sm text-black disabled:opacity-40"><Sparkles size={16} />{busy ? "Agents working..." : "Analyze match"}</button>
        </section>
        <section className="rounded-[2rem] border border-stroke bg-surface p-6 md:p-8">
          {!result ? <div className="grid h-full min-h-[500px] place-items-center text-center"><div><div className="mx-auto grid size-20 place-items-center rounded-full border border-stroke"><Sparkles className="text-[#89aacc]" /></div><p className="mt-6 font-display text-3xl italic">Your analysis appears here.</p><p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-muted">We&apos;ll map the role, skills, experience, match score, and missing keywords against your master resume.</p></div></div> : <div>
            <div className="flex items-center justify-between"><div><p className="text-[10px] uppercase tracking-[0.3em] text-muted">Match result</p><p className="mt-2 font-display text-3xl italic">{result.recommendation}</p></div><Score value={result.match_score} /></div>
            <div className="mt-8 grid grid-cols-3 gap-3">{[["Role", result.role_type], ["Cloud", result.cloud_platform], ["Experience", result.experience_required]].map(([label, value]) => <div key={label} className="rounded-2xl border border-stroke bg-bg p-4"><p className="text-[9px] uppercase tracking-[0.2em] text-muted">{label}</p><p className="mt-2 text-sm">{value}</p></div>)}</div>
            <div className="mt-8 rounded-3xl border border-stroke bg-bg p-5">
              <div className="mb-4 flex items-center justify-between"><p className="text-[10px] uppercase tracking-[0.25em] text-muted">Score breakdown</p><span className="text-xs text-muted">Resume: {result.resume_experience}</span></div>
              <div className="space-y-3">{result.score_breakdown.map((item) => <div key={item.category} className="flex items-center justify-between gap-4 text-sm"><span className={item.applicable ? "text-white/75" : "text-muted"}>{item.category}</span><span className="tabular-nums text-muted">{item.applicable ? `${item.earned}/${item.possible}` : "Not required"}</span></div>)}</div>
            </div>
            {result.score_notes.length > 0 && <div className="mt-4 rounded-2xl border border-amber-200/20 bg-amber-200/10 p-4 text-xs leading-5 text-amber-100">{result.score_notes.map((note) => <p key={note}>{note}</p>)}</div>}
            <section className="mt-5 rounded-2xl border border-[#89aacc]/25 bg-[#89aacc]/5 p-4 text-xs leading-5">
              <div className="flex items-center justify-between gap-3">
                <p className="uppercase tracking-[0.18em] text-[#bcd3e8]">Resume updater plan</p>
                <span className="text-white">{result.resume_update_plan.baseline_weighted_score}% evidence match · 95% gate</span>
              </div>
              <p className="mt-3 text-muted">Only evidence already in your resume can be mirrored. Unsupported requirements remain gaps and block final DOCX output.</p>
              {result.resume_update_plan.weak_sections.length > 0 && <p className="mt-2 text-white/80">Focus: {result.resume_update_plan.weak_sections.join(", ")}</p>}
              {result.resume_update_plan.missing_required.length > 0 && <p className="mt-2 text-amber-100">Required gaps: {result.resume_update_plan.missing_required.join(", ")}</p>}
              {result.resume_update_plan.client_gaps?.map((client) => <p key={client.client} className="mt-2 text-muted">{client.client}: {client.existing_stack.join(", ") || "No stack detected"}</p>)}
            </section>
            <TagSection title="Matching skills" values={result.matching_skills} />
            <TagSection title="Required skills" values={result.required_skills} />
            <TagSection title="Missing keywords" values={result.missing_keywords} warning />
            <p className="mt-8 rounded-2xl border border-stroke bg-bg px-4 py-3 text-xs leading-5 text-muted">The Resume Tailoring Agent rewrites the summary, prioritizes supported skills, and updates relevant experience bullets in place. The Resume Quality Monitor then verifies every change against the base resume and requests corrections when needed.</p>
            <button onClick={generate} disabled={busy} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full border border-[#89aacc]/40 bg-[#89aacc]/10 py-3.5 text-sm text-[#d7e8f7] disabled:opacity-50"><Sparkles size={16} /> {busy ? "Tailoring and verifying..." : "Create reviewable resume draft"}</button>
            {draft && <DraftReviewPanel draft={draft} onApprove={approve} busy={busy} />}
            {resume && <AgentReport report={resume.generation_report} />}
            {resume && <a href={downloadUrl(resume.download_url)} className="mt-3 flex w-full items-center justify-center gap-2 rounded-full bg-white py-3.5 text-sm text-black"><Download size={16} /> Download verified DOCX</a>}
          </div>}
        </section>
      </div>
    </AppShell>
  );
}

function AgentReport({ report }: { report: GenerationReport }) {
  return <div className="mt-5 rounded-3xl border border-[#89aacc]/25 bg-[#89aacc]/5 p-5">
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div><p className="text-[10px] uppercase tracking-[0.25em] text-[#bcd3e8]">Agent execution report</p><p className="mt-2 text-lg">{report.status === "approved" ? "Monitor approved the tailored resume" : "Monitor found unresolved issues"}</p></div>
      <span className="rounded-full border border-stroke bg-bg px-3 py-1.5 text-xs text-muted">{report.revision_count} corrective pass{report.revision_count === 1 ? "" : "es"}</span>
    </div>
    <div className="mt-5 grid gap-3 sm:grid-cols-2">
      {report.agents.map((agent, index) => <div key={agent.name} className="rounded-2xl border border-stroke bg-bg p-4">
        <div className="flex items-start gap-3">{index === 0 ? <UserRoundPen size={18} className="mt-0.5 text-[#89aacc]" /> : <SearchCheck size={18} className="mt-0.5 text-emerald-300" />}<div><p className="text-sm text-white">{agent.name}</p><p className="mt-1 text-xs leading-5 text-muted">{agent.role}</p></div></div>
        <div className="mt-4 flex items-center justify-between text-xs"><span className="capitalize text-muted">{agent.status.replace("_", " ")}</span><span className="text-white">{agent.task_completion}% task completion</span></div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-[#89aacc]" style={{ width: `${agent.task_completion}%` }} /></div>
      </div>)}
    </div>
    <div className="mt-4 grid grid-cols-2 gap-3">
      <Metric label="ATS gate coverage" value={report.ats_score} />
      <Metric label="Truthfulness score" value={report.truthfulness_score} />
    </div>
    <div className="mt-4 rounded-2xl border border-stroke bg-bg p-4 text-xs leading-5 text-muted">
      <p><span className="text-white">{report.changes.length} targeted edits</span> completed across the summary, skills, and work experience.</p>
      {report.unsupported_requirements.length > 0 && <p className="mt-2 text-amber-100">Not added because the base resume has no verifiable evidence: {report.unsupported_requirements.join(", ")}.</p>}
      {report.review_directives.length > 0 && report.review_directives.map((directive) => <p key={directive} className="mt-2 text-amber-100">{directive}</p>)}
    </div>
  </div>;
}

function Metric({ label, value }: { label: string; value: number }) {
  return <div className="rounded-2xl border border-stroke bg-bg p-4"><div className="flex items-center justify-between gap-2"><span className="text-xs text-muted">{label}</span><CheckCircle2 size={15} className={value === 100 ? "text-emerald-300" : "text-amber-200"} /></div><p className="mt-2 text-2xl">{value}%</p></div>;
}

function TagSection({ title, values, warning = false }: { title: string; values: string[]; warning?: boolean }) {
  return <div className="mt-8"><p className="mb-3 text-[10px] uppercase tracking-[0.25em] text-muted">{title}</p><div className="flex flex-wrap gap-2">{values.length ? values.map((value) => <span key={value} className={`rounded-full border px-3 py-1.5 text-xs ${warning ? "border-amber-200/20 bg-amber-200/10 text-amber-100" : "border-stroke bg-bg text-white/75"}`}>{value}</span>) : <span className="text-sm text-muted">None detected</span>}</div></div>;
}
