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
# Chat session index/sidebar plan (explicit opt-in, read-only local data):
#   --include-chat-session-index
#
# Chat model status display plan (explicit opt-in, read-only local data):
#   --include-chat-model-status
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
INCLUDE_CHAT_SESSION_INDEX="0"
INCLUDE_CHAT_MODEL_STATUS="0"
INCLUDE_CHAT_READINESS="0"
INCLUDE_CHAT_COMPOSER="0"
INCLUDE_CHAT_SEND_RESULT="0"
INCLUDE_CHAT_TRANSCRIPT_POLICY="0"
INCLUDE_CHAT_AUDIT_EVENT="0"

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
        --include-chat-session-index)
            INCLUDE_CHAT_SESSION_INDEX="1"
            shift
            ;;
        --include-chat-model-status)
            INCLUDE_CHAT_MODEL_STATUS="1"
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

if [ -n "$BACKEND" ] && { [ "$INCLUDE_RUNTIME_READINESS" = "1" ] || [ "$INCLUDE_DEVICE_SESSION" = "1" ] || [ "$INCLUDE_CHAT_SESSION" = "1" ] || [ "$INCLUDE_CHAT_SURFACE_LAYOUT" = "1" ] || [ "$INCLUDE_CHAT_SESSION_INDEX" = "1" ] || [ "$INCLUDE_CHAT_MODEL_STATUS" = "1" ] || [ "$INCLUDE_CHAT_READINESS" = "1" ] || [ "$INCLUDE_CHAT_COMPOSER" = "1" ] || [ "$INCLUDE_CHAT_SEND_RESULT" = "1" ] || [ "$INCLUDE_CHAT_TRANSCRIPT_POLICY" = "1" ] || [ "$INCLUDE_CHAT_AUDIT_EVENT" = "1" ]; }; then
    ERROR "--include-runtime-readiness, --include-device-session, --include-chat-session, --include-chat-surface-layout, --include-chat-session-index, --include-chat-model-status, --include-chat-readiness, --include-chat-composer, --include-chat-send-result, --include-chat-transcript-policy, and --include-chat-audit-event are only supported in local scaffold mode"
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
    NOTE "chat index    : opt-in via --include-chat-session-index (read-only empty session index data)"
    NOTE "chat model    : opt-in via --include-chat-model-status (read-only model status display data)"
    NOTE "chat readiness: opt-in via --include-chat-readiness (read-only readiness and recovery data)"
    NOTE "chat composer : opt-in via --include-chat-composer (read-only input control data)"
    NOTE "chat send     : opt-in via --include-chat-send-result (read-only blocked send-result data)"
    NOTE "chat transcript: opt-in via --include-chat-transcript-policy (read-only retention/export policy data)"
    NOTE "chat audit    : opt-in via --include-chat-audit-event (read-only blocked audit metadata)"
    NOTE "editor bridge  : planned (VS Code / other IDEs)"

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

    if [ "$INCLUDE_CHAT_SESSION_INDEX" = "1" ]; then
        if ! print_chat_session_index_summary; then
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
