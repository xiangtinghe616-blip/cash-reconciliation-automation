export const ACTION_TRAIL_STORAGE_KEY = "cash-reconciliation-workbench.action-trail.v1";

export type DecisionType = "Action recommendation" | "Candidate decision";

export type CandidateSource = "Rule-based" | "Splink" | "Split-payment";

export type CandidateAction = "Review" | "Accept" | "Reject";

export type LocalActionRecord = {
  id: string;
  exceptionId: string;
  decisionType: DecisionType | string;
  actionType: string;
  proposedStatus: string;
  dispositionCode: string;
  actor: string;
  timestamp: string;
  analystNote: string;
  candidateSource?: CandidateSource;
  candidateAction?: CandidateAction;
  candidateConfidence?: string;
};

export type ActionLogPayloadV1 = {
  schemaVersion: "action-log-v1";
  exceptionId: string;
  actor: string;
  actionTs: string;
  decisionType: DecisionType | string;
  actionType: string;
  previousStatus: string;
  proposedStatus: string;
  dispositionCode: string;
  analystNote: string;
  evidenceSnapshotIncluded: boolean;
  candidateContext?: {
    source?: CandidateSource;
    action?: CandidateAction;
    confidence?: string;
  };
};

export function toActionLogPayloadV1(
  record: LocalActionRecord,
  previousStatus = "Open",
): ActionLogPayloadV1 {
  return {
    schemaVersion: "action-log-v1",
    exceptionId: record.exceptionId,
    actor: record.actor,
    actionTs: record.timestamp,
    decisionType: record.decisionType,
    actionType: record.actionType,
    previousStatus,
    proposedStatus: record.proposedStatus,
    dispositionCode: record.dispositionCode,
    analystNote: record.analystNote,
    evidenceSnapshotIncluded: true,
    candidateContext: record.candidateSource
      ? {
          source: record.candidateSource,
          action: record.candidateAction,
          confidence: record.candidateConfidence,
        }
      : undefined,
  };
}

export function isLocalActionRecordArray(
  value: unknown,
): value is LocalActionRecord[] {
  return (
    Array.isArray(value) &&
    value.every((item) => {
      if (!item || typeof item !== "object") {
        return false;
      }

      const record = item as Partial<LocalActionRecord>;

      return (
        typeof record.id === "string" &&
        typeof record.exceptionId === "string" &&
        typeof record.actionType === "string" &&
        typeof record.proposedStatus === "string" &&
        typeof record.dispositionCode === "string" &&
        typeof record.actor === "string" &&
        typeof record.timestamp === "string"
      );
    })
  );
}

