"""Verify publication exclusions with synthetic paths, without private files."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(shutil.which("git"), "Git is required to check publication rules")
class PublicationIgnoreTests(unittest.TestCase):
    def test_only_expected_source_paths_can_be_staged(self):
        allowed = (
            ".gitignore", "README.md", "SECURITY.md", "REVIEW.md", "LICENSE",
            "skills/telegram-context/SKILL.md",
            "skills/tg-cleanup/agents/openai.yaml",
            "skills/telegram-context/scripts/telegram_context.py",
            "skills/telegram-context/references/workflow.md",
            "tests/test_telegram_context.py", "tests/test_gitignore.py",
            "tests/fixtures/conversation.json", ".github/workflows/tests.yml",
        )
        private = (
            "export.json", "notes.md", "report.txt", "backup.zip", "photo.jpg",
            "source/export.json", "result.json", "messages.html", "messages2.html",
            "ChatExport_2026-01-05/result.json", "data/chat.json", "output/context.md",
            "exports/conversation.json", "packages/demo/manifest.json",
            "tests/fixtures/private-chat.json", "tests/fixtures/messages.jsonl",
            "tests/smoke-report.md", "skills/tg-cleanup/result.json",
            "skills/tg-cleanup/summaries/private.md",
            "skills/tg-cleanup/drafts/next.json", "skills/tg-cleanup/chunks/c000001.md",
            "skills/tg-cleanup/references/exports/chat.md",
            "skills/tg-cleanup/references/.env.md",
            "skills/tg-cleanup/scripts/__pycache__/engine.pyc",
            ".agents/skills/private/SKILL.md", ".codex/settings.json",
            ".env", ".env.production", "key.pem", "account.session", ".DS_Store",
        )
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copyfile(repo / ".gitignore", root / ".gitignore")
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
            result = subprocess.run(
                ["git", "-c", "core.excludesFile=/dev/null", "-C", str(root),
                 "check-ignore", "--no-index", "--stdin"],
                input="\n".join(allowed + private) + "\n", text=True,
                capture_output=True, check=True,
            )
            ignored = set(result.stdout.splitlines())
            self.assertEqual(ignored, set(private))


if __name__ == "__main__":
    unittest.main()
