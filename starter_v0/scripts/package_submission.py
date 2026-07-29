"""Zip starter_v0/ for submission without shipping secrets or build output.

README nói "Submit starter_v0/" nhưng cũng cấm nộp `.env`, API key, `.venv/`,
cache/build output. Zip cả thư mục bằng tay là ship luôn 4 API key thật trong
`.env`. Script này loại chúng ra và fail nếu vẫn còn key lọt vào archive.

    python scripts/package_submission.py --output ../DAY04_G29_E403_submission.zip
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {".venv", "__pycache__", ".git", ".pytest_cache", "arxiv_papers", ".ipynb_checkpoints"}
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}

# `.env.example` chỉ có tên biến nên vẫn được nộp; mọi `.env*` khác thì không.
def is_secret_file(relative: Path) -> bool:
    return relative.name.startswith(".env") and relative.name != ".env.example"


# Khớp shape của key thật, không khớp placeholder trong `.env.example`.
# Giới hạn đã biết: `RAPIDAPI_KEY` là chuỗi hex trần không có prefix, không thể
# bắt bằng regex mà không đụng nhầm `prompt_hash`/`tools_hash` (cũng là hex 64 ký
# tự) trong mọi run JSON — nên nó không nằm trong danh sách này.
SECRET_PATTERNS = (
    re.compile(r"sk-or-v1-[A-Za-z0-9]{16,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]{16,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}"),
    re.compile(r"tvly-[A-Za-z0-9_-]{16,}"),
    re.compile(r"fc-[a-f0-9]{24,}"),
    re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{30,}\b"),  # Telegram bot token
)

SCANNED_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".csv", ".txt", ".toml", ".cfg", ".example"}


def should_include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if relative.name in EXCLUDED_NAMES or relative.suffix in EXCLUDED_SUFFIXES:
        return False
    return not is_secret_file(relative)


def scan_for_secrets(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        if path.suffix.lower() not in SCANNED_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                relative = path.relative_to(ROOT)
                findings.append(f"{relative}: {match.group(0)[:12]}...")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT.parent / "DAY04_G29_E403_submission.zip",
        help="Đường dẫn file zip sẽ tạo.",
    )
    parser.add_argument(
        "--allow-secrets",
        action="store_true",
        help="Bỏ qua bước chặn khi quét thấy key (không nên dùng).",
    )
    args = parser.parse_args()

    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and should_include(path))
    if not files:
        print("Không tìm thấy file nào để đóng gói.")
        return 1

    findings = scan_for_secrets(files)
    if findings and not args.allow_secrets:
        print(f"DỪNG: quét thấy {len(findings)} chuỗi giống API key trong các file sắp nộp:")
        for finding in findings[:20]:
            print(f"  - {finding}")
        print("Xoá/khử chúng rồi chạy lại. Chỉ dùng --allow-secrets nếu chắc chắn đó là false positive.")
        return 2

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path(ROOT.name) / path.relative_to(ROOT))

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"Đã đóng gói {len(files)} file -> {output} ({size_mb:.2f} MB)")
    print("Đã loại: .venv/, __pycache__/, .env (giữ .env.example), *.pyc")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
