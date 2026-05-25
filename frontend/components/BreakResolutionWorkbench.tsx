"use client";

import { useMemo, useState } from "react";
import {
  candidatesByExceptionId,
  evidenceByExceptionId,
  priorityQueue,
  type BreakItem,
  type Candidate,
  type EvidenceField,
} from "@/lib/demoData";

function StatusBadge({ value }: { value: string }) {
  const style =
    value === "BREACHED"
      ? "bg-red-50 text-red-700 ring-red-200"
      : value === "DUE_TODAY"
        ? "bg-amber-50 text-amber-700 ring-amber-200"
        : "bg-emerald-50 text-emerald-700 ring-emerald-200";

  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${style}`}>
      {value}
    </span>
  );
}

function PriorityPill({ value }: { value: string }) {
  const style =
    value === "High"
      ? "bg-slate-950 text-white"
      : value === "Medium"
        ? "bg-slate-200 text-slate-900"
        : "bg-slate-100 text-slate-600";

  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${style}`}>
      {value}
    </span>
  );
}

function EvidenceStatus({ value }: { value: string }) {
  const style =
    value === "difference"
      ? "bg-red-50 text-red-700"
      : value === "missing"
        ? "bg-amber-50 text-amber-700"
        : "bg-emerald-50 text-emerald-700";

  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${style}`}>
      {value}
    </span>
  );
}

function QueueCard({
  item,
  active,
  onSelect,
}: {
  item: BreakItem;
  active: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={`w-full rounded-2xl border p-4 text-left transition ${
        active
          ? "border-slate-950 bg-slate-950 text-white shadow-lg shadow-slate-200"
          : "border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50"
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="font-bold">{item.exceptionId}</div>
        <StatusBadge value={item.slaStatus} />
      </div>

      <div className={`mt-2 text-sm ${active ? "text-slate-300" : "text-slate-500"}`}>
        {item.breakType}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <PriorityPill value={item.priority} />
        <span className={`text-xs ${active ? "text-slate-300" : "text-slate-500"}`}>
          Age {item.ageDays}d
        </span>
      </div>

      <div className={`mt-4 text-sm ${active ? "text-slate-200" : "text-slate-600"}`}>
        Recommended: <span className="font-semibold">{item.recommendedAction}</span>
      </div>
    </button>
  );
}

function EvidenceComparison({ fields }: { fields: EvidenceField[] }) {
  return (
    <div className="space-y-3">
      {fields.map((field) => (
        <div
          key={field.field}
          className="grid gap-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 lg:grid-cols-[160px_1fr_1fr_120px]"
        >
          <div>
            <div className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
              Field
            </div>
            <div className="mt-2 font-bold">{field.field}</div>
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
              Bank
            </div>
            <div className="mt-2 text-sm font-semibold">{field.bankValue}</div>
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
              Ledger
            </div>
            <div className="mt-2 text-sm font-semibold">{field.ledgerValue}</div>
            <p className="mt-2 text-xs leading-5 text-slate-500">{field.note}</p>
          </div>
          <div className="flex items-start justify-end">
            <EvidenceStatus value={field.status} />
          </div>
        </div>
      ))}
    </div>
  );
}

function CandidateCard({ candidate }: { candidate: Candidate }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
        {candidate.source}
      </div>
      <div className="mt-3 text-2xl font-black">{candidate.confidence}</div>
      <p className="mt-3 text-sm leading-6 text-slate-600">{candidate.rationale}</p>
    </div>
  );
}

export default function BreakResolutionWorkbench() {
  const [selectedId, setSelectedId] = useState(priorityQueue[0].exceptionId);
  const [decision, setDecision] = useState<string | null>(null);

  const selectedBreak = useMemo(
    () => priorityQueue.find((item) => item.exceptionId === selectedId) ?? priorityQueue[0],
    [selectedId],
  );

  const evidenceFields = evidenceByExceptionId[selectedBreak.exceptionId] ?? [];
  const relatedCandidates = candidatesByExceptionId[selectedBreak.exceptionId] ?? [];

  return (
    <main className="min-h-screen bg-[#f4f6f8] text-slate-950">
      <section className="mx-auto flex max-w-[1500px] flex-col gap-6 px-6 py-6">
        <header className="rounded-[28px] bg-slate-950 px-8 py-7 text-white shadow-2xl shadow-slate-300">
          <div className="mb-3 text-xs font-bold uppercase tracking-[0.24em] text-amber-300">
            Cash Break Resolution Workbench
          </div>

          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="max-w-4xl text-4xl font-black tracking-tight">
                Resolve reconciliation breaks faster without giving automation the final word.
              </h1>
              <p className="mt-4 max-w-3xl text-base leading-7 text-slate-300">
                Deterministic matches are handled automatically. This workbench focuses
                analyst attention on unresolved breaks, candidate evidence, and controlled
                action logging.
              </p>
            </div>

            <div className="rounded-2xl border border-amber-300/30 bg-amber-300/10 px-5 py-4 text-sm text-amber-100">
              <div className="font-bold text-amber-200">Decision boundary</div>
              <div className="mt-1 leading-6">
                System recommends. Analyst decides. Action log records.
              </div>
            </div>
          </div>
        </header>

        <section className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)_360px]">
          <aside className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4">
              <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                Priority Queue
              </div>
              <h2 className="mt-2 text-2xl font-black">Next breaks to review</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Sorted by SLA pressure, priority, amount mismatch risk, and age.
              </p>
            </div>

            <div className="space-y-3">
              {priorityQueue.map((item) => (
                <QueueCard
                  key={item.exceptionId}
                  item={item}
                  active={item.exceptionId === selectedBreak.exceptionId}
                  onSelect={() => {
                    setSelectedId(item.exceptionId);
                    setDecision(null);
                  }}
                />
              ))}
            </div>
          </aside>

          <section className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6 flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                  Evidence Comparison
                </div>
                <h2 className="mt-2 text-3xl font-black">{selectedBreak.exceptionId}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Bank-side and ledger-side evidence are aligned by judgment dimension,
                  so the analyst can review differences without scanning raw CSV rows.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <PriorityPill value={selectedBreak.priority} />
                <StatusBadge value={selectedBreak.slaStatus} />
              </div>
            </div>

            <EvidenceComparison fields={evidenceFields} />
          </section>

          <aside className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-5">
              <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                Action Panel
              </div>
              <h2 className="mt-2 text-2xl font-black">Recommended next step</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Recommendations support the analyst. They do not close breaks automatically.
              </p>
            </div>

            <div className="rounded-2xl border border-red-200 bg-red-50 p-4">
              <div className="text-sm font-bold text-red-700">
                {selectedBreak.recommendedAction}
              </div>
              <p className="mt-2 text-sm leading-6 text-red-700">{selectedBreak.reason}</p>
            </div>

            <div className="mt-5 space-y-3">
              <button
                onClick={() => setDecision("Accepted recommendation")}
                className="w-full rounded-2xl bg-slate-950 px-4 py-3 text-sm font-bold text-white"
              >
                Accept recommendation
              </button>
              <button
                onClick={() => setDecision("Rejected recommendation")}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm font-bold text-slate-800"
              >
                Reject recommendation
              </button>
              <button
                onClick={() => setDecision("Requested more information")}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm font-bold text-slate-800"
              >
                Request info
              </button>
              <button
                onClick={() => setDecision("Added analyst note")}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm font-bold text-slate-800"
              >
                Add analyst note
              </button>
            </div>

            <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
              <div className="font-bold text-slate-900">Action log preview</div>
              <p className="mt-2">
                {decision
                  ? `${decision} for ${selectedBreak.exceptionId}. The system would record analyst identity, timestamp, recommendation source, and evidence snapshot.`
                  : "Choose an action to preview the audit log entry before submission."}
              </p>
            </div>
          </aside>
        </section>

        <section className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                Related Candidate Evidence
              </div>
              <h2 className="mt-2 text-2xl font-black">
                Possible explanations and match hypotheses
              </h2>
            </div>
            <p className="max-w-xl text-sm leading-6 text-slate-500">
              Candidates are not final matches. They help the analyst decide whether a break can be resolved.
            </p>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            {relatedCandidates.map((candidate) => (
              <CandidateCard key={candidate.source} candidate={candidate} />
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
