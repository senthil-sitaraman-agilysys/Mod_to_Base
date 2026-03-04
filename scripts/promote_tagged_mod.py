import argparse
import json
import re
from pathlib import Path


MOD_TAG_RE = re.compile(r"\bM\d{2}-[ad]\b", re.IGNORECASE)


def _split_line_ending(line: str):
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def _comment_fixed_col7(line: str):
    content, ending = _split_line_ending(line)
    if len(content) < 7:
        content = content.ljust(7)
    if content[6] == "*":
        return line
    return f"{content[:6]}*{content[7:]}{ending}"


def _comment_free_slash(line: str):
    content, ending = _split_line_ending(line)
    stripped = content.lstrip(" ")
    if stripped.startswith("//"):
        return line
    indent_len = len(content) - len(stripped)
    return f"{' ' * indent_len}// {stripped}{ending}"


def _comment_cl_block(line: str):
    content, ending = _split_line_ending(line)
    stripped = content.lstrip(" ")
    if stripped.startswith("/*") and stripped.endswith("*/"):
        return line
    indent_len = len(content) - len(stripped)
    return f"{' ' * indent_len}/* {stripped} */{ending}"


def _comment_for_source_type(src: Path, line: str):
    suffix = src.suffix.lower()

    if suffix in {".rpg", ".sqlrpg"}:
        return _comment_fixed_col7(line)

    if suffix in {".rpgle", ".sqlrpgle", ".sqlrpgle"}:
        return _comment_free_slash(line)

    if suffix in {".cl", ".clle"}:
        return _comment_cl_block(line)

    if suffix in {".dspf", ".pf", ".lf", ".prtf", ".dds"}:
        return _comment_fixed_col7(line)

    return _comment_free_slash(line)


def process_file(src: Path, selected_mod: str, new_version: str):
    selected_add = f"{selected_mod}-a"
    selected_del = f"{selected_mod}-d"

    text = src.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines(keepends=True)

    out_lines = []
    selected_count = 0
    has_selected = False

    for line in lines:
        tags_in_line = [m.group(0).upper() for m in MOD_TAG_RE.finditer(line)]

        if not tags_in_line:
            out_lines.append(line)
            continue

        matched_selected = False
        for tag in tags_in_line:
            if tag == selected_add.upper() or tag == selected_del.upper():
                matched_selected = True
                break

        if not matched_selected:
            continue

        has_selected = True
        selected_count += 1

        promoted_line = re.sub(re.escape(selected_add), f"{new_version}-a", line, flags=re.IGNORECASE)
        promoted_line = re.sub(re.escape(selected_del), f"{new_version}-d", promoted_line, flags=re.IGNORECASE)

        if re.search(re.escape(selected_del), line, flags=re.IGNORECASE):
            promoted_line = _comment_for_source_type(src, promoted_line)

        out_lines.append(promoted_line)

    return has_selected, selected_count, "".join(out_lines)


def main():
    parser = argparse.ArgumentParser(description="Promote only one tagged mod and retag lines to new version.")
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--target-dir", required=True)
    parser.add_argument("--selected-mod", required=True)
    parser.add_argument("--new-version", required=True)
    parser.add_argument("--mode", choices=["dry-run", "promote"], required=True)
    parser.add_argument("--summary-file", required=True)
    args = parser.parse_args()

    selected_mod = args.selected_mod.upper()
    if not re.fullmatch(r"M\d{2}", selected_mod):
        raise SystemExit("selected_mod must match MNN format, for example M02")

    source_dir = Path(args.source_dir)
    target_dir = Path(args.target_dir)

    if not source_dir.is_dir():
        raise SystemExit(f"Source directory not found: {source_dir}")
    if not target_dir.is_dir():
        raise SystemExit(f"Target directory not found: {target_dir}")

    processed = []
    total_lines = 0

    for src in sorted(source_dir.rglob("*")):
        if not src.is_file():
            continue
        if src.name == "README.md":
            continue

        has_selected, selected_count, output_text = process_file(src, selected_mod, args.new_version)
        if not has_selected:
            continue

        rel = src.relative_to(source_dir)
        processed.append(str(rel).replace("\\", "/"))
        total_lines += selected_count

        if args.mode == "promote":
            dest = target_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(output_text, encoding="utf-8", newline="")

    summary = {
        "selected_mod": selected_mod,
        "new_version": args.new_version,
        "mode": args.mode,
        "files_count": len(processed),
        "tagged_lines_count": total_lines,
        "files": processed,
    }

    Path(args.summary_file).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if not processed:
        raise SystemExit("No files found containing selected mod tag.")


if __name__ == "__main__":
    main()
