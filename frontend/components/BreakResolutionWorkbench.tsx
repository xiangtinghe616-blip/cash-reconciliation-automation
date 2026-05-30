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

const actionButtonStyle = {
  width: "100%",
  minHeight: "40px",
  borderRadius: "12px",
  fontSize: "13px",
  fontWeight: 700,
  letterSpacing: "0",
  textTransform: "none",
  fontFamily: "inherit",
} as const;

const candidateButtonStyle = {
  width: "100%",
  minHeight: "34px",
  borderRadius: "10px",
  fontSize: "12px",
  fontWeight: 700,
  textTransform: "none",
  fontFamily: "inherit",
} as const;

function candidateCountForException(
  exceptionId: string,
  candidatesByExceptionId: Record<string, Candidate[]>,
  breakPacketsByExceptionId: Record<string, BreakPacket>,
) {
  const directCandidateCount = (candidatesByExceptionId[exceptionId] ?? []).length;
  const packetCandidateCount =
    breakPacketsByExceptionId[exceptionId]?.relatedCandidates?.length ?? 0;

  return Math.max(directCandidateCount, packetCandidateCount);
}

function hasRelatedCandidate(
  exceptionId: string,
  candidatesByExceptionId: Record<string, Candidate[]>,
  breakPacketsByExceptionId: Record<string, BreakPacket>,
) {
  return (
    candidateCountForException(
      exceptionId,
      candidatesByExceptionId,
      breakPacketsByExceptionId,
    ) > 0
  );
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
  staged,
  candidateCount,
  onSelect,
}: {
  item: BreakItem;
  active: boolean;
  staged: boolean;
  candidateCount: number;
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
        <div className="flex items-center gap-2">
          {staged ? (
            <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-bold text-blue-700 ring-1 ring-blue-200">
              Staged
            </span>
          ) : null}
          <StatusBadge value={item.slaStatus} />
        </div>
      </div>

      <div className={`mt-2 text-sm ${active ? "text-slate-300" : "text-slate-500"}`}>
        {item.breakType}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <PriorityPill value={item.priority} />
        <span className={`text-xs ${active ? "text-slate-300" : "text-slate-500"}`}>
          Age {item.ageDays}d
        </span>
        {candidateCount > 0 ? (
          <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-bold text-blue-700 ring-1 ring-blue-200">
            Candidates {candidateCount}
          </span>
        ) : null}
      </div>

      <div className={`mt-4 text-sm ${active ? "text-slate-200" : "text-slate-600"}`}>
        Recommended: <span className="font-semibold">{item.recommendedAction}</span>
      </div>
    </button>
  );
}

function evidenceStatusOrder(status: EvidenceField["status"]) {
  if (status === "missing") {
    return 0;
  }

  if (status === "difference") {
    return 1;
  }

  return 2;
}

function evidenceRowTone(status: EvidenceField["status"]) {
  if (status === "missing") {
    return "border-amber-200 bg-amber-50/60";
  }

  if (status === "difference") {
    return "border-red-200 bg-red-50/50";
  }

  return "border-slate-200 bg-slate-50";
}

function EvidenceTriagePanel({
  selectedBreak,
  fields,
  selectedPacket,
}: {
  selectedBreak: BreakItem;
  fields: EvidenceField[];
  selectedPacket?: BreakPacket;
}) {
  const missingFields = fields.filter((field) => field.status === "missing");
  const differenceFields = fields.filter((field) => field.status === "difference");
  const matchedFields = fields.filter((field) => field.status === "match");

  const primaryState =
    missingFields.length > 0
      ? "Incomplete evidence"
      : differenceFields.length > 0
        ? "Difference review"
        : "Evidence aligned";

  const primaryTone =
    missingFields.length > 0
      ? "border-amber-200 bg-amber-50 text-amber-800"
      : differenceFields.length > 0
        ? "border-red-200 bg-red-50 text-red-800"
        : "border-emerald-200 bg-emerald-50 text-emerald-800";

  const firstMissing = missingFields[0]?.field;
  const firstDifference = differenceFields[0]?.field;

  const reviewFocus =
    firstMissing
      ? `Start with missing ${firstMissing.toLowerCase()} evidence.`
      : firstDifference
        ? `Start with ${firstDifference.toLowerCase()} difference.`
        : "Evidence is aligned; review candidate and action context.";

  return (
    <div className="mb-5 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
            Evidence triage
          </div>
          <div className="mt-1 text-sm font-semibold text-slate-600">
            Review the highest-friction evidence before opening raw details.
          </div>
        </div>

        <span className={`rounded-full border px-3 py-1.5 text-xs font-bold ${primaryTone}`}>
          {primaryState}
        </span>
      </div>

      <div className="grid gap-3 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-semibold text-slate-500">Amount gap</div>
          <div className="mt-1 text-sm font-black text-slate-950">
            {selectedPacket?.summary?.amountGap ?? selectedBreak.amountGap}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-semibold text-slate-500">Missing fields</div>
          <div className="mt-1 text-sm font-black text-slate-950">
            {missingFields.length}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-semibold text-slate-500">Differences</div>
          <div className="mt-1 text-sm font-black text-slate-950">
            {differenceFields.length}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-semibold text-slate-500">Matched evidence</div>
          <div className="mt-1 text-sm font-black text-slate-950">
            {matchedFields.length}
          </div>
        </div>
      </div>

      <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs leading-5 text-slate-600">
        <span className="font-bold text-slate-800">Review focus:</span> {reviewFocus}
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
  const sortedFields = [...fields].sort(
    (first, second) =>
      evidenceStatusOrder(first.status) - evidenceStatusOrder(second.status),
  );

  return (
    <div className="space-y-3">
      {sortedFields.map((field) => (
        <div
          key={field.field}
          className={`grid gap-3 rounded-2xl border p-3 lg:grid-cols-[145px_1fr_1fr_110px] ${evidenceRowTone(field.status)}`}
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

function candidateDecisionGuardrail(action: CandidateDecision["action"]) {
  if (action === "Accept") {
    return {
      title: "Accept staged — control review required",
      message:
        "Accepting a candidate stages analyst approval. It does not automatically confirm reconciliation.",
      tone: "border-blue-200 bg-blue-50 text-blue-800",
    };
  }

  if (action === "Reject") {
    return {
      title: "Reject staged — review continues",
      message:
        "Rejecting a candidate keeps the exception open and records why this hypothesis was not accepted.",
      tone: "border-amber-200 bg-amber-50 text-amber-800",
    };
  }

  return {
    title: "Candidate under review",
    message:
      "Review mode keeps the candidate visible while the analyst checks supporting evidence.",
    tone: "border-slate-200 bg-white text-slate-600",
  };
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
    <div
      className={`rounded-2xl border p-4 transition ${
        selectedDecision
          ? "border-blue-300 bg-blue-50/60 ring-2 ring-blue-100"
          : "border-slate-200 bg-slate-50"
      }`}
    >
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
          style={candidateButtonStyle}
        >
          Review
        </Button>
        <Button
          sentiment="accented"
          appearance="solid"
          onClick={() => onDecision("Accept")}
          style={candidateButtonStyle}
        >
          Accept
        </Button>
        <Button
          sentiment="neutral"
          appearance="bordered"
          onClick={() => onDecision("Reject")}
          style={candidateButtonStyle}
        >
          Reject
        </Button>
      </div>

      {selectedDecision ? (
        <div
          className={`mt-3 rounded-xl border p-3 text-xs leading-5 ${
            candidateDecisionGuardrail(selectedDecision.action).tone
          }`}
        >
          <div className="font-bold">
            {candidateDecisionGuardrail(selectedDecision.action).title}
          </div>
          <div className="mt-1">
            {candidateDecisionGuardrail(selectedDecision.action).message}
          </div>
          <div className="mt-2 font-semibold">
            Candidate decision staged: {selectedDecision.action}
          </div>
        </div>
      ) : (
        <div className="mt-3 rounded-xl border border-slate-200 bg-white p-3 text-xs leading-5 text-slate-500">
          Accept or reject requires analyst rationale before it can be staged.
        </div>
      )}
    </div>
  );
}

function normalizeForCode(value: string) {
  return value.toUpperCase().replace(/[^A-Z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

function buildActionPreview({
  decision,
  candidateDecision,
  selectedBreak,
  decisionTimestamp,
  analystNote,
}: {
  decision: string | null;
  candidateDecision: CandidateDecision | null;
  selectedBreak: BreakItem;
  decisionTimestamp: string | null;
  analystNote: string;
}) {
  const decisionType = candidateDecision ? "Candidate decision" : "Action recommendation";

  let actionType = "NO_ACTION_SELECTED";
  let proposedStatus = "Open";
  let dispositionCode = "NO_DISPOSITION";
  let noteRequired = false;
  let guardrailMessage =
    "Choose an action to preview how the decision would be recorded.";

  if (candidateDecision) {
    actionType = `${candidateDecision.action.toUpperCase()}_${normalizeForCode(
      candidateDecision.source,
    )}_CANDIDATE`;
    dispositionCode = `CANDIDATE_${candidateDecision.action.toUpperCase()}`;

    if (candidateDecision.action === "Accept") {
      proposedStatus = "Candidate accepted - pending control review";
      noteRequired = true;
      guardrailMessage =
        "Accepting a candidate requires analyst rationale and remains pending control review.";
    } else if (candidateDecision.action === "Reject") {
      proposedStatus = "Candidate rejected - continue exception review";
      noteRequired = true;
      guardrailMessage =
        "Rejecting a candidate requires analyst rationale so the review trail explains why the hypothesis was not accepted.";
    } else {
      proposedStatus = "Candidate under review";
      guardrailMessage =
        "Review mode keeps the candidate staged for analyst attention without changing exception status.";
    }
  } else if (decision?.includes("Staged recommendation")) {
    actionType = "STAGE_RECOMMENDATION";
    proposedStatus = "Recommendation staged";
    dispositionCode = "RECOMMENDATION_STAGED";
    guardrailMessage =
      "Staging a recommendation records analyst intent but does not close the break.";
  } else if (decision?.includes("Rejected recommendation")) {
    actionType = "REJECT_RECOMMENDATION";
    proposedStatus = "Recommendation rejected";
    dispositionCode = "RECOMMENDATION_REJECTED";
    noteRequired = true;
    guardrailMessage =
      "Rejecting a system recommendation requires analyst rationale.";
  } else if (decision?.includes("Requested more information")) {
    actionType = "REQUEST_INFORMATION";
    proposedStatus = "Information requested";
    dispositionCode = "INFO_REQUESTED";
    noteRequired = true;
    guardrailMessage =
      "Information requests require a note describing what is missing.";
  } else if (decision?.includes("Added analyst note")) {
    actionType = "ADD_ANALYST_NOTE";
    proposedStatus = "Analyst note added";
    dispositionCode = "NOTE_ADDED";
    noteRequired = true;
    guardrailMessage =
      "Analyst-note actions require note content before staging.";
  }

  const canStageAction = Boolean(decision) && (!noteRequired || analystNote.trim().length > 0);

  return {
    exceptionId: selectedBreak.exceptionId,
    decisionType,
    actionType,
    previousStatus: "Open",
    proposedStatus,
    dispositionCode,
    actor: "demo_analyst",
    timestamp: decisionTimestamp ?? "Pending",
    noteRequired,
    analystNote,
    evidenceSnapshotIncluded: Boolean(decision),
    canStageAction,
    guardrailMessage,
  };
}


export default function BreakResolutionWorkbench() {
  const [workbenchData, setWorkbenchData] = useState<WorkbenchData>(fallbackWorkbenchData);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [decision, setDecision] = useState<string | null>(null);
  const [decisionTimestamp, setDecisionTimestamp] = useState<string | null>(null);
  const [candidateDecision, setCandidateDecision] = useState<CandidateDecision | null>(null);
  const [analystNote, setAnalystNote] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [hideStaged, setHideStaged] = useState(false);
  const [stagedExceptionIds, setStagedExceptionIds] = useState<string[]>([]);
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

  const visiblePriorityQueue = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return filteredPriorityQueue.filter((item) => {
      const matchesSearch =
        normalizedSearch.length === 0 ||
        item.exceptionId.toLowerCase().includes(normalizedSearch) ||
        item.breakType.toLowerCase().includes(normalizedSearch);

      const matchesStaged =
        !hideStaged || !stagedExceptionIds.includes(item.exceptionId);

      return matchesSearch && matchesStaged;
    });
  }, [filteredPriorityQueue, hideStaged, searchTerm, stagedExceptionIds]);

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
    if (visiblePriorityQueue.length === 0) {
      return;
    }

    const selectedStillExists = visiblePriorityQueue.some(
      (item) => item.exceptionId === selectedId,
    );

    if (!selectedId || !selectedStillExists) {
      setSelectedId(visiblePriorityQueue[0].exceptionId);
    }
  }, [selectedId, visiblePriorityQueue]);

  const selectedBreak = useMemo(
    () =>
      visiblePriorityQueue.find((item) => item.exceptionId === selectedId) ??
      visiblePriorityQueue[0] ??
      workbenchData.priorityQueue[0],
    [selectedId, visiblePriorityQueue, workbenchData.priorityQueue],
  );

  const currentVisibleIndex = visiblePriorityQueue.findIndex(
    (item) => item.exceptionId === selectedBreak?.exceptionId,
  );
  const safeVisibleIndex = currentVisibleIndex >= 0 ? currentVisibleIndex : 0;
  const nextVisibleBreak =
    visiblePriorityQueue.length > 1
      ? visiblePriorityQueue[(safeVisibleIndex + 1) % visiblePriorityQueue.length]
      : null;
  const stagedCount = stagedExceptionIds.length;

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

  function scrollToCandidateEvidence() {
    document
      .getElementById("candidate-evidence-preview")
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  const displayedRecommendedAction =
    selectedPacket?.summary?.recommendedAction ?? selectedBreak.recommendedAction;
  const displayedReason = selectedPacket?.summary?.reason ?? selectedBreak.reason;
  const displayedDecisionBoundary =
    selectedPacket?.summary?.decisionBoundary ??
    "System recommendations and candidates support review. The analyst remains responsible for final disposition.";

  const actionPreview = buildActionPreview({
    decision,
    candidateDecision,
    selectedBreak,
    decisionTimestamp,
    analystNote,
  });

  return (
    <main className="min-h-screen bg-[#f4f6f8] text-slate-950">
      <section className="mx-auto flex max-w-[1500px] flex-col gap-5 px-4 py-4 xl:px-6">
        <header className="rounded-[20px] border border-slate-800 bg-slate-950 px-5 py-4 text-white shadow-lg shadow-slate-300">
          <div className="mb-2 text-[11px] font-bold uppercase tracking-[0.24em] text-amber-300">
            Cash Break Resolution Workbench
          </div>

          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="max-w-4xl text-2xl font-black tracking-tight lg:text-[28px]">
                Resolve reconciliation breaks faster without giving automation the final word.
              </h1>
              <p className="mt-2 max-w-3xl text-xs leading-5 text-slate-300">
                Deterministic matches are handled automatically. This workbench focuses
                analyst attention on unresolved breaks, candidate evidence, and controlled
                action logging.
              </p>
            </div>

            <div className="max-w-[560px] rounded-2xl border border-amber-300/25 bg-amber-300/10 px-4 py-3 text-xs text-amber-100">
              <div className="font-bold text-amber-200">Decision boundary</div>
              <div className="mt-1 leading-6">{displayedDecisionBoundary}</div>
              <div className="mt-3 text-xs text-amber-200/80">
                Data source: {isLoadingData ? "loading..." : dataSource}
              </div>
            </div>
          </div>
        </header>

        <section className="grid gap-5 xl:grid-cols-[340px_minmax(0,1fr)_340px]">
          <aside className="rounded-[22px] border border-slate-200 bg-white p-4 shadow-sm xl:sticky xl:top-4 xl:self-start">
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

            <div className="mb-4 space-y-3">
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Search exception id or break type..."
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-800 outline-none ring-slate-300 placeholder:text-slate-400 focus:ring-2"
              />

              <div className="flex items-center justify-between gap-3">
                <label className="flex items-center gap-2 text-xs font-bold text-slate-600">
                  <input
                    type="checkbox"
                    checked={hideStaged}
                    onChange={(event) => setHideStaged(event.target.checked)}
                  />
                  Hide staged
                </label>

                <button
                  type="button"
                  disabled={!nextVisibleBreak}
                  onClick={() => {
                    if (!nextVisibleBreak) {
                      return;
                    }

                    setSelectedId(nextVisibleBreak.exceptionId);
                    setDecision(null);
                    setDecisionTimestamp(null);
                    setCandidateDecision(null);
                    setAnalystNote("");
                  }}
                  className={`rounded-full px-3 py-1.5 text-xs font-bold ring-1 ${
                    nextVisibleBreak
                      ? "bg-white text-slate-700 ring-slate-200 hover:bg-slate-50"
                      : "cursor-not-allowed bg-slate-50 text-slate-300 ring-slate-100"
                  }`}
                >
                  Next break
                </button>
              </div>
            </div>

            <div className="mb-3 text-xs font-semibold text-slate-500">
              Showing {visiblePriorityQueue.length} of {filteredPriorityQueue.length} filtered breaks
              {" "}· total {workbenchData.priorityQueue.length}
              {" "}· staged {stagedCount}
            </div>

            <div className="max-h-[70vh] space-y-3 overflow-y-auto pr-1">
              {visiblePriorityQueue.length === 0 ? (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-500">
                  No breaks match this filter.
                </div>
              ) : (
                visiblePriorityQueue.map((item) => (
                  <QueueCard
                    key={item.exceptionId}
                    item={item}
                    active={item.exceptionId === selectedBreak.exceptionId}
                    staged={stagedExceptionIds.includes(item.exceptionId)}
                    candidateCount={candidateCountForException(
                      item.exceptionId,
                      workbenchData.candidatesByExceptionId,
                      workbenchData.breakPacketsByExceptionId,
                    )}
                    onSelect={() => {
                      setSelectedId(item.exceptionId);
                      setDecision(null);
                      setDecisionTimestamp(null);
                      setCandidateDecision(null);
                      setAnalystNote("");
                    }}
                  />
                ))
              )}
            </div>
          </aside>

          <section className="rounded-[22px] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-6 flex flex-col gap-4 border-b border-slate-200 pb-5 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                  Active Break Review
                </div>
                <h2 className="mt-2 text-2xl font-black">{selectedBreak.exceptionId}</h2>
                <div className="mt-2 inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700 ring-1 ring-blue-200">
                  Packet: {selectedPacket ? "break packet v2" : "fallback evidence"}
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-500">
                  Bank-side and ledger-side evidence are organized by review dimension so the analyst can move from signal to decision without scanning raw CSV rows.
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

            <EvidenceTriagePanel
              selectedBreak={selectedBreak}
              fields={evidenceFields}
              selectedPacket={selectedPacket}
            />

            {relatedCandidates.length > 0 ? (
              <div
                id="candidate-evidence-preview"
                className="mb-5 rounded-2xl border border-blue-200 bg-blue-50/60 p-4"
              >
                <div className="mb-3 flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
                  <div>
                    <div className="text-xs font-bold uppercase tracking-[0.18em] text-blue-700">
                      Candidate evidence
                    </div>
                    <div className="mt-1 text-sm font-semibold text-blue-900">
                      Review candidate hypotheses before staging a candidate decision.
                    </div>
                  </div>
                  <div className="text-xs font-bold text-blue-700">
                    {relatedCandidates.length} candidate source(s)
                  </div>
                </div>

                <div className="grid gap-3 lg:grid-cols-2">
                  {relatedCandidates.slice(0, 2).map((candidate) => (
                    <CandidateCard
                      key={`preview-${candidate.source}`}
                      candidate={candidate}
                      selectedDecision={
                        candidateDecision?.source === candidate.source
                          ? candidateDecision
                          : null
                      }
                      onDecision={(action) => {
                        const nextCandidateDecision = {
                          source: candidate.source,
                          action,
                          confidence: candidate.confidence,
                          rationale: candidate.rationale,
                        };

                        setCandidateDecision(nextCandidateDecision);
                        setAnalystNote("");
                        setDecision(`${action} ${candidate.source} candidate`);
                        setDecisionTimestamp(new Date().toISOString());
                      }}
                    />
                  ))}
                </div>
              </div>
            ) : null}

            <EvidenceComparison fields={evidenceFields} />

            <DrillDownPanels packet={selectedPacket} />
          </section>

          <aside className="rounded-[22px] border border-slate-200 bg-white p-4 shadow-sm xl:sticky xl:top-4 xl:self-start">
            <div className="mb-5">
              <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                Action Panel
              </div>
              <h2 className="mt-2 text-xl font-black">Action workflow</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Stage analyst actions with note requirements and audit-style preview.
              </p>
            </div>

            <div className="rounded-2xl border border-red-200 bg-red-50/70 p-4">
              <div className="text-sm font-bold text-red-700">
                {displayedRecommendedAction}
              </div>
              <p className="mt-2 text-sm leading-6 text-red-700">{displayedReason}</p>
            </div>

            {candidateDecision ? (
              <div className="mt-5 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm leading-6 text-blue-800">
                <div className="text-xs font-bold uppercase tracking-[0.16em] text-blue-600">
                  Selected candidate
                </div>
                <div className="mt-2 grid gap-1">
                  <div className="flex justify-between gap-3">
                    <span>Source</span>
                    <span className="font-bold">{candidateDecision.source}</span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span>Action</span>
                    <span className="font-bold">{candidateDecision.action}</span>
                  </div>
                  <div className="flex justify-between gap-3">
                    <span>Confidence</span>
                    <span className="font-bold">{candidateDecision.confidence}</span>
                  </div>
                </div>
                <p className="mt-3 text-xs leading-5 text-blue-700">
                  Candidate decisions are staged as analyst actions. They do not automatically
                  confirm reconciliation.
                </p>
              </div>
            ) : null}

            {relatedCandidates.length > 0 ? (
              <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm leading-6 text-blue-800">
                <div className="font-bold">Candidate evidence available</div>
                <p className="mt-1 text-xs leading-5 text-blue-700">
                  This break has related candidate evidence. Review it before staging a
                  candidate decision.
                </p>
                <button
                  type="button"
                  onClick={scrollToCandidateEvidence}
                  className="mt-3 rounded-full bg-blue-700 px-3 py-1.5 text-xs font-bold text-white"
                >
                  View candidate evidence
                </button>
              </div>
            ) : null}

            <div className="mt-5">
              <div className="mb-2 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
                Stage analyst action
              </div>
              <div className="space-y-3">
              <Button
                sentiment="accented"
                appearance="solid"
                onClick={() => {
                  setDecision("Staged recommendation");
                  setCandidateDecision(null);
                  setAnalystNote("");
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={actionButtonStyle}
              >
                Stage recommendation
              </Button>
              <Button
                sentiment="neutral"
                appearance="bordered"
                onClick={() => {
                  setDecision("Rejected recommendation");
                  setCandidateDecision(null);
                  setAnalystNote("");
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={actionButtonStyle}
              >
                Reject recommendation
              </Button>
              <Button
                sentiment="neutral"
                appearance="bordered"
                onClick={() => {
                  setDecision("Requested more information");
                  setCandidateDecision(null);
                  setAnalystNote("");
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={actionButtonStyle}
              >
                Request information
              </Button>
              <Button
                sentiment="neutral"
                appearance="bordered"
                onClick={() => {
                  setDecision("Added analyst note");
                  setCandidateDecision(null);
                  setAnalystNote("");
                  setDecisionTimestamp(new Date().toISOString());
                }}
                style={actionButtonStyle}
              >
                Add analyst note
              </Button>
              </div>
            </div>

            <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
              <div className="font-bold text-slate-900">Action log preview</div>

              {decision ? (
                <div className="mt-3 space-y-3">
                  <div className="grid gap-2 rounded-xl border border-slate-200 bg-white p-3 text-xs">
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Exception</span>
                      <span className="font-semibold text-slate-900">
                        {actionPreview.exceptionId}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Decision type</span>
                      <span className="font-semibold text-slate-900">
                        {actionPreview.decisionType}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Action type</span>
                      <span className="text-right font-semibold text-slate-900">
                        {actionPreview.actionType}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Previous status</span>
                      <span className="font-semibold text-slate-900">
                        {actionPreview.previousStatus}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Proposed status</span>
                      <span className="text-right font-semibold text-slate-900">
                        {actionPreview.proposedStatus}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Disposition code</span>
                      <span className="text-right font-semibold text-slate-900">
                        {actionPreview.dispositionCode}
                      </span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-slate-500">Timestamp</span>
                      <span className="text-right font-semibold text-slate-900">
                        {actionPreview.timestamp}
                      </span>
                    </div>
                  </div>

                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-800">
                    <div className="font-bold">Workflow guardrail</div>
                    <div className="mt-1">{actionPreview.guardrailMessage}</div>
                  </div>

                  {candidateDecision ? (
                    <div className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-xs leading-5 text-blue-700">
                      <div className="font-bold">Candidate decision context</div>
                      <div>Source: {candidateDecision.source}</div>
                      <div>Action: {candidateDecision.action}</div>
                      <div>Confidence: {candidateDecision.confidence}</div>
                    </div>
                  ) : null}

                  <label className="block">
                    <div className="mb-1 flex items-center justify-between text-xs font-bold text-slate-700">
                      <span>Analyst note</span>
                      <span className={actionPreview.noteRequired ? "text-red-700" : "text-slate-400"}>
                        {actionPreview.noteRequired ? "Required" : "Optional"}
                      </span>
                    </div>
                    <textarea
                      value={analystNote}
                      onChange={(event) => setAnalystNote(event.target.value)}
                      placeholder="Add rationale, follow-up request, or review note..."
                      className="min-h-24 w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-800 outline-none ring-slate-300 placeholder:text-slate-400 focus:ring-2"
                    />
                  </label>

                  <div className="rounded-xl border border-slate-200 bg-white p-3 text-xs leading-5 text-slate-500">
                    Evidence snapshot included:{" "}
                    <span className="font-bold text-slate-900">
                      {actionPreview.evidenceSnapshotIncluded ? "Yes" : "No"}
                    </span>
                  </div>

                  <button
                    type="button"
                    disabled={!actionPreview.canStageAction}
                    onClick={() => {
                      if (!actionPreview.canStageAction) {
                        return;
                      }

                      setStagedExceptionIds((current) =>
                        current.includes(selectedBreak.exceptionId)
                          ? current
                          : [...current, selectedBreak.exceptionId],
                      );
                    }}
                    className={`w-full rounded-2xl px-4 py-3 text-sm font-bold ${
                      actionPreview.canStageAction
                        ? "bg-slate-950 text-white"
                        : "cursor-not-allowed bg-slate-200 text-slate-400"
                    }`}
                  >
                    Mark action as staged locally
                  </button>

                  {!actionPreview.canStageAction ? (
                    <div className="text-xs leading-5 text-red-700">
                      Analyst note is required before this action can be staged.
                    </div>
                  ) : null}
                </div>
              ) : (
                <p className="mt-2">
                  Choose an action to preview the audit log entry before submission.
                </p>
              )}
            </div>

          </aside>
        </section>

        <section id="related-candidate-evidence" className="rounded-[22px] border border-slate-200 bg-white p-5 shadow-sm">
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
              Candidates are not final matches. Choose Review, Accept, or Reject to stage
              candidate context in the Action Panel and action log preview.
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
                    setAnalystNote("");
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
