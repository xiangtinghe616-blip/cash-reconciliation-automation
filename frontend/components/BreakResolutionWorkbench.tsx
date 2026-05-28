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

type CandidateDecision = {
  source: Candidate["source"];
  action: "Review" | "Accept" | "Reject";
  confidence: string;
  rationale: string;
};

type BreakSide = {
  sourceRowId?: string;
  amount?: string;
  transactionDate?: string;
  accountId?: string;
  currency?: string;
};

type BreakPacket = {
  exceptionId: string;
  summary?: {
    exceptionId?: string;
    breakType?: string;
    priority?: string;
    slaStatus?: string;
    ageDays?: number;
    amountGap?: string;
    recommendedAction?: string;
    reason?: string;
    decisionBoundary?: string;
  };
  bankSide?: BreakSide;
  ledgerSide?: BreakSide;
  lifecycle?: Record<string, unknown>;
  actionRecommendation?: Record<string, unknown>;
  evidence?: EvidenceField[];
  relatedCandidates?: Candidate[];
  rawException?: Record<string, unknown>;
};

type WorkbenchData = {
  priorityQueue: BreakItem[];
  evidenceByExceptionId: Record<string, EvidenceField[]>;
  candidatesByExceptionId: Record<string, Candidate[]>;
  breakPacketsByExceptionId: Record<string, BreakPacket>;
};

const QUEUE_FILTERS: QueueFilter[] = [
  "All",
  "Breached SLA",
  "High Priority",
  "Amount Mismatch",
  "Candidate Available",
];

const fallbackWorkbenchData: WorkbenchData = {
  priorityQueue: fallbackPriorityQueue,
  evidenceByExceptionId: fallbackEvidenceByExceptionId,
  candidatesByExceptionId: fallbackCandidatesByExceptionId,
  breakPacketsByExceptionId: {},
};

function hasRelatedCandidate(
  exceptionId: string,
  candidatesByExceptionId: Record<string, Candidate[]>,
  breakPacketsByExceptionId: Record<string, BreakPacket>,
) {
  const candidateCount = (candidatesByExceptionId[exceptionId] ?? []).length;
  const packetCandidateCount =
    breakPacketsByExceptionId[exceptionId]?.relatedCandidates?.length ?? 0;

  return candidateCount + packetCandidateCount > 0;
}

function filterPriorityQueue(
  items: BreakItem[],
  candidatesByExceptionId: Record<string, Candidate[]>,
  breakPacketsByExceptionId: Record<string, BreakPacket>,
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
    hasRelatedCandidate(
      item.exceptionId,
      candidatesByExceptionId,
      breakPacketsByExceptionId,
    ),
  );
}

function queueFilterCount(
  items: BreakItem[],
  candidatesByExceptionId: Record<string, Candidate[]>,
  breakPacketsByExceptionId: Record<string, BreakPacket>,
  filter: QueueFilter,
) {
  return filterPriorityQueue(
    items,
    candidatesByExceptionId,
    breakPacketsByExceptionId,
    filter,
  ).length;
}

function statusPillClass(value: string) {
  if (value === "BREACHED" || value === "difference") {
    return {
      chip: "bg-red-50 text-red-800 ring-red-200",
      dot: "bg-red-600",
    };
  }

  if (value === "DUE_TODAY" || value === "missing") {
    return {
      chip: "bg-amber-50 text-amber-800 ring-amber-200",
      dot: "bg-amber-500",
    };
  }

  if (value === "WITHIN_SLA" || value === "match") {
    return {
      chip: "bg-emerald-50 text-emerald-800 ring-emerald-200",
      dot: "bg-emerald-600",
    };
  }

  return {
    chip: "bg-slate-100 text-slate-700 ring-slate-200",
    dot: "bg-slate-500",
  };
}

function StatusBadge({ value }: { value: string }) {
  const style = statusPillClass(value);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${style.chip}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      {value}
    </span>
  );
}

function PriorityPill({ value }: { value: string }) {
  const style =
    value === "High"
      ? "bg-slate-950 text-white ring-slate-950"
      : value === "Medium"
        ? "bg-slate-100 text-slate-800 ring-slate-300"
        : "bg-white text-slate-600 ring-slate-200";

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${style}`}
    >
      Priority: {value}
    </span>
  );
}

function EvidenceStatus({ value }: { value: string }) {
  const style = statusPillClass(value);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${style.chip}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      {value}
    </span>
  );
}

function QueueFilterChip({
  filter,
  count,
  active,
  disabled,
  onClick,
}: {
  filter: QueueFilter;
  count: number;
  active: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`rounded-full px-3 py-1.5 text-xs font-bold ring-1 transition ${
        active
          ? "bg-slate-950 text-white ring-slate-950"
          : disabled
            ? "cursor-not-allowed bg-slate-50 text-slate-300 ring-slate-100"
            : "bg-white text-slate-600 ring-slate-200 hover:bg-slate-50 hover:text-slate-950"
      }`}
    >
      {filter} <span className="ml-1 opacity-70">{count}</span>
    </button>
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
      type="button"
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
  selectedPacket,
}: {
  selectedBreak: BreakItem;
  fields: EvidenceField[];
  candidates: Candidate[];
  selectedPacket?: BreakPacket;
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
            {selectedPacket?.summary?.breakType ?? selectedBreak.breakType}
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
            {selectedPacket?.summary?.recommendedAction ?? selectedBreak.recommendedAction}
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

function BreakSideContext({
  bankSide,
  ledgerSide,
}: {
  bankSide?: BreakSide;
  ledgerSide?: BreakSide;
}) {
  if (!bankSide && !ledgerSide) {
    return null;
  }

  return (
    <div className="mb-5 grid gap-3 lg:grid-cols-2">
      <div className="rounded-2xl border border-slate-200 bg-white p-4">
        <div className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">
          Bank side
        </div>
        <div className="mt-3 space-y-2 text-sm text-slate-600">
          <div className="flex justify-between gap-3">
            <span>Source row</span>
            <span className="font-semibold text-slate-950">{bankSide?.sourceRowId ?? "N/A"}</span>
          </div>
          <div className="flex justify-between gap-3">
            <span>Amount</span>
            <span className="font-semibold text-slate-950">{bankSide?.amount ?? "N/A"}</span>
          </div>
          <div className="flex justify-between gap-3">
            <span>Date</span>
            <span className="font-semibold text-slate-950">
              {bankSide?.transactionDate ?? "N/A"}
            </span>
          </div>
          <div className="flex justify-between gap-3">
            <span>Account</span>
            <span className="font-semibold text-slate-950">{bankSide?.accountId ?? "N/A"}</span>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4">
        <div className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">
          Ledger side
        </div>
        <div className="mt-3 space-y-2 text-sm text-slate-600">
          <div className="flex justify-between gap-3">
            <span>Source row</span>
            <span className="font-semibold text-slate-950">
              {ledgerSide?.sourceRowId ?? "N/A"}
            </span>
          </div>
          <div className="flex justify-between gap-3">
            <span>Amount</span>
            <span className="font-semibold text-slate-950">{ledgerSide?.amount ?? "N/A"}</span>
          </div>
          <div className="flex justify-between gap-3">
            <span>Date</span>
            <span className="font-semibold text-slate-950">
              {ledgerSide?.transactionDate ?? "N/A"}
            </span>
          </div>
          <div className="flex justify-between gap-3">
            <span>Account</span>
            <span className="font-semibold text-slate-950">
              {ledgerSide?.accountId ?? "N/A"}
            </span>
          </div>
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

function formatRecordValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Not available";
  }

  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function DrillDownRecord({
  title,
  record,
  emptyMessage,
}: {
  title: string;
  record?: Record<string, unknown>;
  emptyMessage: string;
}) {
  const entries = Object.entries(record ?? {}).filter(
    ([, value]) => value !== null && value !== undefined && value !== "",
  );

  return (
    <details className="rounded-2xl border border-slate-200 bg-white p-4">
      <summary className="cursor-pointer text-sm font-bold text-slate-950">
        {title}
      </summary>

      {entries.length === 0 ? (
        <div className="mt-3 text-sm leading-6 text-slate-500">{emptyMessage}</div>
      ) : (
        <div className="mt-4 grid gap-2">
          {entries.map(([key, value]) => (
            <div
              key={key}
              className="grid gap-2 rounded-xl bg-slate-50 p-3 text-xs lg:grid-cols-[190px_1fr]"
            >
              <div className="font-bold uppercase tracking-[0.08em] text-slate-400">
                {key}
              </div>
              <div className="break-words font-semibold text-slate-700">
                {formatRecordValue(value)}
              </div>
            </div>
          ))}
        </div>
      )}
    </details>
  );
}

function DrillDownPanels({ packet }: { packet?: BreakPacket }) {
  if (!packet) {
    return (
      <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-500">
        No drill-down packet is available for this break.
      </div>
    );
  }

  return (
    <div className="mt-5 space-y-3">
      <div>
        <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
          Drill-down context
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Open these panels when you need to investigate the source row, lifecycle state,
          recommendation context, or raw exception record.
        </p>
      </div>

      <DrillDownRecord
        title="Lifecycle context"
        record={packet.lifecycle}
        emptyMessage="No lifecycle context is available."
      />

      <DrillDownRecord
        title="Action recommendation detail"
        record={packet.actionRecommendation}
        emptyMessage="No action recommendation detail is available."
      />

      <DrillDownRecord
        title="Raw exception detail"
        record={packet.rawException}
        emptyMessage="No raw exception detail is available."
      />
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
        <Button
          sentiment="neutral"
          appearance="bordered"
          onClick={() => onDecision("Review")}
        >
          Review
        </Button>
        <Button
          sentiment="accented"
          appearance="solid"
          onClick={() => onDecision("Accept")}
        >
          Accept
        </Button>
        <Button
          sentiment="neutral"
          appearance="bordered"
          onClick={() => onDecision("Reject")}
        >
          Reject
        </Button>
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
            breakPacketsByExceptionId: payload.breakPacketsByExceptionId ?? {},
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
        workbenchData.breakPacketsByExceptionId,
        queueFilter,
      ),
    [
      queueFilter,
      workbenchData.priorityQueue,
      workbenchData.candidatesByExceptionId,
      workbenchData.breakPacketsByExceptionId,
    ],
  );

  const queueFilterCounts = useMemo(
    () =>
      Object.fromEntries(
        QUEUE_FILTERS.map((filter) => [
          filter,
          queueFilterCount(
            workbenchData.priorityQueue,
            workbenchData.candidatesByExceptionId,
            workbenchData.breakPacketsByExceptionId,
            filter,
          ),
        ]),
      ) as Record<QueueFilter, number>,
    [
      workbenchData.priorityQueue,
      workbenchData.candidatesByExceptionId,
      workbenchData.breakPacketsByExceptionId,
    ],
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
      filteredPriorityQueue.find((item) => item.exceptionId === selectedId) ??
      filteredPriorityQueue[0] ??
      workbenchData.priorityQueue[0],
    [selectedId, filteredPriorityQueue, workbenchData.priorityQueue],
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

  const selectedPacket = workbenchData.breakPacketsByExceptionId[selectedBreak.exceptionId];
  const evidenceFields =
    selectedPacket?.evidence ??
    workbenchData.evidenceByExceptionId[selectedBreak.exceptionId] ??
    [];
  const relatedCandidates =
    selectedPacket?.relatedCandidates ??
    workbenchData.candidatesByExceptionId[selectedBreak.exceptionId] ??
    [];

  const displayedRecommendedAction =
    selectedPacket?.summary?.recommendedAction ?? selectedBreak.recommendedAction;
  const displayedReason = selectedPacket?.summary?.reason ?? selectedBreak.reason;
  const displayedDecisionBoundary =
    selectedPacket?.summary?.decisionBoundary ??
    "System recommendations and candidates support review. The analyst remains responsible for final disposition.";

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
              <div className="mt-1 leading-6">{displayedDecisionBoundary}</div>
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
              {QUEUE_FILTERS.map((filter) => {
                const count = queueFilterCounts[filter];

                return (
                  <QueueFilterChip
                    key={filter}
                    filter={filter}
                    count={count}
                    active={queueFilter === filter}
                    disabled={filter !== "All" && count === 0}
                    onClick={() => {
                      if (filter === "All" || count > 0) {
                        setQueueFilter(filter);
                      }
                    }}
                  />
                );
              })}
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
                      setCandidateDecision(null);
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
                <div className="mt-2 inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700 ring-1 ring-blue-200">
                  Packet: {selectedPacket ? "break packet v2" : "fallback evidence"}
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-500">
                  Bank-side and ledger-side evidence are aligned by judgment dimension,
                  so the analyst can review differences without scanning raw CSV rows.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <PriorityPill value={selectedPacket?.summary?.priority ?? selectedBreak.priority} />
                <StatusBadge value={selectedPacket?.summary?.slaStatus ?? selectedBreak.slaStatus} />
              </div>
            </div>

            <BreakSideContext
              bankSide={selectedPacket?.bankSide}
              ledgerSide={selectedPacket?.ledgerSide}
            />

            <EvidenceInsightSummary
              selectedBreak={selectedBreak}
              fields={evidenceFields}
              candidates={relatedCandidates}
              selectedPacket={selectedPacket}
            />

            <EvidenceComparison fields={evidenceFields} />

            <DrillDownPanels packet={selectedPacket} />
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
                {displayedRecommendedAction}
              </div>
              <p className="mt-2 text-sm leading-6 text-red-700">{displayedReason}</p>
            </div>

            <div className="mt-5 space-y-3">
              <Button
                sentiment="accented"
                appearance="solid"
                onClick={() => {
                  setDecision("Staged recommendation");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={{ width: "100%" }}
              >
                Stage recommendation
              </Button>
              <Button
                sentiment="neutral"
                appearance="bordered"
                onClick={() => {
                  setDecision("Rejected recommendation");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={{ width: "100%" }}
              >
                Reject recommendation
              </Button>
              <Button
                sentiment="neutral"
                appearance="bordered"
                onClick={() => {
                  setDecision("Requested more information");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={{ width: "100%" }}
              >
                Request information
              </Button>
              <Button
                sentiment="neutral"
                appearance="bordered"
                onClick={() => {
                  setDecision("Added analyst note");
                  setCandidateDecision(null);
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={{ width: "100%" }}
              >
                Add analyst note
              </Button>
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
