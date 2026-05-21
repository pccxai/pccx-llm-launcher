# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai

launcher_error() {
    if [ "$#" -lt 2 ]; then
        printf '[ERROR] TraceError(trace_error): launcher_error requires a type and message\n' >&2
        return 1
    fi

    local root_dir="${PCCX_LAUNCHER_ROOT:-}"
    if [ -z "$root_dir" ]; then
        printf '[ERROR] TraceError(trace_error): PCCX_LAUNCHER_ROOT is not set\n' >&2
        return 1
    fi

    local error_type="$1"
    shift
    python3 "$root_dir/pccx_launcher/errors.py" "$error_type" "$*" >&2
}

AXI_ERROR() { launcher_error AxiError "$*"; }
GEMMA_ERROR() { launcher_error GemmaError "$*"; }
KV260_ERROR() { launcher_error KV260Error "$*"; }
TRACE_ERROR() { launcher_error TraceError "$*"; }
