# Action Log Schema v1

## Purpose

The action log schema defines how analyst decisions should be represented when the workbench moves from frontend-only staged actions to a persisted review workflow.

The current Next.js workbench only stages actions locally. This schema describes the payload shape that a future API or persistence layer should accept.

## Control Principle

System recommends.

Analyst decides.

Action log records.

Candidate evidence and system recommendations are not final reconciliation decisions until a human analyst stages and records an action.

## Action Log Payload v1

Type shape:

    type ActionLogPayloadV1 = {
      schemaVersion: "action-log-v1";
      exceptionId: string;
      actor: string;
      actionTs: string;
      decisionType: "Action recommendation" | "Candidate decision" | string;
      actionType: string;
      previousStatus: string;
      proposedStatus: string;
      dispositionCode: string;
      analystNote: string;
      evidenceSnapshotIncluded: boolean;
      candidateContext?: {
        source?: "Rule-based" | "Splink" | "Split-payment";
        action?: "Review" | "Accept" | "Reject";
        confidence?: string;
      };
    };

## Required Fields

Required for all action log records:

- schemaVersion
- exceptionId
- actor
- actionTs
- decisionType
- actionType
- previousStatus
- proposedStatus
- dispositionCode
- analystNote
- evidenceSnapshotIncluded

## Candidate Decision Rules

Candidate Review:

- Does not require analyst note.
- Does not resolve the exception.
- Keeps the candidate staged for analyst attention.

Candidate Accept:

- Requires analyst note.
- Does not automatically confirm reconciliation.
- Proposed status should indicate pending control review.

Candidate Reject:

- Requires analyst note.
- Keeps the exception open.
- Records why the candidate hypothesis was not accepted.

## Future API Direction

A future API endpoint could accept:

    POST /api/actions

With payload:

    ActionLogPayloadV1

The API should validate:

- required fields
- note requirement for accept or reject decisions
- candidate context for candidate decisions
- evidence snapshot presence
- allowed disposition codes
- valid exception ID

## Current Limitation

The current frontend does not persist actions.

All staged actions are local UI state only.
