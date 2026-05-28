"use client";

import { Button } from "@salt-ds/core";
import { useEffect, useMemo, useState } from "react";
import {
  candidatesByExceptionId as fallbackCandidatesByExceptionId,
  evidenceByExceptionId as fallbackEvidenceByExceptionId,
  priorityQueue as fallbackPriorityQueue,
  type BreakItem,
  type Candidate,
  type EvidenceField,
} from "@/lib/demoData";

type QueueFilter =
  | "All"
  | "Breached SLA"
  | "High Priority"
  | "Amount Mismatch"
  | "Candidate Available";

const QUEUE_FILTERS: QueueFilter[] = [
  "All",
  "Breached SLA",
  "High Priority",
  "Amount Mismatch",
  "Candidate Available",
];

function hasRelatedCandidate(
  exceptionId: string,
  candidatesByExceptionId: Record<string, Candidate[]>,
) {
  return (candidatesByExceptionId[exceptionId] ?? []).length > 0;
}

function filterPriorityQueue(
  items: BreakItem[],
  candidatesByExceptionId: Record<string, Candidate[]>,
  filter: QueueFilter,
) {
  if (filter === "All") {
    return items;
  }

  if (filter === "Breached SLA") {
    return items.filter((item) => item.slaStatus === "BREACHED");
  }

  if (filter === "High Priority") {
    return items.filter((item) => item.priority === "High");
  }

  if (filter === "Amount Mismatch") {
    return items.filter((item) => item.breakType === "AMOUNT_MISMATCH");
  }

  return items.filter((item) =>
    hasRelatedCandidate(item.exceptionId, candidatesByExceptionId),
  );
}

type CandidateDecision = {
  source: Candidate["source"];
  action: "Review" | "Accept" | "Reject";
  confidence: string;
  rationale: string;
};


type WorkbenchData = {
  priorityQueue: BreakItem[];
  evidenceByExceptionId: Record<string, EvidenceField[]>;
  candidatesByExceptionId: Record<string, Candidate[]>;
};

const fallbackWorkbenchData: WorkbenchData = {
  priorityQueue: fallbackPriorityQueue,
  evidenceByExceptionId: fallbackEvidenceByExceptionId,
  candidatesByExceptionId: fallbackCandidatesByExceptionId,
};

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

function EvidenceInsightSummary({
  selectedBreak,
  fields,
  candidates,
}: {
  selectedBreak: BreakItem;
  fields: EvidenceField[];
  candidates: Candidate[];
}) {
  const amountField = fields.find((field) => field.field === "Amount");
  const dateField = fields.find((field) => field.field === "Transaction Date");
  const referenceField = fields.find((field) => field.field === "Reference");

  const differenceCount = fields.filter((field) => field.status === "difference").length;
  const missingCount = fields.filter((field) => field.status === "missing").length;
  const candidateSupport =
    candidates.length > 0 ? `${candidates.length} candidate source(s)` : "No candidate support";

  return (
    <div className="mb-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="mb-3 text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
        Review snapshot
      </div>

      <div className="grid gap-3 lg:grid-cols-4">
        <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
          <div className="text-xs font-semibold text-slate-500">Primary break</div>
          <div className="mt-1 text-sm font-bold text-slate-950">
            {selectedBreak.breakType}
          </div>
        </div>

        <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
          <div className="text-xs font-semibold text-slate-500">Differences</div>
          <div className="mt-1 text-sm font-bold text-slate-950">
            {differenceCount} difference(s), {missingCount} missing
          </div>
        </div>

        <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
          <div className="text-xs font-semibold text-slate-500">Candidate support</div>
          <div className="mt-1 text-sm font-bold text-slate-950">
            {candidateSupport}
          </div>
        </div>

        <div className="rounded-xl bg-white p-3 ring-1 ring-slate-200">
          <div className="text-xs font-semibold text-slate-500">Recommended action</div>
          <div className="mt-1 text-sm font-bold text-slate-950">
            {selectedBreak.recommendedAction}
          </div>
        </div>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        <div className="text-xs leading-5 text-slate-500">
          <span className="font-bold text-slate-700">Amount:</span>{" "}
          {amountField?.note ?? "No amount note available."}
        </div>
        <div className="text-xs leading-5 text-slate-500">
          <span className="font-bold text-slate-700">Timing:</span>{" "}
          {dateField?.note ?? "No timing note available."}
        </div>
        <div className="text-xs leading-5 text-slate-500">
          <span className="font-bold text-slate-700">Reference:</span>{" "}
          {referenceField?.note ?? "No reference note available."}
        </div>
      </div>
    </div>
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

function CandidateCard({
  candidate,
  selectedDecision,
  onDecision,
}: {
  candidate: Candidate;
  selectedDecision: CandidateDecision | null;
  onDecision: (action: CandidateDecision["action"]) => void;
}) {
  const sourceStyle =
    candidate.source === "Splink"
      ? "bg-blue-50 text-blue-700 ring-blue-200"
      : candidate.source === "Split-payment"
        ? "bg-amber-50 text-amber-700 ring-amber-200"
        : "bg-slate-100 text-slate-700 ring-slate-200";

  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center justify-between gap-3">
        <span className={`rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${sourceStyle}`}>
          {candidate.source}
        </span>
        <span className="text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
          Review only
        </span>
      </div>

      <div className="mt-4 text-2xl font-black">{candidate.confidence}</div>
      <p className="mt-3 text-sm leading-6 text-slate-600">{candidate.rationale}</p>

      <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3 text-xs leading-5 text-slate-500">
        Candidate evidence supports review prioritization. It does not confirm a match.
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2">
        <button
          type="button"
          onClick={() => onDecision("Review")}
          className="rounded-xl border border-slate-300 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-white"
        >
          Review
        </button>
        <button
          type="button"
          onClick={() => onDecision("Accept")}
          className="rounded-xl bg-slate-950 px-3 py-2 text-xs font-bold text-white"
        >
          Accept
        </button>
        <button
          type="button"
          onClick={() => onDecision("Reject")}
          className="rounded-xl border border-slate-300 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-white"
        >
          Reject
        </button>
      </div>

      {selectedDecision ? (
        <div className="mt-3 rounded-xl bg-blue-50 p-3 text-xs font-semibold text-blue-700 ring-1 ring-blue-200">
          Candidate decision staged: {selectedDecision.action}
        </div>
      ) : null}
    </div>
  );
}

export default function BreakResolutionWorkbench() {
  const [workbenchData, setWorkbenchData] = useState<WorkbenchData>(fallbackWorkbenchData);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [decision, setDecision] = useState<string | null>(null);
  const [decisionTimestamp, setDecisionTimestamp] = useState<string | null>(null);
  const [candidateDecision, setCandidateDecision] = useState<CandidateDecision | null>(null);
  const [queueFilter, setQueueFilter] = useState<QueueFilter>("All");
  const [dataSource, setDataSource] = useState("static fallback");
  const [isLoadingData, setIsLoadingData] = useState(true);

  useEffect(() => {
    async function loadWorkbenchData() {
      try {
        const response = await fetch("/demo-data/workbench-data.json", {
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error("Could not load generated workbench JSON.");
        }

        const payload = (await response.json()) as Partial<WorkbenchData>;

        if (
          Array.isArray(payload.priorityQueue) &&
          payload.priorityQueue.length > 0 &&
          payload.evidenceByExceptionId &&
          payload.candidatesByExceptionId
        ) {
          setWorkbenchData({
            priorityQueue: payload.priorityQueue,
            evidenceByExceptionId: payload.evidenceByExceptionId,
            candidatesByExceptionId: payload.candidatesByExceptionId,
          });
          setDataSource("generated v3 output");
        }
      } catch {
        setWorkbenchData(fallbackWorkbenchData);
        setDataSource("static fallback");
      } finally {
        setIsLoadingData(false);
      }
    }

    void loadWorkbenchData();
  }, []);

  const filteredPriorityQueue = useMemo(
    () =>
      filterPriorityQueue(
        workbenchData.priorityQueue,
        workbenchData.candidatesByExceptionId,
        queueFilter,
      ),
    [queueFilter, workbenchData.priorityQueue, workbenchData.candidatesByExceptionId],
  );

  useEffect(() => {
    if (filteredPriorityQueue.length === 0) {
      return;
    }

    const selectedStillExists = filteredPriorityQueue.some(
      (item) => item.exceptionId === selectedId,
    );

    if (!selectedId || !selectedStillExists) {
      setSelectedId(filteredPriorityQueue[0].exceptionId);
    }
  }, [selectedId, filteredPriorityQueue]);

  const selectedBreak = useMemo(
    () =>
      workbenchData.priorityQueue.find((item) => item.exceptionId === selectedId) ??
      workbenchData.priorityQueue[0],
    [selectedId, workbenchData.priorityQueue],
  );

  if (!selectedBreak) {
    return (
      <main className="min-h-screen bg-[#f4f6f8] p-8 text-slate-950">
        <div className="rounded-3xl bg-white p-8 shadow-sm">
          No workbench data available. Run the v3 pipeline and frontend exporter.
        </div>
      </main>
    );
  }

  const evidenceFields =
    workbenchData.evidenceByExceptionId[selectedBreak.exceptionId] ?? [];
  const relatedCandidates =
    workbenchData.candidatesByExceptionId[selectedBreak.exceptionId] ?? [];

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
              <div className="mt-3 text-xs text-amber-200/80">
                Data source: {isLoadingData ? "loading..." : dataSource}
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

            <div className="mb-4 flex flex-wrap gap-2">
              {QUEUE_FILTERS.map((filter) => (
                <button
                  key={filter}
                  type="button"
                  onClick={() => setQueueFilter(filter)}
                  className={`rounded-full px-3 py-1.5 text-xs font-bold transition ${
                    queueFilter === filter
                      ? "bg-slate-950 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            <div className="mb-3 text-xs font-semibold text-slate-500">
              Showing {filteredPriorityQueue.length} of {workbenchData.priorityQueue.length} breaks
            </div>

            <div className="space-y-3">
              {filteredPriorityQueue.length === 0 ? (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-500">
                  No breaks match this filter.
                </div>
              ) : (
                filteredPriorityQueue.map((item) => (
                  <QueueCard
                    key={item.exceptionId}
                    item={item}
                    active={item.exceptionId === selectedBreak.exceptionId}
                    onSelect={() => {
                      setSelectedId(item.exceptionId);
                      setDecision(null);
                      setDecisionTimestamp(null);
                    }}
                  />
                ))
              )}
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

            <EvidenceInsightSummary
              selectedBreak={selectedBreak}
              fields={evidenceFields}
              candidates={relatedCandidates}
            />

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
                onClick={() => {
                  setDecision("Staged recommendation");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                className="w-full rounded-2xl bg-slate-950 px-4 py-3 text-sm font-bold text-white"
              >
                Accept recommendation
              </button>
              <button
                onClick={() => {
                  setDecision("Rejected recommendation");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm font-bold text-slate-800"
              >
                Reject recommendation
              </button>
              <button
                onClick={() => {
                  setDecision("Requested more information");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm font-bold text-slate-800"
              >
                Request info
              </button>
              <button
                onClick={() => {
                  setDecision("Added analyst note");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm font-bold text-slate-800"
              >
                Add analyst note
              </button>
            </div>

            <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
              <div className="font-bold text-slate-900">Action log preview</div>

              {decision ? (
                <div className="mt-3 space-y-2">
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Exception</span>
                    <span className="font-semibold text-slate-900">{selectedBreak.exceptionId}</span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Decision type</span>
                    <span className="font-semibold text-slate-900">
                      {candidateDecision ? "Candidate decision" : "Action recommendation"}
                    </span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Decision</span>
                    <span className="font-semibold text-slate-900">{decision}</span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span className="text-slate-500">Timestamp</span>
                    <span className="text-right font-semibold text-slate-900">
                      {decisionTimestamp ?? "Pending"}
                    </span>
                  </div>
                  {candidateDecision ? (
                    <div className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-xs leading-5 text-blue-700">
                      <div className="font-bold">Candidate decision context</div>
                      <div>Source: {candidateDecision.source}</div>
                      <div>Action: {candidateDecision.action}</div>
                      <div>Confidence: {candidateDecision.confidence}</div>
                    </div>
                  ) : null}

                  <div className="rounded-xl border border-slate-200 bg-white p-3 text-xs leading-5 text-slate-500">
                    This preview would become a manual action log entry with analyst identity,
                    recommendation source, selected evidence, and disposition.
                  </div>
                </div>
              ) : (
                <p className="mt-2">
                  Choose an action to preview the audit log entry before submission.
                </p>
              )}
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

          {relatedCandidates.length === 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm leading-6 text-slate-500">
              No related candidate evidence is available for this break. Continue with
              exception evidence and action review.
            </div>
          ) : (
            <div className="grid gap-4 lg:grid-cols-3">
              {relatedCandidates.map((candidate) => (
                <CandidateCard
                  key={candidate.source}
                  candidate={candidate}
                  selectedDecision={
                    candidateDecision?.source === candidate.source ? candidateDecision : null
                  }
                  onDecision={(action) => {
                    const nextCandidateDecision = {
                      source: candidate.source,
                      action,
                      confidence: candidate.confidence,
                      rationale: candidate.rationale,
                    };

                    setCandidateDecision(nextCandidateDecision);
                    setDecision(`${action} ${candidate.source} candidate`);
                    setDecisionTimestamp(new Date().toISOString());
                  }}
                />
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
