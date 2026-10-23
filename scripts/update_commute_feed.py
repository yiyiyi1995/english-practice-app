#!/usr/bin/env python3
"""Build the static commute feed used by the GitHub Pages app."""

from __future__ import annotations

import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "commute.json"

SOURCES = [
    {"source": "BBC Global News", "kind": "news", "type": "podcast", "url": "https://podcasts.files.bbci.co.uk/p02nq0gn.rss", "limit": 8},
    {"source": "BBC 6 Minute English", "kind": "learning", "type": "podcast", "url": "https://podcasts.files.bbci.co.uk/p02pc9tn.rss", "limit": 8},
    {"source": "Practical AI", "kind": "ai", "type": "podcast", "url": "https://changelog.com/practicalai/feed", "limit": 8},
    {"source": "BBC World", "kind": "news", "type": "article", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "limit": 8},
    {"source": "MIT Technology Review", "kind": "ai", "type": "article", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "limit": 8},
    {"source": "OpenAI News", "kind": "ai", "type": "article", "url": "https://openai.com/news/rss.xml", "limit": 6},
]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def children(node: ET.Element, name: str):
    return [child for child in node if local_name(child.tag) == name]


def text(node: ET.Element, *names: str) -> str:
    wanted = {name.lower() for name in names}
    for child in node.iter():
        if local_name(child.tag) in wanted and child.text:
            return child.text.strip()
    return ""


def clean(value: str, limit: int = 240) -> str:
    value = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def iso_date(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return ""
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def duration_minutes(value: str) -> int:
    if not value:
        return 0
    try:
        parts = [int(float(part)) for part in value.strip().split(":")]
        seconds = parts[0] if len(parts) == 1 else parts[-1] + parts[-2] * 60 + (parts[-3] * 3600 if len(parts) > 2 else 0)
        return max(1, round(seconds / 60))
    except ValueError:
        return 0


def entry_link(node: ET.Element) -> str:
    for child in node.iter():
        if local_name(child.tag) == "link":
            href = child.attrib.get("href", "")
            if href and child.attrib.get("rel", "alternate") in ("alternate", ""):
                return href
            if child.text and child.text.strip().startswith("http"):
                return child.text.strip()
    return ""


def enclosure(node: ET.Element) -> str:
    for child in node.iter():
        if local_name(child.tag) == "enclosure" and child.attrib.get("url"):
            return child.attrib["url"]
        if local_name(child.tag) == "link" and child.attrib.get("rel") == "enclosure":
            return child.attrib.get("href", "")
    return ""


def fetch(source: dict) -> list[dict]:
    request = urllib.request.Request(source["url"], headers={"User-Agent": "Fluent120-feed-updater/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    nodes = [node for node in root.iter() if local_name(node.tag) in ("item", "entry")]
    result = []
    for node in nodes[: source["limit"]]:
        audio = enclosure(node) if source["type"] == "podcast" else ""
        if source["type"] == "podcast" and not audio:
            continue
        result.append(
            {
                "source": source["source"],
                "kind": source["kind"],
                "title": clean(text(node, "title"), 160),
                "summary": clean(text(node, "description", "summary", "content")),
                "link": entry_link(node),
                "audio": audio,
                "duration": duration_minutes(text(node, "duration")),
                "published": iso_date(text(node, "pubdate", "published", "updated", "date")),
            }
        )
    return [item for item in result if item["title"] and item["link"]]


def main() -> None:
    previous = {source["source"]: [] for source in SOURCES}
    previous_payload = None
    if OUTPUT.exists():
        try:
            previous_payload = json.loads(OUTPUT.read_text())
            for item in previous_payload["items"]:
                previous.setdefault(item.get("source", ""), []).append(item)
        except (KeyError, json.JSONDecodeError):
            pass

    items = []
    errors = []
    for source in SOURCES:
        try:
            items.extend(fetch(source))
        except Exception as exc:  # Keep the last successful snapshot per source.
            errors.append(f"{source['source']}: {exc}")
            items.extend(previous.get(source["source"], []))

    items.sort(key=lambda item: item.get("published", ""), reverse=True)
    if previous_payload and items == previous_payload.get("items"):
        print(f"No feed changes; kept {OUTPUT}")
        return
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "items": items,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {len(items)} items to {OUTPUT}")
    if errors:
        print("Feed warnings: " + " | ".join(errors))


if __name__ == "__main__":
    main()
