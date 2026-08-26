"""Build the public resume PDF from the master .docx.

    python scripts/build_resume_pdf.py

Takes ~/OneDrive/Career/Greg Chedwick - Resume.docx, replaces the contact line
with a redacted one, and converts the result to public/resume.pdf via Word.

The master is never modified — everything happens on a copy in a temp directory.
The full-detail document stays as it is for direct applications, where a named
recruiter has a reason to have a street address and a phone number. This file is
downloadable by anyone, indexed by search engines and scraped by data brokers,
so it carries city and email only, matching what the site itself shows.

Requires Microsoft Word (uses COM automation for a faithful conversion).
Re-run after any edit to the master.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]
MASTER = Path.home() / "OneDrive" / "Career" / "Greg Chedwick - Resume.docx"
OUT = SITE_ROOT / "public" / "resume.pdf"

# Matches the whole contact line regardless of the exact street address, so an
# edit to the master cannot quietly reintroduce it.
CONTACT_RE = re.compile(
    r"[^<>]*\|\s*Reno,\s*NV\s*\d{5}\s*\|[^<>]*\|\s*(?P<email>[\w.+-]+@[\w.-]+)[^<>]*"
)
# The portfolio links survive redaction deliberately: they are public, they are
# the point of the site, and a recruiter looks for them at the top of page one.
# Only the street address and phone are removed.
REDACTED = (
    "Reno, NV | {email} | gregchedwick.dev"
    " | linkedin.com/in/gregchedwick | github.com/gregchedwick"
)


def redact(docx_in: Path, docx_out: Path) -> str:
    """Copy the document, rewriting the contact line. Returns the new line."""
    replacement: str | None = None

    with zipfile.ZipFile(docx_in) as src, zipfile.ZipFile(docx_out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/document.xml":
                xml = data.decode("utf8")

                def swap(match: re.Match) -> str:
                    nonlocal replacement
                    replacement = REDACTED.format(email=match.group("email"))
                    return replacement

                xml, count = CONTACT_RE.subn(swap, xml, count=1)
                if count == 0:
                    raise SystemExit(
                        "Contact line not found — the master's format changed.\n"
                        "Check CONTACT_RE before publishing, or the address may ship."
                    )
                data = xml.encode("utf8")
            dst.writestr(item, data)

    assert replacement
    return replacement


def assert_clean(docx: Path) -> None:
    """Refuse to publish if anything private survived the rewrite.

    Checked on the .docx rather than the PDF: this is the exact input Word
    renders, and its text is plainly readable, whereas pulling text back out of
    a PDF is lossy enough to give false reassurance.
    """
    xml = zipfile.ZipFile(docx).read("word/document.xml").decode("utf8")
    text = re.sub(r"<[^>]+>", "", xml)

    leaks = [
        pattern
        for pattern in (r"\d{3,5}\s+\w+\s+(Way|St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Ln|Lane)",
                        r"\(\d{3}\)\s*\d{3}-\d{4}",
                        r"\b\d{3}-\d{3}-\d{4}\b",
                        r"\bNV\s*\d{5}\b")
        if re.search(pattern, text, re.I)
    ]
    if leaks:
        raise SystemExit(
            "Refusing to publish — private details still present in the document.\n"
            + "\n".join(f"  matched: {p}" for p in leaks)
        )


def to_pdf(docx: Path, pdf: Path) -> None:
    """Convert via Word. 17 is wdFormatPDF."""
    script = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open('{docx}', $false, $true)
$doc.SaveAs2('{pdf}', 17)
$doc.Close($false)
$word.Quit()
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True,
        text=True,
    )
    if not pdf.exists():
        raise SystemExit(f"Word conversion failed:\n{result.stdout}\n{result.stderr}")


def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"Master resume not found at {MASTER}")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        # Copy first: Word holds a lock on the master while it is open.
        original = work / "master.docx"
        shutil.copy2(MASTER, original)

        redacted_docx = work / "redacted.docx"
        line = redact(original, redacted_docx)
        assert_clean(redacted_docx)

        built = work / "resume.pdf"
        to_pdf(redacted_docx, built)

        OUT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built, OUT)

    print(f"Contact line is now: {line}")
    print(f"Wrote {OUT.relative_to(SITE_ROOT)} — {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
