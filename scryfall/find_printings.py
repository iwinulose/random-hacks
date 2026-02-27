#!/usr/bin/env python3
"""
Look up Magic card printings via Scryfall API and output a markdown table.
Reads card names from stdin or a file; outputs card name, rarity, and sets printed in.
"""

import argparse
import re
import sys
import time
from dataclasses import dataclass

import requests

SCRYFALL_SEARCH = "https://api.scryfall.com/cards/search"
USER_AGENT = "find_printings/1.0 (https://github.com/your-repo)"
# Most rare to least rare (for separate tables and set order)
RARITY_ORDER = ("mythic", "rare", "special", "uncommon", "common", "bonus")


@dataclass(frozen=True)
class Printing:
    """A single set printing of a card."""

    code: str
    set_name: str
    released_at: str
    rarity: str


@dataclass
class CardPrintings:
    """Result of looking up all printings for one card."""

    name: str
    rarities: list[str]
    printings: list[Printing]

    @property
    def primary_rarity(self) -> str:
        """Rarest rarity (for table grouping and set-line annotations)."""
        return _primary_rarity(self.rarities)


def parse_card_line(line: str) -> str | None:
    """Strip comments, counts (e.g. 1x, 2 x), and return card name or None if empty."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Remove leading count like "1x ", "2 x ", "3x"
    line = re.sub(r"^\s*\d+\s*x\s*", "", line, flags=re.IGNORECASE).strip()
    return line if line else None


def read_card_names(stream) -> list[str]:
    """Read card names from stream, skipping comments and counts."""
    names = []
    for line in stream:
        name = parse_card_line(line)
        if name:
            names.append(name)
    return names


def _sort_rarities(rarities: list[str]) -> list[str]:
    """Sort rarities from most rare to least (mythic first)."""
    order = {r: i for i, r in enumerate(RARITY_ORDER)}
    return sorted(set(rarities), key=lambda r: order.get(r.lower(), len(RARITY_ORDER)))


def _primary_rarity(rarities: list[str]) -> str:
    """Rarest rarity for table grouping (first in RARITY_ORDER)."""
    if not rarities:
        return "—"
    order = {r: i for i, r in enumerate(RARITY_ORDER)}
    return min(rarities, key=lambda r: order.get(r.lower(), len(RARITY_ORDER)))


def fetch_printings(card_name: str) -> CardPrintings:
    """Query Scryfall for all printings of a card. Returns a CardPrintings with sets newest-first."""
    q = f'!"{card_name}"'
    params = {"q": q, "unique": "prints"}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    printings_by_code: dict[str, Printing] = {}
    rarities_seen: set[str] = set()
    canonical_name = card_name
    url = SCRYFALL_SEARCH

    while True:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        if r.status_code == 404:
            return CardPrintings(
                name=card_name,
                rarities=["—"],
                printings=[Printing("—", "Not found", "", "—")],
            )
        r.raise_for_status()
        data = r.json()

        if data.get("object") == "error":
            return CardPrintings(
                name=card_name,
                rarities=["—"],
                printings=[Printing("—", "Not found", "", "—")],
            )

        for card in data.get("data", []):
            code = (card.get("set") or "???").upper()
            set_name = card.get("set_name") or code
            released_at = card.get("released_at") or ""
            rarity = card.get("rarity") or ""
            if code not in printings_by_code:
                printings_by_code[code] = Printing(
                    code=code,
                    set_name=set_name,
                    released_at=released_at,
                    rarity=rarity,
                )
            canonical_name = canonical_name or card.get("name", card_name)
            if rarity:
                rarities_seen.add(rarity)

        if not data.get("has_more"):
            break
        url = data.get("next_page")
        if not url:
            break
        params = {}

    printings_list = sorted(
        printings_by_code.values(), key=lambda p: p.released_at, reverse=True
    )
    rarities_list = (
        _sort_rarities(list(rarities_seen)) if rarities_seen else ["—"]
    )
    return CardPrintings(
        name=canonical_name,
        rarities=rarities_list,
        printings=printings_list,
    )


def format_sets_cell(printings: list[Printing], primary_rarity: str) -> str:
    """Format printings as lines: CODE - Name (date), with *rarity* when different from primary."""
    primary_lower = (primary_rarity or "").lower()
    lines = []
    for p in printings:
        base = (
            f"{p.code} - {p.set_name} ({p.released_at})"
            if p.released_at
            else f"{p.code} - {p.set_name}"
        )
        if p.rarity and p.rarity.lower() != primary_lower:
            base += f" **({p.rarity})**"
        lines.append(base)
    return "\n".join(lines)


def rarity_display_name(rarity: str) -> str:
    """Title-case rarity for section headings."""
    if not rarity or rarity == "—":
        return "Other"
    return rarity.capitalize()


def to_markdown_tables_by_rarity(cards: list[CardPrintings]) -> str:
    """Group cards by primary (rarest) rarity; one table per rarity."""
    by_rarity: dict[str, list[CardPrintings]] = {}
    for card in cards:
        key = card.primary_rarity.lower()
        by_rarity.setdefault(key, []).append(card)

    out = []
    seen_rarities = set()

    for rarity in RARITY_ORDER:
        if rarity not in by_rarity:
            continue
        seen_rarities.add(rarity)
        group = sorted(by_rarity[rarity], key=lambda c: c.name.lower())
        out.append(f"\n### {rarity_display_name(rarity)}\n")
        out.append("| Card | Rarity | Sets |")
        out.append("|------|--------|------|")
        for card in group:
            name_esc = card.name.replace("|", "\\|")
            r_esc = ", ".join(card.rarities).replace("|", "\\|")
            sets_str = format_sets_cell(card.printings, card.primary_rarity)
            sets_esc = sets_str.replace("|", "\\|").replace("\n", "<br>")
            out.append(f"| {name_esc} | {r_esc} | {sets_esc} |")

    for rarity_key, group in sorted(by_rarity.items()):
        if rarity_key in seen_rarities:
            continue
        group = sorted(group, key=lambda c: c.name.lower())
        out.append(f"\n### {rarity_display_name(rarity_key)}\n")
        out.append("| Card | Rarity | Sets |")
        out.append("|------|--------|------|")
        for card in group:
            name_esc = card.name.replace("|", "\\|")
            r_esc = ", ".join(card.rarities).replace("|", "\\|")
            sets_str = format_sets_cell(card.printings, card.primary_rarity)
            sets_esc = sets_str.replace("|", "\\|").replace("\n", "<br>")
            out.append(f"| {name_esc} | {r_esc} | {sets_esc} |")
    return "\n".join(out).strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Look up Scryfall printings for a list of card names and output a markdown table."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=argparse.FileType("r", encoding="utf-8"),
        default=None,
        help="Input file with one card name per line (default: stdin)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w", encoding="utf-8"),
        default=None,
        help="Output file for markdown table (default: stdout)",
    )
    args = parser.parse_args()

    stream = args.input if args.input is not None else sys.stdin
    out = args.output if args.output is not None else sys.stdout

    names = read_card_names(stream)
    if not names:
        return 0

    cards: list[CardPrintings] = []
    for i, name in enumerate(names):
        if i > 0:
            time.sleep(0.1)
        cards.append(fetch_printings(name))

    out.write(to_markdown_tables_by_rarity(cards))
    if out != sys.stdout:
        out.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
