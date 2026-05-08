# Security Policy

## Supported Versions

Security fixes are handled on the default branch until this project starts
publishing supported releases. Older planning snapshots and feature branches are
not supported unless maintainers state otherwise in a release note.

This launcher is currently a planning and preview scaffold. It does not provide
a verified KV260 inference path, a production runtime, or a stable unattended
deployment target yet.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately. Use GitHub private
vulnerability reporting for this repository when it is available. If that option
is unavailable, contact a repository maintainer through a private channel before
posting technical details publicly.

Do not open a public issue, discussion, pull request, or social post with
exploit details before maintainers have had a chance to review the report.

Include the following when possible:

- Affected branch, commit, script, or component.
- Steps to reproduce the issue.
- Expected and actual behavior.
- Impact, including whether secrets, prompts, transcripts, device state,
  runtime logs, model files, or host files may be exposed or modified.
- Any relevant environment details, such as operating system, target device,
  shell, and command arguments.

Please avoid sending real secrets, private prompts, proprietary model weights,
or sensitive hardware logs. Redact sensitive values and use minimal reproducer
data where practical.

## Scope

Reports that are in scope include vulnerabilities in launcher scripts,
configuration handling, local-device connection flows, log handling, transcript
or prompt handling, dependency setup instructions, and future runtime handoff
boundaries maintained in this repository.

Reports about the FPGA implementation, RTL, kernel bring-up, or verification
artifacts should be filed with the relevant PCCX repository unless the issue is
caused by this launcher repository.

## Response Expectations

Maintainers will acknowledge valid private reports when available, investigate
the impact, and coordinate a fix before public disclosure when practical. Public
disclosure timing depends on severity, exploitability, and whether the issue
affects unreleased scaffold code or a supported release.

This project does not currently run a paid bug bounty program.
