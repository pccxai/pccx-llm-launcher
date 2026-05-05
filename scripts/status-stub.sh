#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/status-stub.sh — launcher state summary
# Default mode: local scaffold output, no external calls, always exits 0.
#
# Runtime readiness summary (explicit opt-in, read-only local data):
#   --include-runtime-readiness
#
# Device/session status panel (explicit opt-in, read-only local data):
#   --include-device-session
#
# Chat/session status and lifecycle plan (explicit opt-in, read-only local data):
#   --include-chat-session
#
# Chat surface layout/chrome plan (explicit opt-in, read-only local data):
#   --include-chat-surface-layout
#
# Chat empty-state display boundary (explicit opt-in, read-only local data):
#   --include-chat-empty-state
#
# Chat local-only/cloud-block policy (explicit opt-in, read-only local data):
#   --include-chat-local-only-policy
#
# Chat preferences/settings boundary (explicit opt-in, read-only local data):
#   --include-chat-preferences
#
# Chat session index/sidebar plan (explicit opt-in, read-only local data):
#   --include-chat-session-index
#
# Chat session-store policy (explicit opt-in, read-only local data):
#   --include-chat-session-store-policy
#
# Chat session-title display policy (explicit opt-in, read-only local data):
#   --include-chat-session-title-policy
#
# Chat model status display plan (explicit opt-in, read-only local data):
#   --include-chat-model-status
#
# Chat model-selection policy boundary (explicit opt-in, read-only local data):
#   --include-chat-model-selection-policy
#
# Chat context-window/tokenization policy boundary (explicit opt-in, read-only local data):
#   --include-chat-context-policy
#
# Chat model-load request boundary (explicit opt-in, read-only local data):
#   --include-chat-model-load-request
#
# Chat readiness checks and recovery actions (explicit opt-in, read-only local data):
#   --include-chat-readiness
#
# Chat composer controls and validation state (explicit opt-in, read-only local data):
#   --include-chat-composer
#
# Chat send-result display boundary (explicit opt-in, read-only local data):
#   --include-chat-send-result
#
# Chat transcript retention/export policy (explicit opt-in, read-only local data):
#   --include-chat-transcript-policy
#
# Chat audit-event metadata boundary (explicit opt-in, read-only local data):
#   --include-chat-audit-event
#
# Chat error taxonomy display boundary (explicit opt-in, read-only local data):
#   --include-chat-error-taxonomy
#
# Chat response stream display boundary (explicit opt-in, read-only local data):
#   --include-chat-response-stream
#
# Chat message-list display boundary (explicit opt-in, read-only local data):
#   --include-chat-message-list
#
# Chat action-bar controls boundary (explicit opt-in, read-only local data):
#   --include-chat-action-bar
#
# Chat clipboard-policy boundary (explicit opt-in, read-only local data):
#   --include-chat-clipboard-policy
#
# Chat redaction-policy boundary (explicit opt-in, read-only local data):
#   --include-chat-redaction-policy
#
# Chat attachment-policy boundary (explicit opt-in, read-only local data):
#   --include-chat-attachment-policy
#
# Chat shortcut-map boundary (explicit opt-in, read-only local data):
#   --include-chat-shortcut-map
#
# Chat status-summary aggregate (explicit opt-in, read-only local data):
#   --include-chat-status-summary
#
# Chat review-packet aggregate (explicit opt-in, read-only local data):
#   --include-chat-review-packet
#
# Chat implementation gap matrix (explicit opt-in, read-only local data):
#   --include-chat-gap-matrix
#
# Chat evidence manifest (explicit opt-in, read-only local data):
#   --include-chat-evidence-manifest
#
# pccx-lab backend (explicit opt-in):
#   --backend pccx-lab        call pccx-lab status --format json
#   PCCX_LAB_BIN              override path to pccx-lab binary (takes priority over PATH)
#
# No silent fallback: if --backend pccx-lab is requested and the binary
# cannot be found or fails, the script exits non-zero with a clear error.

set -u

INFO()  { printf '[INFO]  %s\n' "$*"; }
NOTE()  { printf '[NOTE]  %s\n' "$*"; }
ERROR() { printf '[ERROR] %s\n' "$*" >&2; }
HEAD()  { printf '\n=== %s ===\n' "$*"; }

BACKEND=""
INCLUDE_RUNTIME_READINESS="0"
INCLUDE_DEVICE_SESSION="0"
INCLUDE_CHAT_SESSION="0"
INCLUDE_CHAT_SURFACE_LAYOUT="0"
INCLUDE_CHAT_EMPTY_STATE="0"
INCLUDE_CHAT_LOCAL_ONLY_POLICY="0"
INCLUDE_CHAT_PREFERENCES="0"
INCLUDE_CHAT_SESSION_INDEX="0"
INCLUDE_CHAT_SESSION_STORE_POLICY="0"
INCLUDE_CHAT_SESSION_TITLE_POLICY="0"
INCLUDE_CHAT_MODEL_STATUS="0"
INCLUDE_CHAT_MODEL_SELECTION_POLICY="0"
INCLUDE_CHAT_CONTEXT_POLICY="0"
INCLUDE_CHAT_MODEL_LOAD_REQUEST="0"
INCLUDE_CHAT_READINESS="0"
INCLUDE_CHAT_COMPOSER="0"
INCLUDE_CHAT_SEND_RESULT="0"
INCLUDE_CHAT_TRANSCRIPT_POLICY="0"
INCLUDE_CHAT_AUDIT_EVENT="0"
INCLUDE_CHAT_ERROR_TAXONOMY="0"
INCLUDE_CHAT_RESPONSE_STREAM="0"
INCLUDE_CHAT_MESSAGE_LIST="0"
INCLUDE_CHAT_ACTION_BAR="0"
INCLUDE_CHAT_CLIPBOARD_POLICY="0"
INCLUDE_CHAT_REDACTION_POLICY="0"
INCLUDE_CHAT_ATTACHMENT_POLICY="0"
INCLUDE_CHAT_SHORTCUT_MAP="0"
INCLUDE_CHAT_STATUS_SUMMARY="0"
INCLUDE_CHAT_REVIEW_PACKET="0"
INCLUDE_CHAT_GAP_MATRIX="0"
INCLUDE_CHAT_EVIDENCE_MANIFEST="0"

print_chat_status_summary_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_STATUS_SUMMARY_STUB="$ROOT_DIR/scripts/chat-status-summary-stub.sh"

    if [ ! -f "$CHAT_STATUS_SUMMARY_STUB" ]; then
        ERROR "chat status summary stub not found: $CHAT_STATUS_SUMMARY_STUB"
        return 1
    fi

    if ! CHAT_STATUS_SUMMARY_JSON="$(bash "$CHAT_STATUS_SUMMARY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat status summary stub failed"
        printf '%s\n' "$CHAT_STATUS_SUMMARY_JSON" >&2
        return 1
    fi

    if ! CHAT_STATUS_SUMMARY_TEXT="$(
        printf '%s\n' "$CHAT_STATUS_SUMMARY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
cards = " ".join(
    "{}={}:{}".format(card["cardId"], card["state"], card["severity"])
    for card in data["statusCards"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)
actions = " ".join(
    "{}={}:{}".format(action["actionId"], action["state"], str(action["enabled"]).lower())
    for action in data["nextActions"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-status-summary-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/session-store/config/model/runtime/hardware/provider/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  overall   : {}".format(data["overallState"]))
print("[INFO]  surface   : {}".format(data["surfaceState"]))
print("[INFO]  session   : {}".format(data["sessionState"]))
print("[INFO]  modelState: {}".format(data["modelState"]))
print("[INFO]  runtime   : {}".format(data["runtimeState"]))
print("[INFO]  send      : {}".format(data["sendState"]))
print("[INFO]  content   : {}".format(data["contentState"]))
print("[INFO]  privacy   : {}".format(data["privacyState"]))
print("[INFO]  evidence  : {}".format(data["evidenceState"]))
print("[INFO]  cards      : {}".format(cards))
print("[INFO]  blocked    : {}".format(blocked))
print("[INFO]  actions    : {}".format(actions))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "statusSummaryOnly={} aggregatesCheckedFixturesOnly={} "
    "promptCapture={} promptRead={} promptContentIncluded={} "
    "responseContentIncluded={} transcriptContentIncluded={} "
    "messageBodiesIncluded={} sessionStoreRead={} configRead={} "
    "environmentRead={} providerConfigRead={} modelAssetRead={} "
    "modelLoadAttempted={} modelExecution={} runtimeExecution={} "
    "responseGenerated={} sendEnabled={} kv260Access={} hardwareAccess={} "
    "networkCalls={} providerCalls={} cloudCalls={} executesPccxLab={} "
    "executesSystemverilogIde={} releaseOrTagAction={} settingsChange={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["statusSummaryOnly"]),
        b(flags["aggregatesCheckedFixturesOnly"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["sessionStoreRead"]),
        b(flags["configRead"]),
        b(flags["environmentRead"]),
        b(flags["providerConfigRead"]),
        b(flags["modelAssetRead"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["responseGenerated"]),
        b(flags["sendEnabled"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
        b(flags["releaseOrTagAction"]),
        b(flags["settingsChange"]),
    )
)
'
    )"; then
        ERROR "chat status summary JSON could not be summarized"
        return 1
    fi

    HEAD "chat status summary"
    printf '%s\n' "$CHAT_STATUS_SUMMARY_TEXT"
}

print_chat_review_packet_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_REVIEW_PACKET_STUB="$ROOT_DIR/scripts/chat-review-packet-stub.sh"

    if [ ! -f "$CHAT_REVIEW_PACKET_STUB" ]; then
        ERROR "chat review packet stub not found: $CHAT_REVIEW_PACKET_STUB"
        return 1
    fi

    if ! CHAT_REVIEW_PACKET_JSON="$(bash "$CHAT_REVIEW_PACKET_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat review packet stub failed"
        printf '%s\n' "$CHAT_REVIEW_PACKET_JSON" >&2
        return 1
    fi

    if ! CHAT_REVIEW_PACKET_TEXT="$(
        printf '%s\n' "$CHAT_REVIEW_PACKET_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
sections = " ".join(
    "{}={}".format(section["sectionId"], section["state"])
    for section in data["reviewSections"]
)
reviews = " ".join(
    "{}={}:{}".format(review["reviewId"], review["state"], str(review["accepted"]).lower())
    for review in data["requiredReviews"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)
refs = " ".join(
    "{}={}".format(ref["refId"], ref["state"])
    for ref in data["handoffRefs"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-review-packet-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/session-store/config/model/runtime/hardware/provider/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  review    : {}".format(data["reviewState"]))
print("[INFO]  approval  : {}".format(data["approvalState"]))
print("[INFO]  execution : {}".format(data["executionState"]))
print("[INFO]  content   : {}".format(data["contentState"]))
print("[INFO]  privacy   : {}".format(data["privacyState"]))
print("[INFO]  evidence  : {}".format(data["evidenceState"]))
print("[INFO]  sections   : {}".format(sections))
print("[INFO]  reviews    : {}".format(reviews))
print("[INFO]  blocked    : {}".format(blocked))
print("[INFO]  refs       : {}".format(refs))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "reviewPacketOnly={} aggregatesCheckedFixturesOnly={} "
    "statusSummaryReferencedOnly={} approvalGranted={} promptCapture={} "
    "promptRead={} promptContentIncluded={} responseContentIncluded={} "
    "transcriptContentIncluded={} messageBodiesIncluded={} sessionStoreRead={} "
    "sessionPersistence={} summaryGenerated={} transcriptExported={} "
    "clipboardRead={} clipboardWrite={} attachmentReads={} fileMetadataRead={} "
    "fileContentRead={} directoryScan={} redactionRulesLoaded={} contentScan={} "
    "redactionApplied={} auditLogWritten={} configRead={} environmentRead={} "
    "providerConfigRead={} modelAssetRead={} modelLoadAttempted={} "
    "modelExecution={} runtimeExecution={} responseGenerated={} sendEnabled={} "
    "kv260Access={} hardwareAccess={} networkCalls={} providerCalls={} "
    "cloudCalls={} executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["reviewPacketOnly"]),
        b(flags["aggregatesCheckedFixturesOnly"]),
        b(flags["statusSummaryReferencedOnly"]),
        b(flags["approvalGranted"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["sessionStoreRead"]),
        b(flags["sessionPersistence"]),
        b(flags["summaryGenerated"]),
        b(flags["transcriptExported"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["attachmentReads"]),
        b(flags["fileMetadataRead"]),
        b(flags["fileContentRead"]),
        b(flags["directoryScan"]),
        b(flags["redactionRulesLoaded"]),
        b(flags["contentScan"]),
        b(flags["redactionApplied"]),
        b(flags["auditLogWritten"]),
        b(flags["configRead"]),
        b(flags["environmentRead"]),
        b(flags["providerConfigRead"]),
        b(flags["modelAssetRead"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["responseGenerated"]),
        b(flags["sendEnabled"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "chat review packet JSON could not be summarized"
        return 1
    fi

    HEAD "chat review packet"
    printf '%s\n' "$CHAT_REVIEW_PACKET_TEXT"
}

print_chat_gap_matrix_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_GAP_MATRIX_STUB="$ROOT_DIR/scripts/chat-gap-matrix-stub.sh"

    if [ ! -f "$CHAT_GAP_MATRIX_STUB" ]; then
        ERROR "chat gap-matrix stub not found: $CHAT_GAP_MATRIX_STUB"
        return 1
    fi

    if ! CHAT_GAP_MATRIX_JSON="$(bash "$CHAT_GAP_MATRIX_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat gap-matrix stub failed"
        printf '%s\n' "$CHAT_GAP_MATRIX_JSON" >&2
        return 1
    fi

    if ! CHAT_GAP_MATRIX_TEXT="$(
        printf '%s\n' "$CHAT_GAP_MATRIX_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
gaps = " ".join(
    "{}={}:{}".format(row["gapId"], row["state"], row["severity"])
    for row in data["gapRows"]
)
refs = " ".join(
    "{}={}".format(ref["refId"], ref["state"])
    for ref in data["dependencyRefs"]
)
criteria = " ".join(
    "{}={}:{}".format(item["criteriaId"], item["state"], str(item["accepted"]).lower())
    for item in data["exitCriteria"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-gap-matrix-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/session-store/model/runtime/provider/hardware/lab/IDE/artifact execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  matrix     : {}".format(data["matrixState"]))
print("[INFO]  standalone : {}".format(data["standaloneChatState"]))
print("[INFO]  review    : {}".format(data["reviewState"]))
print("[INFO]  evidence  : {}".format(data["evidenceState"]))
print("[INFO]  readiness : {}".format(data["readinessState"]))
print("[INFO]  gaps       : {}".format(gaps))
print("[INFO]  refs       : {}".format(refs))
print("[INFO]  criteria   : {}".format(criteria))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "gapMatrixOnly={} referencesCheckedFixturesOnly={} "
    "reviewPacketReferencedOnly={} statusSummaryReferencedOnly={} "
    "gapClosed={} approvalGranted={} promptCapture={} promptRead={} "
    "promptContentIncluded={} promptEchoed={} inputAccepted={} "
    "responseContentIncluded={} responseGenerated={} responseChunksEmitted={} "
    "tokenCountMeasured={} transcriptContentIncluded={} "
    "messageBodiesIncluded={} sessionStoreRead={} sessionStoreWrite={} "
    "sessionPersistence={} summaryGenerated={} transcriptExported={} "
    "clipboardRead={} clipboardWrite={} attachmentReads={} "
    "fileMetadataRead={} fileContentRead={} directoryScan={} "
    "redactionRulesLoaded={} contentScan={} redactionApplied={} "
    "auditLogWritten={} configRead={} environmentRead={} "
    "providerConfigRead={} modelAssetRead={} modelPathIncluded={} "
    "modelLoadAttempted={} modelExecution={} runtimeExecution={} "
    "sendEnabled={} readsArtifacts={} writesArtifacts={} kv260Access={} "
    "hardwareAccess={} networkCalls={} providerCalls={} cloudCalls={} "
    "executesPccxLab={} executesSystemverilogIde={} commandDispatch={} "
    "actionExecution={} focusChanged={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["gapMatrixOnly"]),
        b(flags["referencesCheckedFixturesOnly"]),
        b(flags["reviewPacketReferencedOnly"]),
        b(flags["statusSummaryReferencedOnly"]),
        b(flags["gapClosed"]),
        b(flags["approvalGranted"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["promptEchoed"]),
        b(flags["inputAccepted"]),
        b(flags["responseContentIncluded"]),
        b(flags["responseGenerated"]),
        b(flags["responseChunksEmitted"]),
        b(flags["tokenCountMeasured"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["sessionStoreRead"]),
        b(flags["sessionStoreWrite"]),
        b(flags["sessionPersistence"]),
        b(flags["summaryGenerated"]),
        b(flags["transcriptExported"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["attachmentReads"]),
        b(flags["fileMetadataRead"]),
        b(flags["fileContentRead"]),
        b(flags["directoryScan"]),
        b(flags["redactionRulesLoaded"]),
        b(flags["contentScan"]),
        b(flags["redactionApplied"]),
        b(flags["auditLogWritten"]),
        b(flags["configRead"]),
        b(flags["environmentRead"]),
        b(flags["providerConfigRead"]),
        b(flags["modelAssetRead"]),
        b(flags["modelPathIncluded"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["sendEnabled"]),
        b(flags["readsArtifacts"]),
        b(flags["writesArtifacts"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
        b(flags["commandDispatch"]),
        b(flags["actionExecution"]),
        b(flags["focusChanged"]),
    )
)
'
    )"; then
        ERROR "chat gap-matrix JSON could not be summarized"
        return 1
    fi

    HEAD "chat gap matrix"
    printf '%s\n' "$CHAT_GAP_MATRIX_TEXT"
}

print_chat_evidence_manifest_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_EVIDENCE_MANIFEST_STUB="$ROOT_DIR/scripts/chat-evidence-manifest-stub.sh"

    if [ ! -f "$CHAT_EVIDENCE_MANIFEST_STUB" ]; then
        ERROR "chat evidence-manifest stub not found: $CHAT_EVIDENCE_MANIFEST_STUB"
        return 1
    fi

    if ! CHAT_EVIDENCE_MANIFEST_JSON="$(bash "$CHAT_EVIDENCE_MANIFEST_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat evidence-manifest stub failed"
        printf '%s\n' "$CHAT_EVIDENCE_MANIFEST_JSON" >&2
        return 1
    fi

    if ! CHAT_EVIDENCE_MANIFEST_TEXT="$(
        printf '%s\n' "$CHAT_EVIDENCE_MANIFEST_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
refs = " ".join(
    "{}={}".format(ref["refId"], ref["state"])
    for ref in data["evidenceRefs"]
)
links = " ".join(
    "{}={}".format(link["linkId"], link["state"])
    for link in data["reviewLinks"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)
actions = " ".join(
    "{}={}:{}".format(action["actionId"], action["state"], str(action["enabled"]).lower())
    for action in data["nextActions"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-evidence-manifest-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/session-store/artifact/model/runtime/provider/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  manifest  : {}".format(data["manifestState"]))
print("[INFO]  review    : {}".format(data["reviewState"]))
print("[INFO]  gap       : {}".format(data["gapState"]))
print("[INFO]  evidence  : {}".format(data["evidenceState"]))
print("[INFO]  artifact  : {}".format(data["artifactState"]))
print("[INFO]  refs       : {}".format(refs))
print("[INFO]  links      : {}".format(links))
print("[INFO]  blocked    : {}".format(blocked))
print("[INFO]  actions    : {}".format(actions))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "evidenceManifestOnly={} referencesCheckedFixturesOnly={} "
    "reviewPacketReferencedOnly={} gapMatrixReferencedOnly={} "
    "statusSummaryReferencedOnly={} evidenceAccepted={} gapClosed={} "
    "approvalGranted={} artifactRead={} artifactWrite={} rawLogRead={} "
    "hardwareDumpRead={} promptCapture={} promptRead={} "
    "promptContentIncluded={} responseContentIncluded={} "
    "transcriptContentIncluded={} messageBodiesIncluded={} "
    "sessionStoreRead={} configRead={} environmentRead={} "
    "providerConfigRead={} providerCalls={} cloudCalls={} networkCalls={} "
    "modelAssetRead={} modelPathIncluded={} modelLoadAttempted={} "
    "modelExecution={} runtimeExecution={} responseGenerated={} "
    "sendEnabled={} clipboardRead={} attachmentReads={} "
    "fileMetadataRead={} fileContentRead={} directoryScan={} "
    "redactionRulesLoaded={} contentScan={} redactionApplied={} "
    "auditLogWritten={} kv260Access={} hardwareAccess={} "
    "executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["evidenceManifestOnly"]),
        b(flags["referencesCheckedFixturesOnly"]),
        b(flags["reviewPacketReferencedOnly"]),
        b(flags["gapMatrixReferencedOnly"]),
        b(flags["statusSummaryReferencedOnly"]),
        b(flags["evidenceAccepted"]),
        b(flags["gapClosed"]),
        b(flags["approvalGranted"]),
        b(flags["artifactRead"]),
        b(flags["artifactWrite"]),
        b(flags["rawLogRead"]),
        b(flags["hardwareDumpRead"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["sessionStoreRead"]),
        b(flags["configRead"]),
        b(flags["environmentRead"]),
        b(flags["providerConfigRead"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["modelAssetRead"]),
        b(flags["modelPathIncluded"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["responseGenerated"]),
        b(flags["sendEnabled"]),
        b(flags["clipboardRead"]),
        b(flags["attachmentReads"]),
        b(flags["fileMetadataRead"]),
        b(flags["fileContentRead"]),
        b(flags["directoryScan"]),
        b(flags["redactionRulesLoaded"]),
        b(flags["contentScan"]),
        b(flags["redactionApplied"]),
        b(flags["auditLogWritten"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "chat evidence-manifest JSON could not be summarized"
        return 1
    fi

    HEAD "chat evidence manifest"
    printf '%s\n' "$CHAT_EVIDENCE_MANIFEST_TEXT"
}

print_chat_error_taxonomy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_ERROR_TAXONOMY_STUB="$ROOT_DIR/scripts/chat-error-taxonomy-stub.sh"

    if [ ! -f "$CHAT_ERROR_TAXONOMY_STUB" ]; then
        ERROR "chat error taxonomy stub not found: $CHAT_ERROR_TAXONOMY_STUB"
        return 1
    fi

    if ! CHAT_ERROR_TAXONOMY_JSON="$(bash "$CHAT_ERROR_TAXONOMY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat error taxonomy stub failed"
        printf '%s\n' "$CHAT_ERROR_TAXONOMY_JSON" >&2
        return 1
    fi

    if ! CHAT_ERROR_TAXONOMY_SUMMARY="$(
        printf '%s\n' "$CHAT_ERROR_TAXONOMY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
groups = " ".join(
    "{}={}".format(group["groupId"], group["state"])
    for group in data["errorGroups"]
)
items = " ".join(
    "{}={}".format(item["itemId"], item["state"])
    for item in data["errorItems"]
)
actions = " ".join(
    "{}={}".format(action["actionId"], action["state"])
    for action in data["actionRefs"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-error-taxonomy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/provider/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  taxonomy   : {}".format(data["taxonomyState"]))
print("[INFO]  display    : {}".format(data["displayState"]))
print("[INFO]  input      : {}".format(data["inputContentState"]))
print("[INFO]  runtime    : {}".format(data["runtimeState"]))
print("[INFO]  groups     : {}".format(groups))
print("[INFO]  items      : {}".format(items))
print("[INFO]  actions    : {}".format(actions))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "taxonomyDisplayOnly={} promptContentIncluded={} "
    "responseContentIncluded={} transcriptContentIncluded={} "
    "sessionStoreRead={} configRead={} providerConfigRead={} "
    "providerCalls={} cloudCalls={} networkCalls={} modelAssetRead={} "
    "modelLoadAttempted={} modelExecution={} runtimeExecution={} "
    "kv260Access={} hardwareAccess={} readsArtifacts={} "
    "writesArtifacts={} executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["taxonomyDisplayOnly"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["sessionStoreRead"]),
        b(flags["configRead"]),
        b(flags["providerConfigRead"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["modelAssetRead"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["readsArtifacts"]),
        b(flags["writesArtifacts"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "chat error taxonomy JSON could not be summarized"
        return 1
    fi

    HEAD "chat error taxonomy"
    printf '%s\n' "$CHAT_ERROR_TAXONOMY_SUMMARY"
}

print_chat_response_stream_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_RESPONSE_STREAM_STUB="$ROOT_DIR/scripts/chat-response-stream-stub.sh"

    if [ ! -f "$CHAT_RESPONSE_STREAM_STUB" ]; then
        ERROR "chat response stream stub not found: $CHAT_RESPONSE_STREAM_STUB"
        return 1
    fi

    if ! CHAT_RESPONSE_STREAM_JSON="$(bash "$CHAT_RESPONSE_STREAM_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat response stream stub failed"
        printf '%s\n' "$CHAT_RESPONSE_STREAM_JSON" >&2
        return 1
    fi

    if ! CHAT_RESPONSE_STREAM_SUMMARY="$(
        printf '%s\n' "$CHAT_RESPONSE_STREAM_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
envelope = data["streamEnvelope"]
phases = " ".join(
    "{}={}".format(phase["phaseId"], phase["state"])
    for phase in data["streamPhases"]
)
slots = " ".join(
    "{}={}".format(slot["slotId"], slot["state"])
    for slot in data["displaySlots"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)
token_count = envelope["tokenCount"]
token_count_text = "none" if token_count is None else str(token_count)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-response-stream-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/response stream/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  stream     : {}".format(data["streamState"]))
print("[INFO]  response   : {}".format(data["responseState"]))
print("[INFO]  transport  : {}".format(data["streamTransportState"]))
print("[INFO]  tokens     : {}".format(data["tokenState"]))
print("[INFO]  progress   : {}".format(data["progressState"]))
print("[INFO]  cancel     : {}".format(data["cancelState"]))
print(
    "[INFO]  envelope   : {} streamStarted={} transportOpened={} "
    "chunksEmitted={} tokenContentIncluded={} responseContentIncluded={} "
    "tokenCount={} stopSignalSent={}".format(
        envelope["state"],
        b(envelope["streamStarted"]),
        b(envelope["transportOpened"]),
        b(envelope["chunksEmitted"]),
        b(envelope["tokenContentIncluded"]),
        b(envelope["responseContentIncluded"]),
        token_count_text,
        b(envelope["stopSignalSent"]),
    )
)
print("[INFO]  phases     : {}".format(phases))
print("[INFO]  slots      : {}".format(slots))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "responseStreamDisplayOnly={} promptContentIncluded={} "
    "responseContentIncluded={} responseGenerated={} "
    "responseChunksEmitted={} tokenContentIncluded={} "
    "tokenCountMeasured={} streamStarted={} streamTransportOpened={} "
    "streamCancellationAttempted={} sessionStoreRead={} "
    "modelAssetRead={} modelLoadAttempted={} modelExecution={} "
    "runtimeExecution={} kv260Access={} hardwareAccess={} "
    "networkCalls={} providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["responseStreamDisplayOnly"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["responseGenerated"]),
        b(flags["responseChunksEmitted"]),
        b(flags["tokenContentIncluded"]),
        b(flags["tokenCountMeasured"]),
        b(flags["streamStarted"]),
        b(flags["streamTransportOpened"]),
        b(flags["streamCancellationAttempted"]),
        b(flags["sessionStoreRead"]),
        b(flags["modelAssetRead"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat response stream JSON could not be summarized"
        return 1
    fi

    HEAD "chat response stream"
    printf '%s\n' "$CHAT_RESPONSE_STREAM_SUMMARY"
}

print_chat_message_list_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_MESSAGE_LIST_STUB="$ROOT_DIR/scripts/chat-message-list-stub.sh"

    if [ ! -f "$CHAT_MESSAGE_LIST_STUB" ]; then
        ERROR "chat message-list stub not found: $CHAT_MESSAGE_LIST_STUB"
        return 1
    fi

    if ! CHAT_MESSAGE_LIST_JSON="$(bash "$CHAT_MESSAGE_LIST_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat message-list stub failed"
        printf '%s\n' "$CHAT_MESSAGE_LIST_JSON" >&2
        return 1
    fi

    if ! CHAT_MESSAGE_LIST_SUMMARY="$(
        printf '%s\n' "$CHAT_MESSAGE_LIST_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
collection = data["messageCollection"]
slots = " ".join(
    "{}={}".format(slot["slotId"], slot["state"])
    for slot in data["viewportSlots"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-message-list-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no message bodies/transcript/session-store/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  list       : {}".format(data["listState"]))
print("[INFO]  viewport   : {}".format(data["viewportState"]))
print("[INFO]  transcript : {}".format(data["transcriptState"]))
print("[INFO]  content    : {}".format(data["messageContentState"]))
print("[INFO]  empty      : {}".format(data["emptyState"]))
print("[INFO]  selection  : {}".format(data["selectionState"]))
print("[INFO]  scroll     : {}".format(data["scrollState"]))
print(
    "[INFO]  collection : {} itemCount={} promptMessagesIncluded={} "
    "assistantMessagesIncluded={} systemNoticesIncluded={} "
    "messageBodiesIncluded={} transcriptReadEnabled={}".format(
        collection["state"],
        collection["itemCount"],
        b(collection["promptMessagesIncluded"]),
        b(collection["assistantMessagesIncluded"]),
        b(collection["systemNoticesIncluded"]),
        b(collection["messageBodiesIncluded"]),
        b(collection["transcriptReadEnabled"]),
    )
)
print("[INFO]  slots      : {}".format(slots))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "messageListDisplayOnly={} messageMetadataOnly={} "
    "readsSessionStore={} readsTranscript={} messageBodiesIncluded={} "
    "promptContentIncluded={} responseContentIncluded={} "
    "responseGenerated={} sendAttempted={} sessionStoreRead={} "
    "modelAssetRead={} modelExecution={} runtimeExecution={} "
    "kv260Access={} hardwareAccess={} networkCalls={} providerCalls={} "
    "executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["messageListDisplayOnly"]),
        b(flags["messageMetadataOnly"]),
        b(flags["readsSessionStore"]),
        b(flags["readsTranscript"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["responseGenerated"]),
        b(flags["sendAttempted"]),
        b(flags["sessionStoreRead"]),
        b(flags["modelAssetRead"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat message-list JSON could not be summarized"
        return 1
    fi

    HEAD "chat message list"
    printf '%s\n' "$CHAT_MESSAGE_LIST_SUMMARY"
}

print_chat_action_bar_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_ACTION_BAR_STUB="$ROOT_DIR/scripts/chat-action-bar-stub.sh"

    if [ ! -f "$CHAT_ACTION_BAR_STUB" ]; then
        ERROR "chat action-bar stub not found: $CHAT_ACTION_BAR_STUB"
        return 1
    fi

    if ! CHAT_ACTION_BAR_JSON="$(bash "$CHAT_ACTION_BAR_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat action-bar stub failed"
        printf '%s\n' "$CHAT_ACTION_BAR_JSON" >&2
        return 1
    fi

    if ! CHAT_ACTION_BAR_SUMMARY="$(
        printf '%s\n' "$CHAT_ACTION_BAR_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]

def b(value):
    return "true" if value else "false"

groups = " ".join(
    "{}={}".format(group["groupId"], group["state"])
    for group in data["actionGroups"]
)
controls = " ".join(
    "{}={}:{}".format(control["actionId"], control["state"], b(control["enabled"]))
    for control in data["actionControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-action-bar-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no action execution/session-store/transcript/clipboard/file/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  actions    : {}".format(data["actionBarState"]))
print("[INFO]  conversation: {}".format(data["conversationState"]))
print("[INFO]  selection  : {}".format(data["selectionState"]))
print("[INFO]  transcript : {}".format(data["transcriptState"]))
print("[INFO]  response   : {}".format(data["responseState"]))
print("[INFO]  attachment : {}".format(data["attachmentState"]))
print("[INFO]  clipboard  : {}".format(data["clipboardState"]))
print("[INFO]  export     : {}".format(data["exportState"]))
print("[INFO]  stop       : {}".format(data["stopControlState"]))
print("[INFO]  groups     : {}".format(groups))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "actionBarDisplayOnly={} actionMetadataOnly={} "
    "readsSessionStore={} readsTranscript={} transcriptExport={} "
    "sessionStoreRead={} sessionStoreWrite={} conversationCreated={} "
    "conversationCleared={} attachmentReads={} fileUpload={} "
    "clipboardWrite={} sendAttempted={} retryAttempted={} "
    "stopSignalSent={} responseGenerated={} modelExecution={} "
    "runtimeExecution={} kv260Access={} hardwareAccess={} "
    "networkCalls={} providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["actionBarDisplayOnly"]),
        b(flags["actionMetadataOnly"]),
        b(flags["readsSessionStore"]),
        b(flags["readsTranscript"]),
        b(flags["transcriptExport"]),
        b(flags["sessionStoreRead"]),
        b(flags["sessionStoreWrite"]),
        b(flags["conversationCreated"]),
        b(flags["conversationCleared"]),
        b(flags["attachmentReads"]),
        b(flags["fileUpload"]),
        b(flags["clipboardWrite"]),
        b(flags["sendAttempted"]),
        b(flags["retryAttempted"]),
        b(flags["stopSignalSent"]),
        b(flags["responseGenerated"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat action-bar JSON could not be summarized"
        return 1
    fi

    HEAD "chat action bar"
    printf '%s\n' "$CHAT_ACTION_BAR_SUMMARY"
}

print_chat_clipboard_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_CLIPBOARD_POLICY_STUB="$ROOT_DIR/scripts/chat-clipboard-policy-stub.sh"

    if [ ! -f "$CHAT_CLIPBOARD_POLICY_STUB" ]; then
        ERROR "chat clipboard-policy stub not found: $CHAT_CLIPBOARD_POLICY_STUB"
        return 1
    fi

    if ! CHAT_CLIPBOARD_POLICY_JSON="$(bash "$CHAT_CLIPBOARD_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat clipboard-policy stub failed"
        printf '%s\n' "$CHAT_CLIPBOARD_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_CLIPBOARD_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_CLIPBOARD_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["clipboardPolicy"]

def b(value):
    return "true" if value else "false"

surfaces = " ".join(
    "{}={}:{}".format(surface["surfaceId"], surface["state"], b(surface["enabled"]))
    for surface in data["clipboardSurfaces"]
)
controls = " ".join(
    "{}={}:{}".format(control["controlId"], control["state"], b(control["enabled"]))
    for control in data["clipboardControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-clipboard-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no clipboard read/write/paste/copy/import/export/session-store/transcript/message/file/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  policy     : {}".format(data["clipboardPolicyState"]))
print("[INFO]  read       : {}".format(data["clipboardReadState"]))
print("[INFO]  write      : {}".format(data["clipboardWriteState"]))
print("[INFO]  copy       : {}".format(data["copyActionState"]))
print("[INFO]  paste      : {}".format(data["pasteActionState"]))
print("[INFO]  import     : {}".format(data["clipboardImportState"]))
print("[INFO]  export     : {}".format(data["clipboardExportState"]))
print("[INFO]  selection  : {}".format(data["selectionState"]))
print("[INFO]  message    : {}".format(data["messageContentState"]))
print("[INFO]  transcript : {}".format(data["transcriptState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  clipboard-policy : {} mode={} readEnabled={} "
    "writeEnabled={} copyEnabled={} pasteEnabled={} "
    "importEnabled={} exportEnabled={} userConsentRequired={}".format(
        policy["state"],
        policy["mode"],
        b(policy["readEnabled"]),
        b(policy["writeEnabled"]),
        b(policy["copyEnabled"]),
        b(policy["pasteEnabled"]),
        b(policy["importEnabled"]),
        b(policy["exportEnabled"]),
        b(policy["userConsentRequired"]),
    )
)
print("[INFO]  surfaces   : {}".format(surfaces))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "clipboardPolicyDisplayOnly={} clipboardMetadataOnly={} "
    "clipboardRead={} clipboardWrite={} clipboardCopy={} "
    "clipboardPaste={} clipboardImport={} clipboardExport={} "
    "clipboardAttachmentRead={} clipboardEventListenerInstalled={} "
    "selectionRead={} messageBodiesIncluded={} promptCapture={} "
    "promptRead={} promptContentIncluded={} responseContentIncluded={} "
    "transcriptContentIncluded={} readsTranscript={} "
    "transcriptExport={} readsSessionStore={} sessionStoreRead={} "
    "sessionStoreWrite={} attachmentReads={} fileUpload={} "
    "fileImport={} filePreview={} writesArtifacts={} "
    "readsArtifacts={} modelAssetRead={} modelExecution={} "
    "runtimeExecution={} kv260Access={} hardwareAccess={} "
    "networkCalls={} providerCalls={} cloudCalls={} "
    "executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["clipboardPolicyDisplayOnly"]),
        b(flags["clipboardMetadataOnly"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["clipboardCopy"]),
        b(flags["clipboardPaste"]),
        b(flags["clipboardImport"]),
        b(flags["clipboardExport"]),
        b(flags["clipboardAttachmentRead"]),
        b(flags["clipboardEventListenerInstalled"]),
        b(flags["selectionRead"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["readsTranscript"]),
        b(flags["transcriptExport"]),
        b(flags["readsSessionStore"]),
        b(flags["sessionStoreRead"]),
        b(flags["sessionStoreWrite"]),
        b(flags["attachmentReads"]),
        b(flags["fileUpload"]),
        b(flags["fileImport"]),
        b(flags["filePreview"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["modelAssetRead"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat clipboard-policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat clipboard policy"
    printf '%s\n' "$CHAT_CLIPBOARD_POLICY_SUMMARY"
}

print_chat_redaction_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_REDACTION_POLICY_STUB="$ROOT_DIR/scripts/chat-redaction-policy-stub.sh"

    if [ ! -f "$CHAT_REDACTION_POLICY_STUB" ]; then
        ERROR "chat redaction-policy stub not found: $CHAT_REDACTION_POLICY_STUB"
        return 1
    fi

    if ! CHAT_REDACTION_POLICY_JSON="$(bash "$CHAT_REDACTION_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat redaction-policy stub failed"
        printf '%s\n' "$CHAT_REDACTION_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_REDACTION_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_REDACTION_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["redactionPolicy"]

def b(value):
    return "true" if value else "false"

surfaces = " ".join(
    "{}={}:{}".format(surface["surfaceId"], surface["state"], b(surface["enabled"]))
    for surface in data["redactionSurfaces"]
)
controls = " ".join(
    "{}={}:{}".format(control["controlId"], control["state"], b(control["enabled"]))
    for control in data["redactionControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-redaction-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no redaction rule load/content scan/PII detection/secret detection/prompt/message/transcript/clipboard/file/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  policy     : {}".format(data["redactionPolicyState"]))
print("[INFO]  scan       : {}".format(data["contentScanState"]))
print("[INFO]  prompt    : {}".format(data["promptRedactionState"]))
print("[INFO]  response  : {}".format(data["responseRedactionState"]))
print("[INFO]  transcript: {}".format(data["transcriptRedactionState"]))
print("[INFO]  message   : {}".format(data["messageRedactionState"]))
print("[INFO]  attachment: {}".format(data["attachmentRedactionState"]))
print("[INFO]  clipboard : {}".format(data["clipboardRedactionState"]))
print("[INFO]  audit     : {}".format(data["auditRedactionState"]))
print("[INFO]  pii       : {}".format(data["piiDetectionState"]))
print("[INFO]  secrets   : {}".format(data["secretDetectionState"]))
print("[INFO]  persistence: {}".format(data["persistenceState"]))
print("[INFO]  privacy   : {}".format(data["privacyState"]))
print(
    "[INFO]  redaction-policy : {} mode={} scannerEnabled={} "
    "promptRedactionEnabled={} responseRedactionEnabled={} "
    "transcriptRedactionEnabled={} messageRedactionEnabled={} "
    "attachmentRedactionEnabled={} clipboardRedactionEnabled={} "
    "auditRedactionEnabled={} piiDetectionEnabled={} "
    "secretDetectionEnabled={} persistenceEnabled={}".format(
        policy["state"],
        policy["mode"],
        b(policy["scannerEnabled"]),
        b(policy["promptRedactionEnabled"]),
        b(policy["responseRedactionEnabled"]),
        b(policy["transcriptRedactionEnabled"]),
        b(policy["messageRedactionEnabled"]),
        b(policy["attachmentRedactionEnabled"]),
        b(policy["clipboardRedactionEnabled"]),
        b(policy["auditRedactionEnabled"]),
        b(policy["piiDetectionEnabled"]),
        b(policy["secretDetectionEnabled"]),
        b(policy["persistenceEnabled"]),
    )
)
print("[INFO]  surfaces   : {}".format(surfaces))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "redactionPolicyDisplayOnly={} redactionMetadataOnly={} "
    "redactionRulesLoaded={} redactionRulesPersisted={} "
    "contentScan={} piiDetection={} secretDetection={} "
    "identifierDetection={} promptRedaction={} responseRedaction={} "
    "transcriptRedaction={} messageRedaction={} attachmentRedaction={} "
    "clipboardRedaction={} auditRedaction={} redactionApplied={} "
    "redactionResultPersisted={} redactionReportGenerated={} "
    "promptCapture={} promptRead={} promptContentIncluded={} "
    "responseContentIncluded={} transcriptContentIncluded={} "
    "messageBodiesIncluded={} readsTranscript={} sessionStoreRead={} "
    "sessionStoreWrite={} clipboardRead={} clipboardWrite={} "
    "attachmentReads={} fileMetadataRead={} fileContentRead={} "
    "directoryScan={} fileImport={} fileUpload={} writesArtifacts={} "
    "readsArtifacts={} modelAssetRead={} modelLoadAttempted={} "
    "modelExecution={} runtimeExecution={} kv260Access={} "
    "hardwareAccess={} networkCalls={} providerCalls={} cloudCalls={} "
    "executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["redactionPolicyDisplayOnly"]),
        b(flags["redactionMetadataOnly"]),
        b(flags["redactionRulesLoaded"]),
        b(flags["redactionRulesPersisted"]),
        b(flags["contentScan"]),
        b(flags["piiDetection"]),
        b(flags["secretDetection"]),
        b(flags["identifierDetection"]),
        b(flags["promptRedaction"]),
        b(flags["responseRedaction"]),
        b(flags["transcriptRedaction"]),
        b(flags["messageRedaction"]),
        b(flags["attachmentRedaction"]),
        b(flags["clipboardRedaction"]),
        b(flags["auditRedaction"]),
        b(flags["redactionApplied"]),
        b(flags["redactionResultPersisted"]),
        b(flags["redactionReportGenerated"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["readsTranscript"]),
        b(flags["sessionStoreRead"]),
        b(flags["sessionStoreWrite"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["attachmentReads"]),
        b(flags["fileMetadataRead"]),
        b(flags["fileContentRead"]),
        b(flags["directoryScan"]),
        b(flags["fileImport"]),
        b(flags["fileUpload"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["modelAssetRead"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "chat redaction-policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat redaction policy"
    printf '%s\n' "$CHAT_REDACTION_POLICY_SUMMARY"
}

print_chat_attachment_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_ATTACHMENT_POLICY_STUB="$ROOT_DIR/scripts/chat-attachment-policy-stub.sh"

    if [ ! -f "$CHAT_ATTACHMENT_POLICY_STUB" ]; then
        ERROR "chat attachment-policy stub not found: $CHAT_ATTACHMENT_POLICY_STUB"
        return 1
    fi

    if ! CHAT_ATTACHMENT_POLICY_JSON="$(bash "$CHAT_ATTACHMENT_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat attachment-policy stub failed"
        printf '%s\n' "$CHAT_ATTACHMENT_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_ATTACHMENT_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_ATTACHMENT_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["attachmentPolicy"]

def b(value):
    return "true" if value else "false"

inputs = " ".join(
    "{}={}:{}".format(input_item["inputKind"], input_item["state"], b(input_item["enabled"]))
    for input_item in data["attachmentInputs"]
)
controls = " ".join(
    "{}={}:{}".format(control["controlId"], control["state"], b(control["enabled"]))
    for control in data["attachmentControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-attachment-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no file picker/file metadata/file content/upload/import/clipboard/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  policy     : {}".format(data["attachmentPolicyState"]))
print("[INFO]  attachment : {}".format(data["attachmentState"]))
print("[INFO]  file picker: {}".format(data["filePickerState"]))
print("[INFO]  file read  : {}".format(data["fileReadState"]))
print("[INFO]  upload     : {}".format(data["uploadState"]))
print("[INFO]  import     : {}".format(data["importState"]))
print("[INFO]  preview    : {}".format(data["previewState"]))
print("[INFO]  persistence: {}".format(data["persistenceState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  attachment-policy : {} mode={} maxAttachmentCount={} "
    "filePickerEnabled={} fileMetadataReadEnabled={} "
    "fileContentReadEnabled={} uploadEnabled={} importEnabled={} "
    "previewEnabled={} persistenceEnabled={}".format(
        policy["state"],
        policy["mode"],
        policy["maxAttachmentCount"],
        b(policy["filePickerEnabled"]),
        b(policy["fileMetadataReadEnabled"]),
        b(policy["fileContentReadEnabled"]),
        b(policy["uploadEnabled"]),
        b(policy["importEnabled"]),
        b(policy["previewEnabled"]),
        b(policy["persistenceEnabled"]),
    )
)
print("[INFO]  inputs     : {}".format(inputs))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "attachmentPolicyDisplayOnly={} attachmentMetadataOnly={} "
    "attachmentsEnabled={} filePickerOpened={} fileMetadataRead={} "
    "fileContentRead={} fileNameIncluded={} filePathIncluded={} "
    "fileBytesIncluded={} directoryScan={} attachmentReads={} "
    "attachmentPersistence={} fileUpload={} fileImport={} "
    "filePreview={} clipboardRead={} writesArtifacts={} "
    "readsArtifacts={} readsTranscript={} transcriptExport={} "
    "promptContentIncluded={} responseContentIncluded={} "
    "modelExecution={} runtimeExecution={} kv260Access={} "
    "hardwareAccess={} networkCalls={} providerCalls={} "
    "executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["attachmentPolicyDisplayOnly"]),
        b(flags["attachmentMetadataOnly"]),
        b(flags["attachmentsEnabled"]),
        b(flags["filePickerOpened"]),
        b(flags["fileMetadataRead"]),
        b(flags["fileContentRead"]),
        b(flags["fileNameIncluded"]),
        b(flags["filePathIncluded"]),
        b(flags["fileBytesIncluded"]),
        b(flags["directoryScan"]),
        b(flags["attachmentReads"]),
        b(flags["attachmentPersistence"]),
        b(flags["fileUpload"]),
        b(flags["fileImport"]),
        b(flags["filePreview"]),
        b(flags["clipboardRead"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["readsTranscript"]),
        b(flags["transcriptExport"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat attachment-policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat attachment policy"
    printf '%s\n' "$CHAT_ATTACHMENT_POLICY_SUMMARY"
}

print_chat_shortcut_map_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SHORTCUT_MAP_STUB="$ROOT_DIR/scripts/chat-shortcut-map-stub.sh"

    if [ ! -f "$CHAT_SHORTCUT_MAP_STUB" ]; then
        ERROR "chat shortcut-map stub not found: $CHAT_SHORTCUT_MAP_STUB"
        return 1
    fi

    if ! CHAT_SHORTCUT_MAP_JSON="$(bash "$CHAT_SHORTCUT_MAP_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat shortcut-map stub failed"
        printf '%s\n' "$CHAT_SHORTCUT_MAP_JSON" >&2
        return 1
    fi

    if ! CHAT_SHORTCUT_MAP_SUMMARY="$(
        printf '%s\n' "$CHAT_SHORTCUT_MAP_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]

def b(value):
    return "true" if value else "false"

scopes = " ".join(
    "{}={}".format(scope["scopeId"], scope["state"])
    for scope in data["shortcutScopes"]
)
bindings = " ".join(
    "{}={}:{}".format(binding["shortcutId"], binding["state"], b(binding["enabled"]))
    for binding in data["shortcutBindings"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-shortcut-map-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no keyboard listener/command dispatch/session-store/transcript/clipboard/file/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  shortcuts  : {}".format(data["shortcutMapState"]))
print("[INFO]  focus      : {}".format(data["focusState"]))
print("[INFO]  keyboard   : {}".format(data["keyboardCaptureState"]))
print("[INFO]  dispatch   : {}".format(data["commandDispatchState"]))
print("[INFO]  execution  : {}".format(data["actionExecutionState"]))
print("[INFO]  scopes     : {}".format(scopes))
print("[INFO]  bindings   : {}".format(bindings))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "shortcutMapDisplayOnly={} shortcutMetadataOnly={} "
    "keyboardListenerInstalled={} keyboardCaptureEnabled={} "
    "commandDispatchEnabled={} shortcutExecuted={} focusChanged={} "
    "readsSessionStore={} readsTranscript={} readsMessages={} "
    "promptCapture={} sendAttempted={} stopSignalSent={} "
    "clipboardWrite={} attachmentReads={} modelExecution={} "
    "runtimeExecution={} kv260Access={} hardwareAccess={} "
    "networkCalls={} providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["shortcutMapDisplayOnly"]),
        b(flags["shortcutMetadataOnly"]),
        b(flags["keyboardListenerInstalled"]),
        b(flags["keyboardCaptureEnabled"]),
        b(flags["commandDispatchEnabled"]),
        b(flags["shortcutExecuted"]),
        b(flags["focusChanged"]),
        b(flags["readsSessionStore"]),
        b(flags["readsTranscript"]),
        b(flags["readsMessages"]),
        b(flags["promptCapture"]),
        b(flags["sendAttempted"]),
        b(flags["stopSignalSent"]),
        b(flags["clipboardWrite"]),
        b(flags["attachmentReads"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat shortcut-map JSON could not be summarized"
        return 1
    fi

    HEAD "chat shortcut map"
    printf '%s\n' "$CHAT_SHORTCUT_MAP_SUMMARY"
}

print_chat_local_only_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_LOCAL_ONLY_POLICY_STUB="$ROOT_DIR/scripts/chat-local-only-policy-stub.sh"

    if [ ! -f "$CHAT_LOCAL_ONLY_POLICY_STUB" ]; then
        ERROR "chat local-only policy stub not found: $CHAT_LOCAL_ONLY_POLICY_STUB"
        return 1
    fi

    if ! CHAT_LOCAL_ONLY_POLICY_JSON="$(bash "$CHAT_LOCAL_ONLY_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat local-only policy stub failed"
        printf '%s\n' "$CHAT_LOCAL_ONLY_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_LOCAL_ONLY_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_LOCAL_ONLY_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
controls = " ".join(
    "{}={}".format(control["controlId"], control["state"])
    for control in data["policyControls"]
)
checks = " ".join(
    "{}={}".format(check["checkId"], check["state"])
    for check in data["dependencyChecks"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-local-only-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no cloud/provider/network/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  policy     : {}".format(data["policyState"]))
print("[INFO]  local      : {}".format(data["localExecutionState"]))
print("[INFO]  cloud      : {}".format(data["cloudDependencyState"]))
print("[INFO]  provider   : {}".format(data["providerState"]))
print("[INFO]  network    : {}".format(data["networkState"]))
print("[INFO]  offline    : {}".format(data["offlineModeState"]))
print("[INFO]  fallback   : {}".format(data["fallbackState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  checks     : {}".format(checks))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "localOnlyPolicyDisplayOnly={} cloudDependency={} "
    "cloudFallbackEnabled={} providerCalls={} cloudCalls={} "
    "networkCalls={} providerConfigRead={} environmentRead={} "
    "secretsRead={} tokensRead={} promptCapture={} "
    "promptContentIncluded={} responseContentIncluded={} "
    "transcriptContentIncluded={} modelLoadAttempted={} modelLoaded={} "
    "modelExecution={} runtimeExecution={} kv260Access={} "
    "writesArtifacts={} readsArtifacts={} telemetry={} upload={} "
    "executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["localOnlyPolicyDisplayOnly"]),
        b(flags["cloudDependency"]),
        b(flags["cloudFallbackEnabled"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["providerConfigRead"]),
        b(flags["environmentRead"]),
        b(flags["secretsRead"]),
        b(flags["tokensRead"]),
        b(flags["promptCapture"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["telemetry"]),
        b(flags["upload"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "chat local-only policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat local-only policy"
    printf '%s\n' "$CHAT_LOCAL_ONLY_POLICY_SUMMARY"
}

print_chat_preferences_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_PREFERENCES_STUB="$ROOT_DIR/scripts/chat-preferences-stub.sh"

    if [ ! -f "$CHAT_PREFERENCES_STUB" ]; then
        ERROR "chat preferences stub not found: $CHAT_PREFERENCES_STUB"
        return 1
    fi

    if ! CHAT_PREFERENCES_JSON="$(bash "$CHAT_PREFERENCES_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat preferences stub failed"
        printf '%s\n' "$CHAT_PREFERENCES_JSON" >&2
        return 1
    fi

    if ! CHAT_PREFERENCES_SUMMARY="$(
        printf '%s\n' "$CHAT_PREFERENCES_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
panels = " ".join(
    "{}={}".format(panel["panelId"], panel["state"])
    for panel in data["preferencePanels"]
)
controls = " ".join(
    "{}={}".format(control["controlId"], control["state"])
    for control in data["preferenceControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-preferences-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no config/provider/session-store/model path/runtime execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  preferences: {}".format(data["preferencesState"]))
print("[INFO]  storage    : {}".format(data["storageState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print("[INFO]  panels     : {}".format(panels))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "preferencesDisplayOnly={} preferencePersistence={} "
    "preferenceWrite={} configRead={} environmentRead={} "
    "secretsRead={} tokensRead={} providerConfigRead={} "
    "providerCalls={} cloudCalls={} networkCalls={} modelAssetRead={} "
    "modelPathIncluded={} sessionStoreRead={} sessionStoreWrite={} "
    "promptContentIncluded={} responseContentIncluded={} "
    "transcriptContentIncluded={} transcriptPersistence={} "
    "transcriptExport={} readsArtifacts={} writesArtifacts={} "
    "executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["preferencesDisplayOnly"]),
        b(flags["preferencePersistence"]),
        b(flags["preferenceWrite"]),
        b(flags["configRead"]),
        b(flags["environmentRead"]),
        b(flags["secretsRead"]),
        b(flags["tokensRead"]),
        b(flags["providerConfigRead"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["modelAssetRead"]),
        b(flags["modelPathIncluded"]),
        b(flags["sessionStoreRead"]),
        b(flags["sessionStoreWrite"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["transcriptPersistence"]),
        b(flags["transcriptExport"]),
        b(flags["readsArtifacts"]),
        b(flags["writesArtifacts"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "chat preferences JSON could not be summarized"
        return 1
    fi

    HEAD "chat preferences"
    printf '%s\n' "$CHAT_PREFERENCES_SUMMARY"
}

print_chat_surface_layout_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SURFACE_LAYOUT_STUB="$ROOT_DIR/scripts/chat-surface-layout-stub.sh"

    if [ ! -f "$CHAT_SURFACE_LAYOUT_STUB" ]; then
        ERROR "chat surface layout stub not found: $CHAT_SURFACE_LAYOUT_STUB"
        return 1
    fi

    if ! CHAT_SURFACE_LAYOUT_JSON="$(bash "$CHAT_SURFACE_LAYOUT_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat surface layout stub failed"
        printf '%s\n' "$CHAT_SURFACE_LAYOUT_JSON" >&2
        return 1
    fi

    if ! CHAT_SURFACE_LAYOUT_SUMMARY="$(
        printf '%s\n' "$CHAT_SURFACE_LAYOUT_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["layoutPolicy"]
regions = " ".join(
    "{}={}".format(region["regionId"], region["state"])
    for region in data["surfaceRegions"]
)
nav = " ".join(
    "{}={}".format(item["navId"], item["state"])
    for item in data["navigationItems"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-surface-layout-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/response/transcript/session-store/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  layout     : {}".format(data["layoutState"]))
print("[INFO]  shell      : {}".format(data["shellState"]))
print("[INFO]  navigation : {}".format(data["navigationState"]))
print("[INFO]  primary    : {}".format(data["primaryRegionState"]))
print("[INFO]  side       : {}".format(data["sideRegionState"]))
print("[INFO]  footer     : {}".format(data["footerState"]))
print("[INFO]  content    : {}".format(data["contentState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  layout-policy : {} renderMode={} sideEffectPolicy={}".format(
        policy["state"],
        policy["renderMode"],
        policy["sideEffectPolicy"],
    )
)
print("[INFO]  regions    : {}".format(regions))
print("[INFO]  nav        : {}".format(nav))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "surfaceLayoutDisplayOnly={} writesArtifacts={} readsArtifacts={} "
    "sessionStoreRead={} promptCapture={} promptContentIncluded={} "
    "responseContentIncluded={} transcriptContentIncluded={} "
    "sessionTitleIncluded={} summaryIncluded={} inputAccepted={} "
    "sendAttempted={} modelExecution={} runtimeExecution={} kv260Access={} "
    "networkCalls={} providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["surfaceLayoutDisplayOnly"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["sessionStoreRead"]),
        b(flags["promptCapture"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["sessionTitleIncluded"]),
        b(flags["summaryIncluded"]),
        b(flags["inputAccepted"]),
        b(flags["sendAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat surface layout JSON could not be summarized"
        return 1
    fi

    HEAD "chat surface layout"
    printf '%s\n' "$CHAT_SURFACE_LAYOUT_SUMMARY"
}

print_chat_empty_state_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_EMPTY_STATE_STUB="$ROOT_DIR/scripts/chat-empty-state-stub.sh"

    if [ ! -f "$CHAT_EMPTY_STATE_STUB" ]; then
        ERROR "chat empty-state stub not found: $CHAT_EMPTY_STATE_STUB"
        return 1
    fi

    if ! CHAT_EMPTY_STATE_JSON="$(bash "$CHAT_EMPTY_STATE_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat empty-state stub failed"
        printf '%s\n' "$CHAT_EMPTY_STATE_JSON" >&2
        return 1
    fi

    if ! CHAT_EMPTY_STATE_SUMMARY="$(
        printf '%s\n' "$CHAT_EMPTY_STATE_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["emptyStatePolicy"]

def b(value):
    return "true" if value else "false"

slots = " ".join(
    "{}={}:{}".format(slot["slotId"], slot["state"], b(slot["enabled"]))
    for slot in data["displaySlots"]
)
hints = " ".join(
    "{}={}:{}".format(hint["hintId"], hint["state"], b(hint["enabled"]))
    for hint in data["affordanceHints"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-empty-state-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/response/transcript/session-store/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  empty      : {}".format(data["emptyStateState"]))
print("[INFO]  surface    : {}".format(data["surfaceState"]))
print("[INFO]  session    : {}".format(data["sessionState"]))
print("[INFO]  modelstate : {}".format(data["modelState"]))
print("[INFO]  readiness  : {}".format(data["readinessState"]))
print("[INFO]  prompt     : {}".format(data["promptState"]))
print("[INFO]  transcript : {}".format(data["transcriptState"]))
print("[INFO]  actions    : {}".format(data["actionState"]))
print("[INFO]  runtime    : {}".format(data["runtimeState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  empty-policy : {} renderMode={} sideEffectPolicy={}".format(
        policy["state"],
        policy["renderMode"],
        policy["sideEffectPolicy"],
    )
)
print("[INFO]  slots      : {}".format(slots))
print("[INFO]  hints      : {}".format(hints))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "emptyStateDisplayOnly={} emptyStateTextOnly={} localRenderOnly={} "
    "promptCapture={} promptRead={} promptContentIncluded={} "
    "inputAccepted={} responseContentIncluded={} responseGenerated={} "
    "transcriptContentIncluded={} messageContentIncluded={} "
    "sessionTitleIncluded={} summaryIncluded={} readsSessionStore={} "
    "writesSessionStore={} actionExecution={} commandDispatch={} "
    "modelAssetRead={} modelLoadAttempted={} modelExecution={} "
    "runtimeExecution={} kv260Access={} hardwareAccess={} networkCalls={} "
    "providerCalls={} readsArtifacts={} writesArtifacts={} "
    "executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["emptyStateDisplayOnly"]),
        b(flags["emptyStateTextOnly"]),
        b(flags["localRenderOnly"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["inputAccepted"]),
        b(flags["responseContentIncluded"]),
        b(flags["responseGenerated"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["messageContentIncluded"]),
        b(flags["sessionTitleIncluded"]),
        b(flags["summaryIncluded"]),
        b(flags["readsSessionStore"]),
        b(flags["writesSessionStore"]),
        b(flags["actionExecution"]),
        b(flags["commandDispatch"]),
        b(flags["modelAssetRead"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["readsArtifacts"]),
        b(flags["writesArtifacts"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat empty-state JSON could not be summarized"
        return 1
    fi

    HEAD "chat empty state"
    printf '%s\n' "$CHAT_EMPTY_STATE_SUMMARY"
}

print_chat_session_index_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SESSION_INDEX_STUB="$ROOT_DIR/scripts/chat-session-index-stub.sh"

    if [ ! -f "$CHAT_SESSION_INDEX_STUB" ]; then
        ERROR "chat session index stub not found: $CHAT_SESSION_INDEX_STUB"
        return 1
    fi

    if ! CHAT_SESSION_INDEX_JSON="$(bash "$CHAT_SESSION_INDEX_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat session index stub failed"
        printf '%s\n' "$CHAT_SESSION_INDEX_JSON" >&2
        return 1
    fi

    if ! CHAT_SESSION_INDEX_SUMMARY="$(
        printf '%s\n' "$CHAT_SESSION_INDEX_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["indexPolicy"]
empty = data["emptyState"]
controls = " ".join(
    "{}={}".format(control["controlId"], control["state"])
    for control in data["indexControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-session-index-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no session-store/transcript/prompt/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  index      : {}".format(data["indexState"]))
print("[INFO]  store      : {}".format(data["sessionStoreState"]))
print("[INFO]  manifest   : {}".format(data["manifestState"]))
print("[INFO]  selection  : {}".format(data["selectionState"]))
print("[INFO]  restore    : {}".format(data["restoreState"]))
print("[INFO]  content    : {}".format(data["contentState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  index-policy : {} localStoreConfigured={} "
    "manifestReadEnabled={} transcriptReadEnabled={}".format(
        policy["state"],
        b(policy["localStoreConfigured"]),
        b(policy["manifestReadEnabled"]),
        b(policy["transcriptReadEnabled"]),
    )
)
print(
    "[INFO]  empty      : {} itemCount={} displayKind={}".format(
        empty["state"],
        empty["itemCount"],
        empty["displayKind"],
    )
)
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "sessionIndexDisplayOnly={} writesArtifacts={} readsArtifacts={} "
    "readsSessionManifest={} readsTranscript={} sessionPersistence={} "
    "transcriptPersistence={} promptContentIncluded={} "
    "responseContentIncluded={} messageBodiesIncluded={} summaryIncluded={} "
    "sessionTitleIncluded={} modelExecution={} runtimeExecution={} "
    "kv260Access={} networkCalls={} providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["sessionIndexDisplayOnly"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["readsSessionManifest"]),
        b(flags["readsTranscript"]),
        b(flags["sessionPersistence"]),
        b(flags["transcriptPersistence"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["summaryIncluded"]),
        b(flags["sessionTitleIncluded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat session index JSON could not be summarized"
        return 1
    fi

    HEAD "chat session index"
    printf '%s\n' "$CHAT_SESSION_INDEX_SUMMARY"
}

print_chat_session_store_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SESSION_STORE_POLICY_STUB="$ROOT_DIR/scripts/chat-session-store-policy-stub.sh"

    if [ ! -f "$CHAT_SESSION_STORE_POLICY_STUB" ]; then
        ERROR "chat session-store policy stub not found: $CHAT_SESSION_STORE_POLICY_STUB"
        return 1
    fi

    if ! CHAT_SESSION_STORE_POLICY_JSON="$(bash "$CHAT_SESSION_STORE_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat session-store policy stub failed"
        printf '%s\n' "$CHAT_SESSION_STORE_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_SESSION_STORE_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_SESSION_STORE_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["sessionStorePolicy"]

def b(value):
    return "true" if value else "false"

surfaces = " ".join(
    "{}={}:{}".format(surface["surfaceId"], surface["state"], b(surface["enabled"]))
    for surface in data["storeSurfaces"]
)
controls = " ".join(
    "{}={}:{}".format(control["controlId"], control["state"], b(control["enabled"]))
    for control in data["storeControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-session-store-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no config/path/manifest/session-store/transcript/title/prompt/model/runtime/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  policy     : {}".format(data["sessionStorePolicyState"]))
print("[INFO]  store      : {}".format(data["storeState"]))
print("[INFO]  path       : {}".format(data["storePathState"]))
print("[INFO]  manifest   : {}".format(data["manifestState"]))
print("[INFO]  read       : {}".format(data["readState"]))
print("[INFO]  write      : {}".format(data["writeState"]))
print("[INFO]  delete     : {}".format(data["deleteState"]))
print("[INFO]  retention  : {}".format(data["retentionState"]))
print("[INFO]  migration  : {}".format(data["migrationState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  session-store-policy : {} mode={} storeConfigured={} "
    "storePathConfigured={} manifestSchemaConfigured={} readEnabled={} "
    "writeEnabled={} deleteEnabled={} retentionEnabled={} "
    "migrationEnabled={}".format(
        policy["state"],
        policy["mode"],
        b(policy["storeConfigured"]),
        b(policy["storePathConfigured"]),
        b(policy["manifestSchemaConfigured"]),
        b(policy["readEnabled"]),
        b(policy["writeEnabled"]),
        b(policy["deleteEnabled"]),
        b(policy["retentionEnabled"]),
        b(policy["migrationEnabled"]),
    )
)
print("[INFO]  surfaces   : {}".format(surfaces))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "sessionStorePolicyDisplayOnly={} storeMetadataOnly={} "
    "storeConfigured={} storePathConfigured={} storePathIncluded={} "
    "configRead={} configWrite={} readsSessionStore={} "
    "sessionStoreRead={} sessionStoreWrite={} readsSessionManifest={} "
    "manifestContentIncluded={} sessionRecordIncluded={} "
    "sessionPersistence={} sessionDeletion={} retentionPolicyActive={} "
    "migrationAttempted={} readsSessionTitle={} sessionTitleIncluded={} "
    "readsTranscript={} promptContentIncluded={} responseContentIncluded={} "
    "writesArtifacts={} readsArtifacts={} modelExecution={} "
    "runtimeExecution={} kv260Access={} hardwareAccess={} networkCalls={} "
    "providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["sessionStorePolicyDisplayOnly"]),
        b(flags["storeMetadataOnly"]),
        b(flags["storeConfigured"]),
        b(flags["storePathConfigured"]),
        b(flags["storePathIncluded"]),
        b(flags["configRead"]),
        b(flags["configWrite"]),
        b(flags["readsSessionStore"]),
        b(flags["sessionStoreRead"]),
        b(flags["sessionStoreWrite"]),
        b(flags["readsSessionManifest"]),
        b(flags["manifestContentIncluded"]),
        b(flags["sessionRecordIncluded"]),
        b(flags["sessionPersistence"]),
        b(flags["sessionDeletion"]),
        b(flags["retentionPolicyActive"]),
        b(flags["migrationAttempted"]),
        b(flags["readsSessionTitle"]),
        b(flags["sessionTitleIncluded"]),
        b(flags["readsTranscript"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat session-store policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat session store policy"
    printf '%s\n' "$CHAT_SESSION_STORE_POLICY_SUMMARY"
}

print_chat_session_title_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SESSION_TITLE_POLICY_STUB="$ROOT_DIR/scripts/chat-session-title-policy-stub.sh"

    if [ ! -f "$CHAT_SESSION_TITLE_POLICY_STUB" ]; then
        ERROR "chat session title-policy stub not found: $CHAT_SESSION_TITLE_POLICY_STUB"
        return 1
    fi

    if ! CHAT_SESSION_TITLE_POLICY_JSON="$(bash "$CHAT_SESSION_TITLE_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat session title-policy stub failed"
        printf '%s\n' "$CHAT_SESSION_TITLE_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_SESSION_TITLE_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_SESSION_TITLE_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["titlePolicy"]
placeholder = data["placeholderTitle"]
controls = " ".join(
    "{}={}".format(control["controlId"], control["state"])
    for control in data["titleControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-session-title-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no session-store/title/transcript/prompt/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  title      : {}".format(data["titlePolicyState"]))
print("[INFO]  source     : {}".format(data["titleSourceState"]))
print("[INFO]  display    : {}".format(data["titleDisplayState"]))
print("[INFO]  generation : {}".format(data["generationState"]))
print("[INFO]  rename     : {}".format(data["renameState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  title-policy : {} displayMode={} titleReadEnabled={} "
    "titleGenerationEnabled={} titleRenameEnabled={} "
    "titlePersistenceEnabled={} summaryReadEnabled={}".format(
        policy["state"],
        policy["displayMode"],
        b(policy["titleReadEnabled"]),
        b(policy["titleGenerationEnabled"]),
        b(policy["titleRenameEnabled"]),
        b(policy["titlePersistenceEnabled"]),
        b(policy["summaryReadEnabled"]),
    )
)
print(
    "[INFO]  placeholder : {} displayKind={} contentIncluded={}".format(
        placeholder["state"],
        placeholder["displayKind"],
        b(placeholder["contentIncluded"]),
    )
)
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "sessionTitlePolicyDisplayOnly={} writesArtifacts={} readsArtifacts={} "
    "readsSessionManifest={} readsSessionTitle={} readsTranscript={} "
    "sessionStoreRead={} titleContentIncluded={} sessionTitleIncluded={} "
    "sessionTitleGenerated={} titleRenameImplemented={} titlePersistence={} "
    "summaryIncluded={} promptContentIncluded={} responseContentIncluded={} "
    "modelExecution={} runtimeExecution={} kv260Access={} networkCalls={} "
    "providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["sessionTitlePolicyDisplayOnly"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["readsSessionManifest"]),
        b(flags["readsSessionTitle"]),
        b(flags["readsTranscript"]),
        b(flags["sessionStoreRead"]),
        b(flags["titleContentIncluded"]),
        b(flags["sessionTitleIncluded"]),
        b(flags["sessionTitleGenerated"]),
        b(flags["titleRenameImplemented"]),
        b(flags["titlePersistence"]),
        b(flags["summaryIncluded"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat session title-policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat session title policy"
    printf '%s\n' "$CHAT_SESSION_TITLE_POLICY_SUMMARY"
}

print_chat_audit_event_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_AUDIT_EVENT_STUB="$ROOT_DIR/scripts/chat-audit-event-stub.sh"

    if [ ! -f "$CHAT_AUDIT_EVENT_STUB" ]; then
        ERROR "chat audit-event stub not found: $CHAT_AUDIT_EVENT_STUB"
        return 1
    fi

    if ! CHAT_AUDIT_EVENT_JSON="$(bash "$CHAT_AUDIT_EVENT_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat audit-event stub failed"
        printf '%s\n' "$CHAT_AUDIT_EVENT_JSON" >&2
        return 1
    fi

    if ! CHAT_AUDIT_EVENT_SUMMARY="$(
        printf '%s\n' "$CHAT_AUDIT_EVENT_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
envelope = data["eventEnvelope"]
redaction = data["redactionPolicy"]
fields = " ".join(
    "{}={}".format(field["fieldId"], field["state"])
    for field in data["auditFields"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-audit-event-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/response/transcript content/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  audit      : {}".format(data["auditState"]))
print("[INFO]  event      : {}".format(data["eventState"]))
print("[INFO]  logging    : {}".format(data["loggingState"]))
print("[INFO]  kind       : {}".format(data["eventKind"]))
print("[INFO]  outcome    : {}".format(data["eventOutcome"]))
print("[INFO]  content    : {}".format(data["contentState"]))
print("[INFO]  persistence: {}".format(data["persistenceState"]))
print("[INFO]  storage    : {}".format(data["storageState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  envelope   : {} targetIncluded={} sessionRefIncluded={} "
    "actorIdentifierIncluded={} promptContentIncluded={} "
    "responseContentIncluded={} transcriptContentIncluded={} "
    "runtimeStarted={} modelLoaded={} writeAttempted={}".format(
        envelope["state"],
        b(envelope["targetIncluded"]),
        b(envelope["sessionRefIncluded"]),
        b(envelope["actorIdentifierIncluded"]),
        b(envelope["promptContentIncluded"]),
        b(envelope["responseContentIncluded"]),
        b(envelope["transcriptContentIncluded"]),
        b(envelope["runtimeStarted"]),
        b(envelope["modelLoaded"]),
        b(envelope["writeAttempted"]),
    )
)
print(
    "[INFO]  redaction  : {} promptContentIncluded={} "
    "responseContentIncluded={} transcriptContentIncluded={} "
    "actorIdentifiersIncluded={} privatePathsIncluded={} "
    "secretsIncluded={} tokensIncluded={} rawLogsIncluded={} "
    "hardwareDumpsIncluded={} generatedBlobsIncluded={} "
    "modelPathsIncluded={}".format(
        redaction["state"],
        b(redaction["promptContentIncluded"]),
        b(redaction["responseContentIncluded"]),
        b(redaction["transcriptContentIncluded"]),
        b(redaction["actorIdentifiersIncluded"]),
        b(redaction["privatePathsIncluded"]),
        b(redaction["secretsIncluded"]),
        b(redaction["tokensIncluded"]),
        b(redaction["rawLogsIncluded"]),
        b(redaction["hardwareDumpsIncluded"]),
        b(redaction["generatedBlobsIncluded"]),
        b(redaction["modelPathsIncluded"]),
    )
)
print("[INFO]  fields     : {}".format(fields))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "auditEventDisplayOnly={} auditLoggerImplemented={} writesArtifacts={} "
    "readsArtifacts={} attachmentReads={} fileUpload={} clipboardRead={} "
    "clipboardWrite={} promptCapture={} promptContentIncluded={} "
    "promptEchoed={} promptPersistence={} inputAccepted={} sendAttempted={} "
    "responseContentIncluded={} responseGenerated={} "
    "transcriptContentIncluded={} transcriptPersistence={} transcriptExport={} "
    "messageBodiesIncluded={} summaryGenerated={} auditEventPersisted={} "
    "localStoreConfigured={} eventTimestampRecorded={} "
    "actorIdentifierIncluded={} modelExecution={} runtimeExecution={} "
    "kv260Access={} networkCalls={} providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["auditEventDisplayOnly"]),
        b(flags["auditLoggerImplemented"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["attachmentReads"]),
        b(flags["fileUpload"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["promptCapture"]),
        b(flags["promptContentIncluded"]),
        b(flags["promptEchoed"]),
        b(flags["promptPersistence"]),
        b(flags["inputAccepted"]),
        b(flags["sendAttempted"]),
        b(flags["responseContentIncluded"]),
        b(flags["responseGenerated"]),
        b(flags["transcriptContentIncluded"]),
        b(flags["transcriptPersistence"]),
        b(flags["transcriptExport"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["summaryGenerated"]),
        b(flags["auditEventPersisted"]),
        b(flags["localStoreConfigured"]),
        b(flags["eventTimestampRecorded"]),
        b(flags["actorIdentifierIncluded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat audit-event JSON could not be summarized"
        return 1
    fi

    HEAD "chat audit event"
    printf '%s\n' "$CHAT_AUDIT_EVENT_SUMMARY"
}

print_chat_send_result_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SEND_RESULT_STUB="$ROOT_DIR/scripts/chat-send-result-stub.sh"

    if [ ! -f "$CHAT_SEND_RESULT_STUB" ]; then
        ERROR "chat send-result stub not found: $CHAT_SEND_RESULT_STUB"
        return 1
    fi

    if ! CHAT_SEND_RESULT_JSON="$(bash "$CHAT_SEND_RESULT_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat send-result stub failed"
        printf '%s\n' "$CHAT_SEND_RESULT_JSON" >&2
        return 1
    fi

    if ! CHAT_SEND_RESULT_SUMMARY="$(
        printf '%s\n' "$CHAT_SEND_RESULT_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
envelope = data["resultEnvelope"]
reasons = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)
messages = " ".join(
    "{}={}".format(message["messageId"], message["state"])
    for message in data["displayMessages"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-send-result-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/response/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  result     : {}".format(data["resultState"]))
print("[INFO]  attempt    : {}".format(data["sendAttemptState"]))
print("[INFO]  prompt     : {}".format(data["promptHandlingState"]))
print("[INFO]  response   : {}".format(data["responseState"]))
print("[INFO]  runtime    : {}".format(data["runtimeState"]))
print("[INFO]  model load : {}".format(data["modelState"]))
print("[INFO]  session    : {}".format(data["sessionState"]))
print(
    "[INFO]  envelope   : {} inputAccepted={} sendAttempted={} "
    "promptContentIncluded={} promptEchoed={} responseGenerated={} "
    "responseContentIncluded={}".format(
        envelope["state"],
        b(envelope["inputAccepted"]),
        b(envelope["sendAttempted"]),
        b(envelope["promptContentIncluded"]),
        b(envelope["promptEchoed"]),
        b(envelope["responseGenerated"]),
        b(envelope["responseContentIncluded"]),
    )
)
print("[INFO]  blocked    : {}".format(reasons))
print("[INFO]  messages   : {}".format(messages))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "sendResultDisplayOnly={} writesArtifacts={} readsArtifacts={} "
    "attachmentReads={} fileUpload={} clipboardRead={} clipboardWrite={} "
    "promptCapture={} promptContentIncluded={} promptEchoed={} "
    "promptPersistence={} inputAccepted={} sendAttempted={} "
    "responseContentIncluded={} responseGenerated={} modelLoadAttempted={} "
    "modelLoaded={} modelExecution={} runtimeExecution={} kv260Access={} "
    "networkCalls={} providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["sendResultDisplayOnly"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["attachmentReads"]),
        b(flags["fileUpload"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["promptCapture"]),
        b(flags["promptContentIncluded"]),
        b(flags["promptEchoed"]),
        b(flags["promptPersistence"]),
        b(flags["inputAccepted"]),
        b(flags["sendAttempted"]),
        b(flags["responseContentIncluded"]),
        b(flags["responseGenerated"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat send-result JSON could not be summarized"
        return 1
    fi

    HEAD "chat send result"
    printf '%s\n' "$CHAT_SEND_RESULT_SUMMARY"
}

print_chat_transcript_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_TRANSCRIPT_POLICY_STUB="$ROOT_DIR/scripts/chat-transcript-policy-stub.sh"

    if [ ! -f "$CHAT_TRANSCRIPT_POLICY_STUB" ]; then
        ERROR "chat transcript policy stub not found: $CHAT_TRANSCRIPT_POLICY_STUB"
        return 1
    fi

    if ! CHAT_TRANSCRIPT_POLICY_JSON="$(bash "$CHAT_TRANSCRIPT_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat transcript policy stub failed"
        printf '%s\n' "$CHAT_TRANSCRIPT_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_TRANSCRIPT_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_TRANSCRIPT_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
retention = data["retentionPolicy"]
content = data["contentPolicy"]
export = data["exportPolicy"]
formats = ",".join(export["exportFormats"]) or "none"
retention_days = retention["retentionDays"]
retention_days_text = "none" if retention_days is None else str(retention_days)
surfaces = " ".join(
    "{}={}".format(surface["surfaceId"], surface["state"])
    for surface in data["uiSurfaces"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-transcript-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/response/transcript content/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  transcript : {}".format(data["transcriptState"]))
print("[INFO]  message    : {}".format(data["messageContentState"]))
print("[INFO]  retention  : {}".format(data["retentionState"]))
print("[INFO]  export     : {}".format(data["exportState"]))
print("[INFO]  storage    : {}".format(data["storageState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  retention-policy : {} localStoreConfigured={} "
    "sessionPersistence={} transcriptPersistence={} retentionDays={}".format(
        retention["state"],
        b(retention["localStoreConfigured"]),
        b(retention["sessionPersistence"]),
        b(retention["transcriptPersistence"]),
        retention_days_text,
    )
)
print(
    "[INFO]  content-policy   : {} contentIncluded={} "
    "promptContentIncluded={} responseContentIncluded={} "
    "messageBodiesIncluded={} summaryIncluded={}".format(
        content["state"],
        b(content["contentIncluded"]),
        b(content["promptContentIncluded"]),
        b(content["responseContentIncluded"]),
        b(content["messageBodiesIncluded"]),
        b(content["summaryIncluded"]),
    )
)
print(
    "[INFO]  export-policy    : {} exportEnabled={} "
    "summaryExportState={} contentExportState={} formats={}".format(
        export["state"],
        b(export["exportEnabled"]),
        export["summaryExportState"],
        export["contentExportState"],
        formats,
    )
)
print("[INFO]  surfaces   : {}".format(surfaces))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "transcriptPolicyDisplayOnly={} writesArtifacts={} readsArtifacts={} "
    "attachmentReads={} fileUpload={} clipboardRead={} clipboardWrite={} "
    "promptCapture={} promptContentIncluded={} promptEchoed={} "
    "promptPersistence={} responseContentIncluded={} responseGenerated={} "
    "messageBodiesIncluded={} summaryGenerated={} transcriptPersistence={} "
    "transcriptExport={} localStoreConfigured={} modelExecution={} "
    "runtimeExecution={} kv260Access={} networkCalls={} providerCalls={} "
    "executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["transcriptPolicyDisplayOnly"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["attachmentReads"]),
        b(flags["fileUpload"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["promptCapture"]),
        b(flags["promptContentIncluded"]),
        b(flags["promptEchoed"]),
        b(flags["promptPersistence"]),
        b(flags["responseContentIncluded"]),
        b(flags["responseGenerated"]),
        b(flags["messageBodiesIncluded"]),
        b(flags["summaryGenerated"]),
        b(flags["transcriptPersistence"]),
        b(flags["transcriptExport"]),
        b(flags["localStoreConfigured"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat transcript policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat transcript policy"
    printf '%s\n' "$CHAT_TRANSCRIPT_POLICY_SUMMARY"
}

print_chat_composer_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_COMPOSER_STUB="$ROOT_DIR/scripts/chat-composer-stub.sh"

    if [ ! -f "$CHAT_COMPOSER_STUB" ]; then
        ERROR "chat composer stub not found: $CHAT_COMPOSER_STUB"
        return 1
    fi

    if ! CHAT_COMPOSER_JSON="$(bash "$CHAT_COMPOSER_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat composer stub failed"
        printf '%s\n' "$CHAT_COMPOSER_JSON" >&2
        return 1
    fi

    if ! CHAT_COMPOSER_SUMMARY="$(
        printf '%s\n' "$CHAT_COMPOSER_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
controls = " ".join(
    "{}={}".format(control["controlId"], control["state"])
    for control in data["composerControls"]
)
rules = " ".join(
    "{}={}".format(rule["ruleId"], rule["state"])
    for rule in data["validationRules"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-composer-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/provider/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  composer   : {}".format(data["composerState"]))
print("[INFO]  input      : {}".format(data["inputBufferState"]))
print("[INFO]  send       : {}".format(data["sendControlState"]))
print("[INFO]  attachment : {}".format(data["attachmentState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print("[INFO]  validation : {}".format(data["validationState"]))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  rules      : {}".format(rules))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "composerDisplayOnly={} writesArtifacts={} readsArtifacts={} "
    "attachmentReads={} fileUpload={} clipboardRead={} clipboardWrite={} "
    "promptContentIncluded={} promptEchoed={} promptPersistence={} "
    "responseContentIncluded={} modelLoadAttempted={} modelLoaded={} "
    "modelExecution={} runtimeExecution={} kv260Access={} networkCalls={} "
    "providerCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["composerDisplayOnly"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["attachmentReads"]),
        b(flags["fileUpload"]),
        b(flags["clipboardRead"]),
        b(flags["clipboardWrite"]),
        b(flags["promptContentIncluded"]),
        b(flags["promptEchoed"]),
        b(flags["promptPersistence"]),
        b(flags["responseContentIncluded"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat composer JSON could not be summarized"
        return 1
    fi

    HEAD "chat composer"
    printf '%s\n' "$CHAT_COMPOSER_SUMMARY"
}

print_chat_readiness_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_READINESS_STUB="$ROOT_DIR/scripts/chat-readiness-stub.sh"

    if [ ! -f "$CHAT_READINESS_STUB" ]; then
        ERROR "chat readiness stub not found: $CHAT_READINESS_STUB"
        return 1
    fi

    if ! CHAT_READINESS_JSON="$(bash "$CHAT_READINESS_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat readiness stub failed"
        printf '%s\n' "$CHAT_READINESS_JSON" >&2
        return 1
    fi

    if ! CHAT_READINESS_SUMMARY="$(
        printf '%s\n' "$CHAT_READINESS_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
checks = " ".join(
    "{}={}".format(check["checkId"], check["state"])
    for check in data["readinessChecks"]
)
errors = " ".join(
    "{}={}".format(error["errorId"], error["state"])
    for error in data["errorTaxonomy"]
)
actions = " ".join(
    "{}={}".format(action["actionId"], action["state"])
    for action in data["recoveryActions"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-readiness-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/model/provider/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  overall    : {}".format(data["overallState"]))
print("[INFO]  input      : {}".format(data["inputReadinessState"]))
print("[INFO]  send       : {}".format(data["sendReadinessState"]))
print("[INFO]  recovery   : {}".format(data["recoveryState"]))
print("[INFO]  evidence   : {}".format(data["evidenceState"]))
print("[INFO]  checks     : {}".format(checks))
print("[INFO]  errors     : {}".format(errors))
print("[INFO]  actions    : {}".format(actions))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "readinessDisplayOnly={} writesArtifacts={} readsArtifacts={} "
    "promptContentIncluded={} responseContentIncluded={} sessionPersistence={} "
    "modelLoadAttempted={} modelLoaded={} modelExecution={} runtimeExecution={} "
    "responseGenerated={} kv260Access={} opensSerialPort={} networkCalls={} "
    "sshExecution={} providerCalls={} cloudCalls={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["readinessDisplayOnly"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["sessionPersistence"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["responseGenerated"]),
        b(flags["kv260Access"]),
        b(flags["opensSerialPort"]),
        b(flags["networkCalls"]),
        b(flags["sshExecution"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat readiness JSON could not be summarized"
        return 1
    fi

    HEAD "chat readiness"
    printf '%s\n' "$CHAT_READINESS_SUMMARY"
}

print_chat_model_status_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_MODEL_STATUS_STUB="$ROOT_DIR/scripts/chat-model-status-stub.sh"

    if [ ! -f "$CHAT_MODEL_STATUS_STUB" ]; then
        ERROR "chat model status stub not found: $CHAT_MODEL_STATUS_STUB"
        return 1
    fi

    if ! CHAT_MODEL_STATUS_JSON="$(bash "$CHAT_MODEL_STATUS_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat model status stub failed"
        printf '%s\n' "$CHAT_MODEL_STATUS_JSON" >&2
        return 1
    fi

    if ! CHAT_MODEL_STATUS_SUMMARY="$(
        printf '%s\n' "$CHAT_MODEL_STATUS_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
rows = " ".join(
    "{}={}".format(row["rowId"], row["state"])
    for row in data["statusRows"]
)
actions = " ".join(
    "{}={}".format(action["actionId"], action["state"])
    for action in data["loadActions"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-model-status-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no model load/provider/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  display    : {}".format(data["displayState"]))
print("[INFO]  descriptor : {}".format(data["descriptorState"]))
print("[INFO]  assets     : {}".format(data["assetState"]))
print("[INFO]  load       : {}".format(data["loadState"]))
print("[INFO]  runtime    : {}".format(data["runtimeState"]))
print("[INFO]  context    : {}".format(data["contextState"]))
print("[INFO]  response   : {}".format(data["responseState"]))
print("[INFO]  provider   : {}".format(data["providerState"]))
print("[INFO]  rows       : {}".format(rows))
print("[INFO]  actions    : {}".format(actions))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "statusDisplayOnly={} modelLoadAttempted={} modelLoaded={} "
    "modelExecution={} runtimeExecution={} responseGenerated={} "
    "kv260Access={} providerCalls={} cloudCalls={} networkCalls={} "
    "modelAssetPathsIncluded={} modelWeightPathsIncluded={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["statusDisplayOnly"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["responseGenerated"]),
        b(flags["kv260Access"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["modelAssetPathsIncluded"]),
        b(flags["modelWeightPathsIncluded"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat model status JSON could not be summarized"
        return 1
    fi

    HEAD "chat model status"
    printf '%s\n' "$CHAT_MODEL_STATUS_SUMMARY"
}

print_chat_model_selection_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_MODEL_SELECTION_POLICY_STUB="$ROOT_DIR/scripts/chat-model-selection-policy-stub.sh"

    if [ ! -f "$CHAT_MODEL_SELECTION_POLICY_STUB" ]; then
        ERROR "chat model-selection policy stub not found: $CHAT_MODEL_SELECTION_POLICY_STUB"
        return 1
    fi

    if ! CHAT_MODEL_SELECTION_POLICY_JSON="$(bash "$CHAT_MODEL_SELECTION_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat model-selection policy stub failed"
        printf '%s\n' "$CHAT_MODEL_SELECTION_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_MODEL_SELECTION_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_MODEL_SELECTION_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["selectionPolicy"]

def b(value):
    return "true" if value else "false"

options = " ".join(
    "{}={}:{}:{}".format(
        option["optionId"],
        option["state"],
        b(option["selected"]),
        b(option["enabled"]),
    )
    for option in data["modelOptions"]
)
controls = " ".join(
    "{}={}:{}".format(control["controlId"], control["state"], b(control["enabled"]))
    for control in data["selectionControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-model-selection-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no catalog/config/model asset path/read/load/runtime/provider/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  selection  : {}".format(data["selectionState"]))
print("[INFO]  catalog    : {}".format(data["catalogState"]))
print("[INFO]  picker     : {}".format(data["pickerState"]))
print("[INFO]  selected   : {}".format(data["selectedModelState"]))
print("[INFO]  descriptor : {}".format(data["descriptorState"]))
print("[INFO]  asset disc : {}".format(data["assetDiscoveryState"]))
print("[INFO]  asset paths: {}".format(data["assetPathState"]))
print("[INFO]  fallback   : {}".format(data["providerFallbackState"]))
print("[INFO]  load req   : {}".format(data["loadRequestState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  model-selection : {} mode={} staticOptionCount={} "
    "dynamicCatalogConfigured={} localCatalogRead={} "
    "assetDiscoveryEnabled={} selectionEnabled={} "
    "selectionPersistenceEnabled={} providerFallbackEnabled={} "
    "loadRequestEnabled={}".format(
        policy["state"],
        policy["mode"],
        policy["staticOptionCount"],
        b(policy["dynamicCatalogConfigured"]),
        b(policy["localCatalogRead"]),
        b(policy["assetDiscoveryEnabled"]),
        b(policy["selectionEnabled"]),
        b(policy["selectionPersistenceEnabled"]),
        b(policy["providerFallbackEnabled"]),
        b(policy["loadRequestEnabled"]),
    )
)
print("[INFO]  options    : {}".format(options))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "selectionPolicyDisplayOnly={} staticOptionOnly={} "
    "dynamicCatalogConfigured={} modelCatalogRead={} "
    "dynamicCatalogDiscovery={} modelSelectionPersisted={} "
    "modelSelectionAcceptedFromUser={} modelOptionsFromConfig={} "
    "modelAssetPathsIncluded={} modelAssetPathRead={} modelAssetRead={} "
    "configRead={} environmentRead={} providerConfigRead={} "
    "providerCalls={} cloudCalls={} networkCalls={} "
    "modelLoadAttempted={} modelLoaded={} modelExecution={} "
    "runtimeExecution={} kv260Access={} hardwareAccess={} "
    "writesArtifacts={} readsArtifacts={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["selectionPolicyDisplayOnly"]),
        b(flags["staticOptionOnly"]),
        b(flags["dynamicCatalogConfigured"]),
        b(flags["modelCatalogRead"]),
        b(flags["dynamicCatalogDiscovery"]),
        b(flags["modelSelectionPersisted"]),
        b(flags["modelSelectionAcceptedFromUser"]),
        b(flags["modelOptionsFromConfig"]),
        b(flags["modelAssetPathsIncluded"]),
        b(flags["modelAssetPathRead"]),
        b(flags["modelAssetRead"]),
        b(flags["configRead"]),
        b(flags["environmentRead"]),
        b(flags["providerConfigRead"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat model-selection policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat model selection policy"
    printf '%s\n' "$CHAT_MODEL_SELECTION_POLICY_SUMMARY"
}

print_chat_context_policy_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_CONTEXT_POLICY_STUB="$ROOT_DIR/scripts/chat-context-policy-stub.sh"

    if [ ! -f "$CHAT_CONTEXT_POLICY_STUB" ]; then
        ERROR "chat context-policy stub not found: $CHAT_CONTEXT_POLICY_STUB"
        return 1
    fi

    if ! CHAT_CONTEXT_POLICY_JSON="$(bash "$CHAT_CONTEXT_POLICY_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat context-policy stub failed"
        printf '%s\n' "$CHAT_CONTEXT_POLICY_JSON" >&2
        return 1
    fi

    if ! CHAT_CONTEXT_POLICY_SUMMARY="$(
        printf '%s\n' "$CHAT_CONTEXT_POLICY_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["contextPolicy"]

def b(value):
    return "true" if value else "false"

slots = " ".join(
    "{}={}:{}".format(slot["slotId"], slot["state"], b(slot["enabled"]))
    for slot in data["contextSlots"]
)
controls = " ".join(
    "{}={}:{}".format(control["controlId"], control["state"], b(control["enabled"]))
    for control in data["contextControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-context-policy-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/transcript/tokenizer/runtime/model/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  context   : {}".format(data["contextPolicyState"]))
print("[INFO]  window    : {}".format(data["contextWindowState"]))
print("[INFO]  budget    : {}".format(data["budgetState"]))
print("[INFO]  tokens    : {}".format(data["tokenizationState"]))
print("[INFO]  prompt    : {}".format(data["promptContentState"]))
print("[INFO]  transcript: {}".format(data["transcriptState"]))
print("[INFO]  summary   : {}".format(data["summaryState"]))
print("[INFO]  truncate  : {}".format(data["truncationState"]))
print("[INFO]  assembly  : {}".format(data["contextAssemblyState"]))
print("[INFO]  handoff   : {}".format(data["runtimeHandoffState"]))
print("[INFO]  privacy   : {}".format(data["privacyState"]))
print(
    "[INFO]  context-policy : {} mode={} contextWindowConfigured={} "
    "tokenBudgetConfigured={} tokenizerConfigured={} tokenCountingEnabled={} "
    "promptReadEnabled={} transcriptReadEnabled={} summaryReadEnabled={} "
    "truncationEnabled={} contextAssemblyEnabled={} "
    "runtimeHandoffEnabled={}".format(
        policy["state"],
        policy["mode"],
        b(policy["contextWindowConfigured"]),
        b(policy["tokenBudgetConfigured"]),
        b(policy["tokenizerConfigured"]),
        b(policy["tokenCountingEnabled"]),
        b(policy["promptReadEnabled"]),
        b(policy["transcriptReadEnabled"]),
        b(policy["summaryReadEnabled"]),
        b(policy["truncationEnabled"]),
        b(policy["contextAssemblyEnabled"]),
        b(policy["runtimeHandoffEnabled"]),
    )
)
print("[INFO]  slots      : {}".format(slots))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "contextPolicyDisplayOnly={} contextMetadataOnly={} "
    "contextWindowConfigured={} contextWindowSizeIncluded={} "
    "tokenBudgetConfigured={} tokenBudgetIncluded={} "
    "tokenizerConfigured={} tokenCountingEnabled={} "
    "tokenCountMeasured={} tokenContentIncluded={} "
    "promptCapture={} promptRead={} promptContentIncluded={} "
    "readsTranscript={} summaryGenerated={} "
    "contextAssemblyAttempted={} contextTruncationAttempted={} "
    "runtimeHandoffAttempted={} modelExecution={} runtimeExecution={} "
    "kv260Access={} hardwareAccess={} networkCalls={} providerCalls={} "
    "executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["contextPolicyDisplayOnly"]),
        b(flags["contextMetadataOnly"]),
        b(flags["contextWindowConfigured"]),
        b(flags["contextWindowSizeIncluded"]),
        b(flags["tokenBudgetConfigured"]),
        b(flags["tokenBudgetIncluded"]),
        b(flags["tokenizerConfigured"]),
        b(flags["tokenCountingEnabled"]),
        b(flags["tokenCountMeasured"]),
        b(flags["tokenContentIncluded"]),
        b(flags["promptCapture"]),
        b(flags["promptRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["readsTranscript"]),
        b(flags["summaryGenerated"]),
        b(flags["contextAssemblyAttempted"]),
        b(flags["contextTruncationAttempted"]),
        b(flags["runtimeHandoffAttempted"]),
        b(flags["modelExecution"]),
        b(flags["runtimeExecution"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat context-policy JSON could not be summarized"
        return 1
    fi

    HEAD "chat context policy"
    printf '%s\n' "$CHAT_CONTEXT_POLICY_SUMMARY"
}

print_chat_model_load_request_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_MODEL_LOAD_REQUEST_STUB="$ROOT_DIR/scripts/chat-model-load-request-stub.sh"

    if [ ! -f "$CHAT_MODEL_LOAD_REQUEST_STUB" ]; then
        ERROR "chat model-load request stub not found: $CHAT_MODEL_LOAD_REQUEST_STUB"
        return 1
    fi

    if ! CHAT_MODEL_LOAD_REQUEST_JSON="$(bash "$CHAT_MODEL_LOAD_REQUEST_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat model-load request stub failed"
        printf '%s\n' "$CHAT_MODEL_LOAD_REQUEST_JSON" >&2
        return 1
    fi

    if ! CHAT_MODEL_LOAD_REQUEST_SUMMARY="$(
        printf '%s\n' "$CHAT_MODEL_LOAD_REQUEST_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
policy = data["loadRequestPolicy"]

def b(value):
    return "true" if value else "false"

inputs = " ".join(
    "{}={}:{}".format(item["inputId"], item["state"], b(item["enabled"]))
    for item in data["loadInputs"]
)
controls = " ".join(
    "{}={}:{}".format(control["controlId"], control["state"], b(control["enabled"]))
    for control in data["loadControls"]
)
blocked = " ".join(
    "{}={}".format(reason["reasonId"], reason["state"])
    for reason in data["blockedReasons"]
)

print("[INFO]  source     : scripts/chat-model-load-request-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no model asset path/read/load/runtime/provider/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  request    : {}".format(data["loadRequestState"]))
print("[INFO]  selected   : {}".format(data["selectedModelState"]))
print("[INFO]  descriptor : {}".format(data["descriptorState"]))
print("[INFO]  assets     : {}".format(data["assetInputState"]))
print("[INFO]  paths      : {}".format(data["assetPathState"]))
print("[INFO]  checksums  : {}".format(data["checksumState"]))
print("[INFO]  plan       : {}".format(data["loadPlanState"]))
print("[INFO]  preflight  : {}".format(data["runtimePreflightState"]))
print("[INFO]  device     : {}".format(data["deviceSessionState"]))
print("[INFO]  warmup     : {}".format(data["warmupState"]))
print("[INFO]  unload     : {}".format(data["unloadState"]))
print("[INFO]  privacy    : {}".format(data["privacyState"]))
print(
    "[INFO]  model-load-request : {} mode={} descriptorSelected={} "
    "modelAssetsConfigured={} assetPathsConfigured={} checksumsAvailable={} "
    "runtimeReady={} deviceSessionReady={} loadEnabled={} warmupEnabled={} "
    "unloadEnabled={}".format(
        policy["state"],
        policy["mode"],
        b(policy["descriptorSelected"]),
        b(policy["modelAssetsConfigured"]),
        b(policy["assetPathsConfigured"]),
        b(policy["checksumsAvailable"]),
        b(policy["runtimeReady"]),
        b(policy["deviceSessionReady"]),
        b(policy["loadEnabled"]),
        b(policy["warmupEnabled"]),
        b(policy["unloadEnabled"]),
    )
)
print("[INFO]  inputs     : {}".format(inputs))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  blocked    : {}".format(blocked))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "loadRequestDisplayOnly={} modelDescriptorMetadataOnly={} "
    "modelAssetsConfigured={} modelAssetPathsConfigured={} "
    "modelAssetPathsIncluded={} modelWeightPathsIncluded={} "
    "modelAssetRead={} modelWeightRead={} tokenizerRead={} "
    "checksumManifestRead={} checksumValuesIncluded={} "
    "modelIntegrityChecked={} configRead={} configWrite={} "
    "environmentRead={} promptContentIncluded={} responseContentIncluded={} "
    "runtimePreflightExecuted={} runtimeStarted={} runtimeExecution={} "
    "modelLoadAttempted={} modelLoaded={} modelUnloadAttempted={} "
    "modelExecution={} warmupAttempted={} kv260Access={} hardwareAccess={} "
    "networkCalls={} providerCalls={} cloudCalls={} writesArtifacts={} "
    "readsArtifacts={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["loadRequestDisplayOnly"]),
        b(flags["modelDescriptorMetadataOnly"]),
        b(flags["modelAssetsConfigured"]),
        b(flags["modelAssetPathsConfigured"]),
        b(flags["modelAssetPathsIncluded"]),
        b(flags["modelWeightPathsIncluded"]),
        b(flags["modelAssetRead"]),
        b(flags["modelWeightRead"]),
        b(flags["tokenizerRead"]),
        b(flags["checksumManifestRead"]),
        b(flags["checksumValuesIncluded"]),
        b(flags["modelIntegrityChecked"]),
        b(flags["configRead"]),
        b(flags["configWrite"]),
        b(flags["environmentRead"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["runtimePreflightExecuted"]),
        b(flags["runtimeStarted"]),
        b(flags["runtimeExecution"]),
        b(flags["modelLoadAttempted"]),
        b(flags["modelLoaded"]),
        b(flags["modelUnloadAttempted"]),
        b(flags["modelExecution"]),
        b(flags["warmupAttempted"]),
        b(flags["kv260Access"]),
        b(flags["hardwareAccess"]),
        b(flags["networkCalls"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["writesArtifacts"]),
        b(flags["readsArtifacts"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat model-load request JSON could not be summarized"
        return 1
    fi

    HEAD "chat model load request"
    printf '%s\n' "$CHAT_MODEL_LOAD_REQUEST_SUMMARY"
}

print_chat_session_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SESSION_STUB="$ROOT_DIR/scripts/chat-session-stub.sh"
    CHAT_SESSION_LIFECYCLE_STUB="$ROOT_DIR/scripts/chat-session-lifecycle-stub.sh"

    if [ ! -f "$CHAT_SESSION_STUB" ]; then
        ERROR "chat/session stub not found: $CHAT_SESSION_STUB"
        return 1
    fi
    if [ ! -f "$CHAT_SESSION_LIFECYCLE_STUB" ]; then
        ERROR "chat/session lifecycle stub not found: $CHAT_SESSION_LIFECYCLE_STUB"
        return 1
    fi

    if ! CHAT_SESSION_JSON="$(bash "$CHAT_SESSION_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat/session stub failed"
        printf '%s\n' "$CHAT_SESSION_JSON" >&2
        return 1
    fi
    if ! CHAT_SESSION_LIFECYCLE_JSON="$(bash "$CHAT_SESSION_LIFECYCLE_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat/session lifecycle stub failed"
        printf '%s\n' "$CHAT_SESSION_LIFECYCLE_JSON" >&2
        return 1
    fi

    if ! CHAT_SESSION_SUMMARY="$(
        printf '%s\n%s\n' "$CHAT_SESSION_JSON" "$CHAT_SESSION_LIFECYCLE_JSON" | python3 -c '
import json
import sys

decoder = json.JSONDecoder()
text = sys.stdin.read()
data, offset = decoder.raw_decode(text)
lifecycle, _ = decoder.raw_decode(text[offset:].lstrip())
flags = data["safetyFlags"]
lifecycle_flags = lifecycle["safetyFlags"]
controls = " ".join(
    "{}={}".format(control["controlId"], control["state"])
    for control in data["sessionControls"]
)
operations = " ".join(
    "{}={}".format(operation["operationId"], operation["state"])
    for operation in lifecycle["lifecycleOperations"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-session-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/model/provider/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  surface    : {}".format(data["surfaceState"]))
print("[INFO]  chat       : {}".format(data["chatState"]))
print("[INFO]  input      : {}".format(data["inputState"]))
print("[INFO]  send       : {}".format(data["sendState"]))
print("[INFO]  model load : {}".format(data["modelStatus"]))
print("[INFO]  transcript : {}".format(data["transcriptPolicy"]["state"]))
print("[INFO]  response   : {}".format(data["messageEnvelope"]["responseState"]))
print("[INFO]  controls   : {}".format(controls))
print("[INFO]  lifecycle  : {}".format(lifecycle["lifecycleState"]))
print("[INFO]  active     : {}".format(lifecycle["activeSessionState"]))
print("[INFO]  storage    : {}".format(lifecycle["storageState"]))
print("[INFO]  restore    : {}".format(lifecycle["restoreState"]))
print("[INFO]  export     : {}".format(lifecycle["exportState"]))
print("[INFO]  operations : {}".format(operations))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "runtimeExecution={} modelLoaded={} modelExecution={} kv260Access={} "
    "providerCalls={} cloudCalls={} networkCalls={} transcriptPersistence={} "
    "promptContentIncluded={} responseContentIncluded={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["runtimeExecution"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["kv260Access"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["transcriptPersistence"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["executesPccxLab"]),
    )
)
print(
    "[INFO]  lifecycle flags : readOnly={} dataOnly={} deterministic={} "
    "writesArtifacts={} readsArtifacts={} sessionPersistence={} "
    "sessionRestoreImplemented={} sessionClearImplemented={} "
    "summaryExportImplemented={}".format(
        b(lifecycle_flags["readOnly"]),
        b(lifecycle_flags["dataOnly"]),
        b(lifecycle_flags["deterministic"]),
        b(lifecycle_flags["writesArtifacts"]),
        b(lifecycle_flags["readsArtifacts"]),
        b(lifecycle_flags["sessionPersistence"]),
        b(lifecycle_flags["sessionRestoreImplemented"]),
        b(lifecycle_flags["sessionClearImplemented"]),
        b(lifecycle_flags["summaryExportImplemented"]),
    )
)
'
    )"; then
        ERROR "chat/session JSON could not be summarized"
        return 1
    fi

    HEAD "chat/session status"
    printf '%s\n' "$CHAT_SESSION_SUMMARY"
}

print_device_session_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    DEVICE_SESSION_STUB="$ROOT_DIR/scripts/device-session-status-stub.sh"

    if [ ! -f "$DEVICE_SESSION_STUB" ]; then
        ERROR "device/session status stub not found: $DEVICE_SESSION_STUB"
        return 1
    fi

    if ! DEVICE_SESSION_JSON="$(bash "$DEVICE_SESSION_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "device/session status stub failed"
        printf '%s\n' "$DEVICE_SESSION_JSON" >&2
        return 1
    fi

    if ! DEVICE_SESSION_SUMMARY="$(
        printf '%s\n' "$DEVICE_SESSION_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
rows = " ".join(
    "{}={}".format(row["rowId"], row["state"])
    for row in data["statusPanel"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no hardware/model/provider/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  connection : {}".format(data["connectionState"]))
print("[INFO]  discovery  : {}".format(data["discoveryState"]))
print("[INFO]  auth       : {}".format(data["authenticationState"]))
print("[INFO]  runtime    : {}".format(data["runtimeState"]))
print("[INFO]  model load : {}".format(data["modelLoadState"]))
print("[INFO]  session    : {}".format(data["sessionState"]))
print("[INFO]  logs       : {}".format(data["logStreamState"]))
print("[INFO]  diagnostic : {}".format(data["diagnosticsState"]))
print("[INFO]  readiness  : {}".format(data["readinessState"]))
print("[INFO]  panel      : {}".format(rows))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "runtimeExecution={} modelLoaded={} modelExecution={} kv260Access={} "
    "opensSerialPort={} networkCalls={} networkScan={} sshExecution={} "
    "authenticationAttempt={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["runtimeExecution"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["kv260Access"]),
        b(flags["opensSerialPort"]),
        b(flags["networkCalls"]),
        b(flags["networkScan"]),
        b(flags["sshExecution"]),
        b(flags["authenticationAttempt"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "device/session status JSON could not be summarized"
        return 1
    fi

    HEAD "device/session status"
    printf '%s\n' "$DEVICE_SESSION_SUMMARY"
}

print_runtime_readiness_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    READINESS_STUB="$ROOT_DIR/scripts/runtime-readiness-stub.sh"

    if [ ! -f "$READINESS_STUB" ]; then
        ERROR "runtime readiness stub not found: $READINESS_STUB"
        return 1
    fi

    if ! READINESS_JSON="$(bash "$READINESS_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "runtime readiness stub failed"
        printf '%s\n' "$READINESS_JSON" >&2
        return 1
    fi

    if ! READINESS_SUMMARY="$(
        printf '%s\n' "$READINESS_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
performance = data["performanceTargets"][0]
flags = data["safetyFlags"]

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no hardware/model/provider/lab/IDE execution")
print("[INFO]  model      : {} {}".format(data["modelFamily"], data["modelVariant"]))
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  status     : {}".format(data["statusAnswer"]))
print("[INFO]  readiness  : {}".format(data["readinessState"]))
print("[INFO]  evidence   : {}".format(data["evidenceState"]))
print("[INFO]  descriptor : {}".format(data["descriptorState"]))
print("[INFO]  xsim       : {}".format(data["simulationEvidenceState"]))
print("[INFO]  synth      : {}".format(data["vivadoSynthState"]))
print("[INFO]  timing     : {}".format(data["timingEvidenceState"]))
print("[INFO]  impl       : {}".format(data["implementationState"]))
print("[INFO]  bitstream  : {}".format(data["bitstreamState"]))
print("[INFO]  smoke      : {}".format(data["kv260SmokeState"]))
print("[INFO]  runtime    : {}".format(data["runtimeEvidenceState"]))
print("[INFO]  throughput : target-only; {} unmeasured".format(performance["target"]))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "runtimeExecution={} modelLoaded={} modelExecution={} kv260Access={} "
    "providerCalls={} networkCalls={} executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["runtimeExecution"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["kv260Access"]),
        b(flags["providerCalls"]),
        b(flags["networkCalls"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "runtime readiness JSON could not be summarized"
        return 1
    fi

    HEAD "runtime readiness"
    printf '%s\n' "$READINESS_SUMMARY"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --include-runtime-readiness)
            INCLUDE_RUNTIME_READINESS="1"
            shift
            ;;
        --include-device-session)
            INCLUDE_DEVICE_SESSION="1"
            shift
            ;;
        --include-chat-session)
            INCLUDE_CHAT_SESSION="1"
            shift
            ;;
        --include-chat-surface-layout)
            INCLUDE_CHAT_SURFACE_LAYOUT="1"
            shift
            ;;
        --include-chat-empty-state)
            INCLUDE_CHAT_EMPTY_STATE="1"
            shift
            ;;
        --include-chat-local-only-policy)
            INCLUDE_CHAT_LOCAL_ONLY_POLICY="1"
            shift
            ;;
        --include-chat-preferences)
            INCLUDE_CHAT_PREFERENCES="1"
            shift
            ;;
        --include-chat-session-index)
            INCLUDE_CHAT_SESSION_INDEX="1"
            shift
            ;;
        --include-chat-session-store-policy)
            INCLUDE_CHAT_SESSION_STORE_POLICY="1"
            shift
            ;;
        --include-chat-session-title-policy)
            INCLUDE_CHAT_SESSION_TITLE_POLICY="1"
            shift
            ;;
        --include-chat-model-status)
            INCLUDE_CHAT_MODEL_STATUS="1"
            shift
            ;;
        --include-chat-model-selection-policy)
            INCLUDE_CHAT_MODEL_SELECTION_POLICY="1"
            shift
            ;;
        --include-chat-context-policy)
            INCLUDE_CHAT_CONTEXT_POLICY="1"
            shift
            ;;
        --include-chat-model-load-request)
            INCLUDE_CHAT_MODEL_LOAD_REQUEST="1"
            shift
            ;;
        --include-chat-readiness)
            INCLUDE_CHAT_READINESS="1"
            shift
            ;;
        --include-chat-composer)
            INCLUDE_CHAT_COMPOSER="1"
            shift
            ;;
        --include-chat-send-result)
            INCLUDE_CHAT_SEND_RESULT="1"
            shift
            ;;
        --include-chat-transcript-policy)
            INCLUDE_CHAT_TRANSCRIPT_POLICY="1"
            shift
            ;;
        --include-chat-audit-event)
            INCLUDE_CHAT_AUDIT_EVENT="1"
            shift
            ;;
        --include-chat-error-taxonomy)
            INCLUDE_CHAT_ERROR_TAXONOMY="1"
            shift
            ;;
        --include-chat-response-stream)
            INCLUDE_CHAT_RESPONSE_STREAM="1"
            shift
            ;;
        --include-chat-message-list)
            INCLUDE_CHAT_MESSAGE_LIST="1"
            shift
            ;;
        --include-chat-action-bar)
            INCLUDE_CHAT_ACTION_BAR="1"
            shift
            ;;
        --include-chat-clipboard-policy)
            INCLUDE_CHAT_CLIPBOARD_POLICY="1"
            shift
            ;;
        --include-chat-redaction-policy)
            INCLUDE_CHAT_REDACTION_POLICY="1"
            shift
            ;;
        --include-chat-attachment-policy)
            INCLUDE_CHAT_ATTACHMENT_POLICY="1"
            shift
            ;;
        --include-chat-shortcut-map)
            INCLUDE_CHAT_SHORTCUT_MAP="1"
            shift
            ;;
        --include-chat-status-summary)
            INCLUDE_CHAT_STATUS_SUMMARY="1"
            shift
            ;;
        --include-chat-review-packet)
            INCLUDE_CHAT_REVIEW_PACKET="1"
            shift
            ;;
        --include-chat-gap-matrix)
            INCLUDE_CHAT_GAP_MATRIX="1"
            shift
            ;;
        --include-chat-evidence-manifest)
            INCLUDE_CHAT_EVIDENCE_MANIFEST="1"
            shift
            ;;
        --backend)
            BACKEND="${2:-}"
            if [ -z "$BACKEND" ]; then
                ERROR "--backend requires an argument"
                exit 1
            fi
            shift 2
            ;;
        *)
            ERROR "unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -n "$BACKEND" ] && { [ "$INCLUDE_RUNTIME_READINESS" = "1" ] || [ "$INCLUDE_DEVICE_SESSION" = "1" ] || [ "$INCLUDE_CHAT_SESSION" = "1" ] || [ "$INCLUDE_CHAT_SURFACE_LAYOUT" = "1" ] || [ "$INCLUDE_CHAT_EMPTY_STATE" = "1" ] || [ "$INCLUDE_CHAT_LOCAL_ONLY_POLICY" = "1" ] || [ "$INCLUDE_CHAT_PREFERENCES" = "1" ] || [ "$INCLUDE_CHAT_SESSION_INDEX" = "1" ] || [ "$INCLUDE_CHAT_SESSION_STORE_POLICY" = "1" ] || [ "$INCLUDE_CHAT_SESSION_TITLE_POLICY" = "1" ] || [ "$INCLUDE_CHAT_MODEL_STATUS" = "1" ] || [ "$INCLUDE_CHAT_MODEL_SELECTION_POLICY" = "1" ] || [ "$INCLUDE_CHAT_CONTEXT_POLICY" = "1" ] || [ "$INCLUDE_CHAT_MODEL_LOAD_REQUEST" = "1" ] || [ "$INCLUDE_CHAT_READINESS" = "1" ] || [ "$INCLUDE_CHAT_COMPOSER" = "1" ] || [ "$INCLUDE_CHAT_SEND_RESULT" = "1" ] || [ "$INCLUDE_CHAT_TRANSCRIPT_POLICY" = "1" ] || [ "$INCLUDE_CHAT_AUDIT_EVENT" = "1" ] || [ "$INCLUDE_CHAT_ERROR_TAXONOMY" = "1" ] || [ "$INCLUDE_CHAT_RESPONSE_STREAM" = "1" ] || [ "$INCLUDE_CHAT_MESSAGE_LIST" = "1" ] || [ "$INCLUDE_CHAT_ACTION_BAR" = "1" ] || [ "$INCLUDE_CHAT_CLIPBOARD_POLICY" = "1" ] || [ "$INCLUDE_CHAT_REDACTION_POLICY" = "1" ] || [ "$INCLUDE_CHAT_ATTACHMENT_POLICY" = "1" ] || [ "$INCLUDE_CHAT_SHORTCUT_MAP" = "1" ] || [ "$INCLUDE_CHAT_STATUS_SUMMARY" = "1" ] || [ "$INCLUDE_CHAT_REVIEW_PACKET" = "1" ] || [ "$INCLUDE_CHAT_GAP_MATRIX" = "1" ] || [ "$INCLUDE_CHAT_EVIDENCE_MANIFEST" = "1" ]; }; then
    ERROR "--include-runtime-readiness, --include-device-session, --include-chat-session, --include-chat-surface-layout, --include-chat-empty-state, --include-chat-local-only-policy, --include-chat-preferences, --include-chat-session-index, --include-chat-session-store-policy, --include-chat-session-title-policy, --include-chat-model-status, --include-chat-model-selection-policy, --include-chat-context-policy, --include-chat-model-load-request, --include-chat-readiness, --include-chat-composer, --include-chat-send-result, --include-chat-transcript-policy, --include-chat-audit-event, --include-chat-error-taxonomy, --include-chat-response-stream, --include-chat-message-list, --include-chat-action-bar, --include-chat-clipboard-policy, --include-chat-redaction-policy, --include-chat-attachment-policy, --include-chat-shortcut-map, --include-chat-status-summary, --include-chat-review-packet, --include-chat-gap-matrix, and --include-chat-evidence-manifest are only supported in local scaffold mode"
    exit 1
fi

# ── Default mode ──────────────────────────────────────────────────────────────
if [ -z "$BACKEND" ]; then
    HEAD "launcher state"
    NOTE "chat-stub      : available (dry-run only; see scripts/chat-stub.sh)"
    NOTE "launch-stub    : available (dry-run only; --dry-run flag required)"
    NOTE "inference path : not active"
    NOTE "KV260 path     : gated on pccxai/pccx-FPGA-NPU-LLM-kv260 bring-up"
    NOTE "pccx-lab diag  : deferred (analyze handoff not yet wired into launcher)"
    NOTE "pccx-lab status: opt-in via --backend pccx-lab (host-dry-run scaffold)"
    NOTE "runtime ready  : opt-in via --include-runtime-readiness (read-only data)"
    NOTE "device/session: opt-in via --include-device-session (read-only panel data)"
    NOTE "chat/session  : opt-in via --include-chat-session (read-only blocked chat and lifecycle data)"
    NOTE "chat layout   : opt-in via --include-chat-surface-layout (read-only surface layout data)"
    NOTE "chat empty    : opt-in via --include-chat-empty-state (read-only empty-state data)"
    NOTE "chat local    : opt-in via --include-chat-local-only-policy (read-only local-only policy data)"
    NOTE "chat prefs    : opt-in via --include-chat-preferences (read-only preferences data)"
    NOTE "chat index    : opt-in via --include-chat-session-index (read-only empty session index data)"
    NOTE "chat store    : opt-in via --include-chat-session-store-policy (read-only session-store policy data)"
    NOTE "chat titles   : opt-in via --include-chat-session-title-policy (read-only title policy data)"
    NOTE "chat model    : opt-in via --include-chat-model-status (read-only model status display data)"
    NOTE "chat select   : opt-in via --include-chat-model-selection-policy (read-only model-selection data)"
    NOTE "chat context  : opt-in via --include-chat-context-policy (read-only context policy data)"
    NOTE "chat load     : opt-in via --include-chat-model-load-request (read-only model-load request data)"
    NOTE "chat readiness: opt-in via --include-chat-readiness (read-only readiness and recovery data)"
    NOTE "chat composer : opt-in via --include-chat-composer (read-only input control data)"
    NOTE "chat send     : opt-in via --include-chat-send-result (read-only blocked send-result data)"
    NOTE "chat transcript: opt-in via --include-chat-transcript-policy (read-only retention/export policy data)"
    NOTE "chat audit    : opt-in via --include-chat-audit-event (read-only blocked audit metadata)"
    NOTE "chat errors   : opt-in via --include-chat-error-taxonomy (read-only error taxonomy data)"
    NOTE "chat stream   : opt-in via --include-chat-response-stream (read-only response stream data)"
    NOTE "chat messages : opt-in via --include-chat-message-list (read-only empty message-list data)"
    NOTE "chat actions  : opt-in via --include-chat-action-bar (read-only disabled action-bar data)"
    NOTE "chat clipboard: opt-in via --include-chat-clipboard-policy (read-only disabled clipboard-policy data)"
    NOTE "chat redact   : opt-in via --include-chat-redaction-policy (read-only disabled redaction-policy data)"
    NOTE "chat attach   : opt-in via --include-chat-attachment-policy (read-only disabled attachment-policy data)"
    NOTE "chat shortcuts: opt-in via --include-chat-shortcut-map (read-only disabled shortcut-map data)"
    NOTE "chat summary  : opt-in via --include-chat-status-summary (read-only aggregate status data)"
    NOTE "chat review   : opt-in via --include-chat-review-packet (read-only review packet data)"
    NOTE "chat gaps     : opt-in via --include-chat-gap-matrix (read-only implementation gap data)"
    NOTE "chat evidence : opt-in via --include-chat-evidence-manifest (read-only evidence manifest data)"
    NOTE "editor bridge  : planned (VS Code / other IDEs)"

    if [ "$INCLUDE_CHAT_EVIDENCE_MANIFEST" = "1" ]; then
        if ! print_chat_evidence_manifest_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_GAP_MATRIX" = "1" ]; then
        if ! print_chat_gap_matrix_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_REVIEW_PACKET" = "1" ]; then
        if ! print_chat_review_packet_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_STATUS_SUMMARY" = "1" ]; then
        if ! print_chat_status_summary_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_ERROR_TAXONOMY" = "1" ]; then
        if ! print_chat_error_taxonomy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_RESPONSE_STREAM" = "1" ]; then
        if ! print_chat_response_stream_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_MESSAGE_LIST" = "1" ]; then
        if ! print_chat_message_list_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_ACTION_BAR" = "1" ]; then
        if ! print_chat_action_bar_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_CLIPBOARD_POLICY" = "1" ]; then
        if ! print_chat_clipboard_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_REDACTION_POLICY" = "1" ]; then
        if ! print_chat_redaction_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_ATTACHMENT_POLICY" = "1" ]; then
        if ! print_chat_attachment_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_SHORTCUT_MAP" = "1" ]; then
        if ! print_chat_shortcut_map_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_AUDIT_EVENT" = "1" ]; then
        if ! print_chat_audit_event_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_SURFACE_LAYOUT" = "1" ]; then
        if ! print_chat_surface_layout_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_EMPTY_STATE" = "1" ]; then
        if ! print_chat_empty_state_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_LOCAL_ONLY_POLICY" = "1" ]; then
        if ! print_chat_local_only_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_PREFERENCES" = "1" ]; then
        if ! print_chat_preferences_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_SESSION_INDEX" = "1" ]; then
        if ! print_chat_session_index_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_SESSION_STORE_POLICY" = "1" ]; then
        if ! print_chat_session_store_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_SESSION_TITLE_POLICY" = "1" ]; then
        if ! print_chat_session_title_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_TRANSCRIPT_POLICY" = "1" ]; then
        if ! print_chat_transcript_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_SEND_RESULT" = "1" ]; then
        if ! print_chat_send_result_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_COMPOSER" = "1" ]; then
        if ! print_chat_composer_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_MODEL_STATUS" = "1" ]; then
        if ! print_chat_model_status_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_MODEL_SELECTION_POLICY" = "1" ]; then
        if ! print_chat_model_selection_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_CONTEXT_POLICY" = "1" ]; then
        if ! print_chat_context_policy_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_MODEL_LOAD_REQUEST" = "1" ]; then
        if ! print_chat_model_load_request_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_SESSION" = "1" ]; then
        if ! print_chat_session_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_CHAT_READINESS" = "1" ]; then
        if ! print_chat_readiness_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_DEVICE_SESSION" = "1" ]; then
        if ! print_device_session_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_RUNTIME_READINESS" = "1" ]; then
        if ! print_runtime_readiness_summary; then
            exit 1
        fi
    fi

    HEAD "summary"
    INFO "no inference engine is wired up; all paths are planned or deferred"
    exit 0
fi

if [ "$BACKEND" != "pccx-lab" ]; then
    ERROR "unknown backend: $BACKEND (supported: pccx-lab)"
    exit 1
fi

# ── pccx-lab backend ─────────────────────────────────────────────────────────
# Resolution order: PCCX_LAB_BIN env var (if non-empty), then pccx-lab on PATH.
_PCCX_LAB_BIN="${PCCX_LAB_BIN:-}"
if [ -n "$_PCCX_LAB_BIN" ]; then
    if [ ! -x "$_PCCX_LAB_BIN" ]; then
        ERROR "PCCX_LAB_BIN=$_PCCX_LAB_BIN is not executable or does not exist."
        ERROR "No silent fallback: --backend pccx-lab was explicitly requested."
        exit 1
    fi
    LAB_BIN="$_PCCX_LAB_BIN"
elif command -v pccx-lab >/dev/null 2>&1; then
    LAB_BIN="$(command -v pccx-lab)"
else
    ERROR "pccx-lab binary not found."
    ERROR "Set PCCX_LAB_BIN=/path/to/pccx-lab or ensure pccx-lab is on PATH."
    ERROR "No silent fallback: --backend pccx-lab was explicitly requested."
    exit 1
fi

HEAD "pccx-lab status handoff"
INFO "backend   : pccx-lab"
INFO "binary    : $LAB_BIN"
INFO "boundary  : run-status envelope (host-dry-run / early scaffold)"
INFO "note      : no real KV260 device probing; no inference executed"

if ! OUTPUT="$("$LAB_BIN" status --format json 2>&1)"; then
    ERROR "pccx-lab exited with error"
    printf '%s\n' "$OUTPUT" >&2
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    ERROR "pccx-lab status produced no output"
    exit 1
fi

# Lightweight JSON shape check — output must begin with '{'.
STRIPPED="$(printf '%s' "$OUTPUT" | tr -d '[:space:]')"
FIRST_CHAR="${STRIPPED:0:1}"
if [ "$FIRST_CHAR" != "{" ]; then
    ERROR "pccx-lab output does not look like a JSON object (first char: '$FIRST_CHAR')"
    printf '%s\n' "$OUTPUT" >&2
    exit 1
fi

HEAD "run-status envelope"
printf '%s\n' "$OUTPUT"

HEAD "summary"
INFO "pccx-lab status handoff complete (host-dry-run; no KV260 probing; no inference)"
exit 0
