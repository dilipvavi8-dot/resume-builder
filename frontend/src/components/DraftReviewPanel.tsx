"use client";

import { CheckCircle2, Download } from "lucide-react";
import { downloadUrl } from "@/lib/api";

export type GenerationReport = {
  status: string;
  revision_count: number;
  agents: { name: string; role: string; status: string; task_completion: number; tasks: Record<string, boolean> }[];
  requirement_coverage: number;
  truthfulness_score: number;
  ats_score: number;
  ats_gate_passed: boolean;
  unsupported_requirements: string[];
  changes: { section: string; original: string; updated: string; reason: string; client?: string }[];
  review_directives: string[];
  requirements: { requirement: string; supported_by_base: boolean; included_in_resume: boolean; source_evidence?: string | null; status: string }[];
};

export type ResumeDraft = {
  id: number;
  draft_name: string;
  status: string;
  generation_report: GenerationReport;
};

export function DraftReviewPanel({
  draft,
  onApprove,
  busy,
}: {
  draft: ResumeDraft;
  onApprove: () => void;
  busy: boolean;
}) {
  const report = draft.generation_report;
  const canApprove = draft.status === "pending_approval" && report.ats_gate_passed;
  return (
    <div className="mt-5 rounded-3xl border border-[#89aacc]/35 bg-[#89aacc]/5 p-5">
      <p className="text-[10px] uppercase tracking-[0.25em] text-[#bcd3e8]">Resume draft — review required</p>
      <p className="mt-2 text-sm leading-6 text-white/80">
        No final file has been created. Review each evidence-backed edit below. Final DOCX output is available only after the 95% ATS gate passes.
      </p>
      <a
        href={downloadUrl(`/resume-drafts/${draft.id}/download`)}
        className="mt-5 flex w-full items-center justify-center gap-2 rounded-full border border-stroke py-3 text-sm text-white"
      >
        <Download size={16} />
        Download draft preview
      </a>
      <div className="mt-5 space-y-3">
        {report.changes.map((change, index) => (
          <div key={`${change.section}-${index}`} className="rounded-2xl border border-stroke bg-bg p-4 text-xs leading-5">
            <p className="text-[#bcd3e8]">
              {change.section}
              {change.client ? ` — ${change.client}` : ""} · {change.reason}
            </p>
            <p className="mt-3 text-muted">
              <span className="text-white/65">Before:</span> {change.original || "Updated existing skills line"}
            </p>
            <p className="mt-2 text-emerald-100">
              <span className="text-white/65">After:</span> {change.updated}
            </p>
          </div>
        ))}
      </div>
      <div className="mt-5 rounded-2xl border border-stroke bg-bg p-4 text-xs leading-5">
        <p className="text-white">Requirement evidence map</p>
        {report.requirements.map((item) => (
          <div key={item.requirement} className="mt-3">
            <p className={item.supported_by_base ? "text-emerald-100" : "text-amber-100"}>
              {item.requirement}: {item.supported_by_base ? "supported by base resume" : "gap — not added"}
            </p>
            {item.source_evidence && <p className="mt-1 text-muted">Evidence: {item.source_evidence}</p>}
          </div>
        ))}
      </div>
      {canApprove ? (
        <button
          onClick={onApprove}
          disabled={busy}
          className="mt-5 flex w-full items-center justify-center gap-2 rounded-full bg-white py-3.5 text-sm text-black disabled:opacity-40"
        >
          <CheckCircle2 size={16} />
          Approve draft and generate DOCX
        </button>
      ) : (
        <div className="mt-5 rounded-2xl border border-amber-200/40 bg-amber-200/10 p-4 text-xs leading-5 text-amber-50">
          Final output is blocked: evidence-backed ATS coverage is {report.ats_score}% (95% required). Add missing experience to your base resume, then create a new draft.
        </div>
      )}
    </div>
  );
}
