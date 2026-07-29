#!/usr/bin/env python3
"""
Regenerates data_inventory_table.md from data.json.
Run this manually with `python generate_table.py`, or let the
GitHub Action run it automatically on every push that touches data.json.
"""
import json

SOURCE_JSON = "data.json"
OUTPUT_MD = "data_inventory_table.md"

HEADERS = [
    "ID", "Name", "Type", "Institution", "Category", "Detail Level",
    "Accessibility", "Update Frequency", "COVID-specific",
    "Belgium-specific", "Active", "Link",
]


def join_list(v, sep=", "):
    if isinstance(v, list):
        return sep.join(str(x) for x in v if x)
    return v or ""


def esc(s):
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def first_link(link_url):
    if isinstance(link_url, list):
        for l in link_url:
            if l:
                return l
        return ""
    return link_url or ""


def build_table(datasets):
    lines = ["# BE-PIN Data Inventory", ""]
    lines.append("| " + " | ".join(HEADERS) + " |")
    lines.append("|" + "|".join(["---"] * len(HEADERS)) + "|")

    for d in datasets:
        link = first_link(d.get("linkURL"))
        link_md = f"[link]({link})" if link else ""
        row = [
            str(d.get("id", "")),
            esc(d.get("name", "")),
            esc(d.get("type", "")),
            esc(join_list(d.get("institution"))),
            esc(d.get("category", "")),
            esc(d.get("detailLevel", "")),
            esc(d.get("accessibility", "")),
            esc(d.get("updateFrequency", "")),
            "Yes" if d.get("isCovid") == 1 else "No",
            "Yes" if d.get("isBelgium") == 1 else "No",
            "Yes" if d.get("isActive") == 1 else "No",
            link_md,
        ]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines) + "\n"


def main():
    with open(SOURCE_JSON, encoding="utf-8") as f:
        data = json.load(f)

    table_md = build_table(data["datasets"])

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(table_md)

    print(f"Wrote {OUTPUT_MD} ({len(data['datasets'])} rows)")


if __name__ == "__main__":
    main()
