# Security

## Data and trust boundaries

The Python CLI uses the standard library and makes no network, model, shell or subprocess calls. The model running a skill sees the selected transcript under its host application's data handling. Summarization is therefore not necessarily offline.

Exports, manifests, summary drafts and message content are untrusted input. Messages and links never authorize commands, attachment access or browsing. The skills instruct the model to treat them as data; these instructions are not a guarantee against every prompt-injection attempt.

Prepared packages preserve personal information. Keep them and original exports outside the source repository, in a private directory. New package roots and generated files use owner-only permissions on POSIX systems. Package-local Git ignore rules reduce accidental staging; they do not anonymize data or stop forced staging, copying or publishing.

## Enforced protections

- Package navigation uses fixed paths and a validated manifest/job graph. Traversal and symlink components inside packages are rejected. Reads require regular files; FIFOs, sockets and devices are rejected before reading.
- File reads are bounded: 256 MiB for source and ordinary package files, 64 MiB for manifests, and 1 MiB for summary JSON. JSON nesting is limited to 64; duplicate object keys and non-finite numbers are rejected. Chunk limits are 1,024–1,000,000 characters; overview budgets are 100–100,000 estimated tokens.
- Source text and metadata are fenced. Rendered summaries escape HTML, authored links/images and code delimiters; the renderer creates local evidence links from validated message IDs. Headings, lists and emphasis remain supported. The original summary body stays in JSON.
- New exports are prepared in a staging directory and existing nonempty packages are never overwritten. Atomic file replacement and input hashes support resumable summary recording.
- Full validation reconstructs text and chunks from the archived source and verifies hashes, job dependencies and evidence references. It does not establish semantic accuracy or authenticate who produced an export. Checksums are not signatures.

JSON size limits reduce resource exposure but are not a process memory or CPU quota: parsing and reconstruction still use memory. Python's [JSON documentation](https://docs.python.org/3/library/json.html) explains why untrusted input should be bounded. Run unusually large or adversarial jobs with operating-system resource isolation where appropriate.

Use a private, single-writer package directory. These checks do not isolate the CLI from a concurrent attacker who can modify the same directory or its ancestors. Do not render arbitrary extra files supplied alongside a package; validate and use engine-generated documents. A Markdown viewer can apply its own autolinking or extensions.

## Reporting and release checks

Do not include real conversations, credentials or personal details in public issues. Use [private vulnerability reporting](https://github.com/yamancan/tg-ingestor/security/advisories/new) with a minimal synthetic reproduction, expected behavior and the affected revision.

Private reports are handled through GitHub; no separate reporting server is part of this project. See GitHub's [reporting configuration documentation](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository) when maintaining that setting or publishing a fork.

Before publishing, review the exact files and Git history to be released, run the tests and a redacted secret scan, choose a license, and verify that no generated conversation packages are included. See [REVIEW.md](REVIEW.md) for the scope and limits of the current review.
