# Telegram Context

Turn Telegram Desktop JSON exports into text context that an AI can read in bounded pieces, then create source-linked summaries at the level of detail you need.

This repository contains a local Python CLI and three Codex skills. The CLI prepares and validates files; the model running the skill writes summaries. Each conversation gets its own package. No Telegram bot, Telegram login, server, or separate model API key is required by this project.

`Telegram JSON → text chunks → chunk summaries → period summaries → overview`

## Start with the repository URL

Give [this repository](https://github.com/yamancan/tg-ingestor) to Codex with this prompt:

```text
Read https://github.com/yamancan/tg-ingestor and its README. Install the three skills from
skills/telegram-context, skills/tg-cleanup, and skills/tg-summarize
into my personal skill directory. Keep them as sibling folders because
they share one Python engine. Preserve any existing installations.
Run the synthetic cleanup example to verify the setup.
```

You can also use Codex's `$skill-installer` to install those three paths from the repository. Keep all three together. This installs local skills, not a hosted service: Codex needs access to Python and your files. See the [official OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills) for local installation and discovery.

## Install manually

You need Python 3.10+, Git to clone the repository, and IANA timezone data. There are no third-party Python package dependencies on systems with timezone data. Codex is needed only for the skill-driven summarization workflow; cleanup works without an AI application.

These terminal commands are for macOS, Linux, or Windows WSL:

```sh
git clone https://github.com/yamancan/tg-ingestor.git
cd tg-ingestor
python3 --version
```

A downloaded ZIP also works: extract it and open a terminal in the directory containing this README.

Run this from the repository root to make the three skills available across your local Codex projects:

```sh
python3 -B - <<'PY'
from pathlib import Path

source = Path("skills").resolve()
target = Path.home() / ".agents" / "skills"
names = ("telegram-context", "tg-cleanup", "tg-summarize")
for name in names:
    if not (source / name / "SKILL.md").is_file():
        raise SystemExit("Run this command from the repository root.")
    destination = target / name
    if (destination.exists() or destination.is_symlink()) and destination.resolve() != source / name:
        raise SystemExit(f"Existing installation preserved: {destination}")
target.mkdir(parents=True, exist_ok=True)
for name in names:
    destination = target / name
    if not destination.is_symlink():
        destination.symlink_to(source / name, target_is_directory=True)
    print(f"Ready: {name}")
PY
```

This links to the checkout and refuses to replace another installation. Keep the checkout at this location. After `git pull --ff-only`, linked skills use the updated files. If you prefer copies, copy all three complete folders into `~/.agents/skills` and update them together.

Codex supports this personal skill location and symlinked folders. Changes are normally detected automatically; restart Codex if a skill does not appear. In Codex CLI or the IDE extension, use `/skills` to select a skill or type `$tg-cleanup`, `$tg-summarize`, or `$telegram-context` in your prompt. [Official documentation](https://learn.chatgpt.com/docs/build-skills)

## Try the included example

No private export or model access is needed. From the repository root:

```sh
tg_demo="$(mktemp -d)"
python3 -B skills/telegram-context/scripts/telegram_context.py prepare \
  tests/fixtures/conversation.json --out "$tg_demo/package" --language English
python3 -B skills/telegram-context/scripts/telegram_context.py validate \
  "$tg_demo/package" --prepared-only
python3 -B skills/telegram-context/scripts/telegram_context.py status \
  "$tg_demo/package" --json
```

`prepare` prints the package path and counts. Open its `INDEX.md` to find text chunks. Prepared-only validation should return `"valid": true`. The synthetic fixture intentionally includes a missing reply target, reported as a warning. Summary jobs remain pending until a model writes them.

## Use the skills

Supply `result.json` from a Telegram Desktop export saved in JSON format. HTML exports and ZIP archives are not accepted directly. For an account-wide export, select one conversation by ID or unique name; unrelated chats are excluded from its package.

| Skill | Behavior |
| --- | --- |
| `$tg-cleanup` | Extract and normalize text, split by period and size, and validate preservation. No summaries or anonymization. |
| `$tg-summarize` | Create source-linked summaries from a raw JSON export or resume an existing package. |
| `$telegram-context` | Run preparation and summarization together. |

Cleanup only:

```text
$tg-cleanup Prepare ~/Downloads/TelegramExport/result.json.
Use weekly chunks of at most 24,000 characters and save to
~/.local/share/telegram-context/packages/my-chat. Use English for later summaries.
```

Summarize the prepared package:

```text
$tg-summarize Summarize ~/.local/share/telegram-context/packages/my-chat.
Follow its saved settings and include decisions, commitments, open questions,
and changes over time. Complete every summary job and validate the result.
```

Run the whole workflow with a chosen overview budget:

```text
$telegram-context Process ~/Downloads/TelegramExport/result.json into a new
package. Use weekly chunks, English summaries, and an overview budget of
about 1,000 tokens. Focus on decisions and unresolved questions.
```

Resume in another session:

```text
$tg-summarize Resume ~/.local/share/telegram-context/packages/my-chat
from its next pending job. Keep completed summaries and finish validation.
```

Each new export needs a new or empty output directory. Resume an existing package without preparing it again. Language, focus, period, and overview budget are saved during preparation; choose a new package to use different settings.

## What cleanup changes

The readable text excludes duplicated export representation such as plain `text_entities`, reaction details, media file properties, and records containing no text. It preserves message spelling, whitespace, emoji, code, link targets, author information, and reply relationships. Captions count as text; photos, audio, and attachments are not analyzed.

Dates appear once per day section, repeated when a new chunk starts. Message times use `HH:MM`, without seconds. Exact timestamps remain in the source archive and canonical records; message order is unchanged.

A simplified reading view of four **synthetic** messages, with source anchors and metadata omitted here:

```text
2026-01-05
09:10 Ada: Can we share the preview?
09:10 Bora: After the copy review.
09:12 Bora: Copy review is complete.
09:12 Ada: I will send it this afternoon.
```

The actual chunk files contain fenced text, source IDs, and metadata for verifiable citations. Cleanup keeps all four messages. A summary can compress them to: “The preview was waiting for copy review. After the review, Ada committed to sending it that afternoon.” It must not claim the preview was already sent.

Cleanup does not remove greetings, short replies, or repeated messages based on meaning. Selective compression belongs to the summary layer. Packages are not anonymized.

## Use the CLI directly

Run from the repository root:

```sh
python3 -B skills/telegram-context/scripts/telegram_context.py prepare \
  "$HOME/Downloads/TelegramExport/result.json" \
  --out "$HOME/.local/share/telegram-context/packages/my-chat" \
  --period week --timezone Europe/Istanbul --language English \
  --max-chars 24000 --overview-tokens 2000 \
  --focus "Decisions and unresolved questions"

python3 -B skills/telegram-context/scripts/telegram_context.py validate \
  "$HOME/.local/share/telegram-context/packages/my-chat" --prepared-only

python3 -B skills/telegram-context/scripts/telegram_context.py status \
  "$HOME/.local/share/telegram-context/packages/my-chat" --json
```

| Option | Default / accepted values |
| --- | --- |
| `--out` | Required; a new or empty directory |
| `--chat` | Chat ID or exact unique name, when selection is needed |
| `--period` | `week`; also `day` or `month`. Weeks start Monday. |
| `--timezone` | `Europe/Istanbul`; an installed IANA timezone |
| `--max-chars` | `24000`; 1,024–1,000,000 rendered characters per chunk |
| `--overview-tokens` | `2000`; 100–100,000 estimated tokens |
| `--language` | `Turkish`; set `English` or your desired summary language |
| `--focus` | Empty; optional summary priorities |

The CLI never calls a model. For automation or another AI host, follow [the summary workflow and exact draft schema](skills/telegram-context/references/workflow.md): read `status` and every `next_job.input_paths` file, write a draft, and submit it with `record-summary`. Repeat until no jobs remain:

```sh
python3 -B skills/telegram-context/scripts/telegram_context.py record-summary \
  "$HOME/.local/share/telegram-context/packages/my-chat" \
  --input "$HOME/.local/share/telegram-context/packages/my-chat/drafts/next.json"

python3 -B skills/telegram-context/scripts/telegram_context.py validate \
  "$HOME/.local/share/telegram-context/packages/my-chat"
```

The model must write the draft before `record-summary` runs. Correct a recorded summary with `--replace`; dependent summaries become stale and must be regenerated. `status` reports progress; `validate` checks integrity and completion.

## Read the results

| Package file | Purpose |
| --- | --- |
| `context.md` | Standalone overview, explicitly incomplete until all work finishes |
| `INDEX.md` | Navigation to summaries and source chunks |
| `chunks/*.md` | Message text with day headings, minute-only times, and source anchors |
| `summaries/*.md` | Chunk, reduction, period, and overview summaries |
| `summaries/*.txt` | Plain summary text with bare `[[m:id]]` markers, read by parent summaries (version 4) |
| `summaries/*.json` | Recorded model outputs and input fingerprints |
| `messages.jsonl` | Canonical text and metadata with exact timestamps |
| `manifest.json`, `report.json` | Settings, coverage, checksums, and source issues |
| `source/export.json` | Private source archive |

A single-chat input is archived byte for byte. An account-wide input contributes only the complete selected chat object. The original input file is never changed.

Give another AI `context.md` for an overview, plus relevant summary/chunk files when it needs evidence. Local links alone do not provide file access. Review files before sharing: they retain personal information present in the conversation.

## Troubleshooting

- **Skill not found:** install all three folders together, then restart Codex. Avoid duplicate installations in multiple skill directories.
- **Output already exists:** choose a new directory or use `$tg-summarize` to resume that package.
- **Unsupported input:** supply an extracted Telegram Desktop JSON file and select one chat if needed.
- **Unknown timezone:** ensure IANA timezone data is installed. If system data is unavailable, install `tzdata` in your Python environment with `python3 -m pip install tzdata`.
- **Warnings:** inspect `report.json` for missing senders or reply targets. Unsupported records are not silently treated as processed.
- **Exit codes:** `0` means command success; `2` means invalid input, failed/incomplete validation, or unprocessed records. `status` succeeds with pending jobs. `prepare` can leave a partial package when it reports unsupported records.

File limits are 256 MiB for source/ordinary files, 64 MiB for manifests, and 1 MiB for summary JSON. JSON nesting is limited to 64. Parsing and full validation use memory. Token estimates use characters divided by three, not a model tokenizer.

New packages use version 4: the same information as version 3 in a compact chunk layout, with parent summaries reading plain text instead of linked Markdown. Versions 2 and 3 remain valid and resumable with their original rendering. For the compact layout, prepare the source into a new directory. Version 1 requires fresh preparation. Existing packages are never automatically migrated or overwritten.

## Development and privacy

Run the synthetic test suite:

```sh
python3 -B -m unittest discover -s tests -v
```

Tests cover text preservation, Unicode, size limits, minute display with exact ordering, summary dependencies, resume/correction behavior, integrity, and malicious file/Markdown inputs. Mechanical validation cannot prove summary accuracy.

Keep real exports and generated packages outside this repository. Skills default to `~/.local/share/telegram-context/packages/`. Each package includes a Git ignore rule, which does not anonymize files or prevent forced staging. Only synthetic examples belong in `tests/fixtures/`.

The repository's `.gitignore` excludes files by default and allows specific source, documentation, test, and workflow paths. New public file types or fixtures must be explicitly allowed and reviewed. This prevents ordinary accidental staging of exports, reports, archives, and local configuration; it does not protect against overwriting an allowed file with private content or using `git add --force`.

The CLI makes no network calls. Summarization uses the host AI application's model and data handling. See [SECURITY.md](SECURITY.md) for trust boundaries and [REVIEW.md](REVIEW.md) for findings. The source is publicly viewable; an open-source license has not yet been selected.
