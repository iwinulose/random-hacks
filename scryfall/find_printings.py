#!/usr/bin/env python3
"""
Look up Magic card printings via Scryfall API and output grouped tables.
Reads card names from stdin or a file; outputs card name, rarity, and sets printed in.
Supports markdown (pipe tables) or terminal-friendly table format.
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

# Price buckets for group-by price: (min_inclusive, max_exclusive, label)
PRICE_BUCKETS = [
    (0.0, 1.0, "< $1"),
    (1.0, 5.0, "$1–4.99"),
    (5.0, 10.0, "$5–9.99"),
    (10.0, 20.0, "$10–19.99"),
    (20.0, 50.0, "$20–50"),
    (50.0, float("inf"), "$50+"),
]
PRICE_BUCKET_ORDER = [label for _, _, label in reversed(PRICE_BUCKETS)]


def _cheaper_usd(card: dict) -> float | None:
    """Return the cheaper of usd and usd_foil from a Scryfall card, or None."""
    prices = card.get("prices") or {}
    vals = []
    for key in ("usd", "usd_foil"):
        s = prices.get(key)
        if s is not None and s.strip():
            try:
                vals.append(float(s))
            except ValueError:
                pass
    return min(vals) if vals else None


@dataclass(frozen=True)
class Printing:
    """A single set printing of a card."""

    code: str
    set_name: str
    released_at: str
    rarity: str
    usd_price: float | None  # cheaper of usd / usd_foil


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


@dataclass
class Section:
    """A grouped section of output: title plus a table (headers + rows)."""

    title: str
    headers: list[str]
    rows: list[list[str]]


def parse_card_line(line: str) -> str | None:
    """Strip comments, counts (e.g. 1x, 2 x), and return card name or None if empty."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # Remove leading count like "1x ", "2 x ", "3x"
    line = re.sub(r"^\s*\d+\s*x\s*", "", line, flags=re.IGNORECASE).strip()
    return line if line else None


def read_card_names(stream, unique: bool = True) -> list[str]:
    """Read card names from stream, skipping comments and counts."""
    names = []
    for line in stream:
        name = parse_card_line(line)
        if name:
            names.append(name)
    names = list(set(names)) if unique else names
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
                printings=[Printing("—", "Not found", "", "—", None)],
            )
        r.raise_for_status()
        data = r.json()

        if data.get("object") == "error":
            return CardPrintings(
                name=card_name,
                rarities=["—"],
                printings=[Printing("—", "Not found", "", "—", None)],
            )

        for card in data.get("data", []):
            code = (card.get("set") or "???").upper()
            set_name = card.get("set_name") or code
            released_at = card.get("released_at") or ""
            rarity = card.get("rarity") or ""
            usd_price = _cheaper_usd(card)
            if code not in printings_by_code:
                printings_by_code[code] = Printing(
                    code=code,
                    set_name=set_name,
                    released_at=released_at,
                    rarity=rarity,
                    usd_price=usd_price,
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


def format_price(price: float | None) -> str:
    """Format USD price for display."""
    return f"${price:.2f}" if price is not None else "—"


def _lowest_price(card: CardPrintings) -> float:
    """Lowest USD price across all printings; 0 if none."""
    prices = [p.usd_price for p in card.printings if p.usd_price is not None]
    return min(prices) if prices else 0.0


def _price_bucket_label(price: float | None) -> str:
    """Return the bucket label for a price; 'No price' if None or no bucket."""
    if price is None or price <= 0:
        return "No price"
    for lo, hi, label in PRICE_BUCKETS:
        if lo <= price < hi:
            return label
    return "No price"


def rarity_display_name(rarity: str) -> str:
    """Title-case rarity for section headings."""
    if not rarity or rarity == "—":
        return "Other"
    return rarity.capitalize()


def build_sections_by_rarity(cards: list[CardPrintings], sort_by: str) -> list[Section]:
    """Group cards by primary (rarest) rarity; one section per rarity."""
    by_rarity: dict[str, list[CardPrintings]] = {}
    for card in cards:
        key = card.primary_rarity.lower()
        by_rarity.setdefault(key, []).append(card)

    if sort_by == "price":
        sort_key = lambda c: (-_lowest_price(c), c.name.lower())
    else:
        sort_key = lambda c: c.name.lower()

    sections: list[Section] = []
    seen_rarities = set()

    for rarity in RARITY_ORDER:
        if rarity not in by_rarity:
            continue
        seen_rarities.add(rarity)
        group = sorted(by_rarity[rarity], key=sort_key)
        rows = []
        for card in group:
            r_str = ", ".join(card.rarities)
            sets_str = format_sets_cell(card.printings, card.primary_rarity)
            # Lowest price among all printings and the set code where it occurs
            with_prices = [(p.usd_price, p.code) for p in card.printings if p.usd_price is not None]
            if with_prices:
                low_price, low_code = min(with_prices, key=lambda x: (x[0], x[1]))
                low_str = f"{format_price(low_price)} ({low_code})"
            else:
                low_str = "—"
            rows.append([card.name, r_str, low_str, sets_str])
        sections.append(
            Section(
                title=rarity_display_name(rarity),
                headers=["Card", "Rarity", "Lowest", "Sets"],
                rows=rows,
            )
        )

    for rarity_key, group in sorted(by_rarity.items()):
        if rarity_key in seen_rarities:
            continue
        group = sorted(group, key=sort_key)
        rows = []
        for card in group:
            r_str = ", ".join(card.rarities)
            sets_str = format_sets_cell(card.printings, card.primary_rarity)
            with_prices = [(p.usd_price, p.code) for p in card.printings if p.usd_price is not None]
            if with_prices:
                low_price, low_code = min(with_prices, key=lambda x: (x[0], x[1]))
                low_str = f"{format_price(low_price)} ({low_code})"
            else:
                low_str = "—"
            rows.append([card.name, r_str, low_str, sets_str])
        sections.append(
            Section(
                title=rarity_display_name(rarity_key),
                headers=["Card", "Rarity", "Lowest", "Sets"],
                rows=rows,
            )
        )
    return sections


def build_sections_by_price(cards: list[CardPrintings], sort_by: str) -> list[Section]:
    """Group cards by price bucket (lowest price across printings); one section per bucket."""
    by_bucket: dict[str, list[CardPrintings]] = {}
    for card in cards:
        low = _lowest_price(card) if any(p.usd_price is not None for p in card.printings) else None
        if low is not None and low <= 0:
            low = None
        label = _price_bucket_label(low)
        by_bucket.setdefault(label, []).append(card)

    if sort_by == "price":
        sort_key = lambda c: (-_lowest_price(c), c.name.lower())
    else:
        sort_key = lambda c: c.name.lower()

    sections: list[Section] = []
    for label in PRICE_BUCKET_ORDER + ["No price"]:
        if label not in by_bucket:
            continue
        group = sorted(by_bucket[label], key=sort_key)
        rows = []
        for card in group:
            r_str = ", ".join(card.rarities)
            sets_str = format_sets_cell(card.printings, card.primary_rarity)
            with_prices = [(p.usd_price, p.code) for p in card.printings if p.usd_price is not None]
            if with_prices:
                low_price, low_code = min(with_prices, key=lambda x: (x[0], x[1]))
                low_str = f"{format_price(low_price)} ({low_code})"
            else:
                low_str = "—"
            rows.append([card.name, r_str, low_str, sets_str])
        sections.append(
            Section(
                title=label,
                headers=["Card", "Rarity", "Lowest", "Sets"],
                rows=rows,
            )
        )
    return sections


def build_sections_by_set(cards: list[CardPrintings], sort_by: str) -> list[Section]:
    """Group by set; one section per set with Card, Rarity, Price. Sets ordered by card count (desc) then release date (newest first)."""
    by_set: dict[str, tuple[str, str, list[tuple[str, str, float | None]]]] = {}
    for card in cards:
        for p in card.printings:
            if p.code == "—":
                continue
            if p.code not in by_set:
                by_set[p.code] = (p.set_name, p.released_at, [])
            by_set[p.code][2].append((card.name, p.rarity or "—", p.usd_price))

    set_items = [
        (code, set_name, released_at, entries)
        for code, (set_name, released_at, entries) in by_set.items()
    ]
    set_items.sort(key=lambda x: x[2] or "", reverse=True)
    set_items.sort(key=lambda x: len(x[3]), reverse=True)

    rarity_order = {r: i for i, r in enumerate(RARITY_ORDER)}

    if sort_by == "rarity":
        def entry_sort(e: tuple[str, str, float | None]) -> tuple[int, str]:
            name, rarity, _ = e
            return (rarity_order.get((rarity or "").lower(), len(RARITY_ORDER)), name.lower())
    elif sort_by == "price":
        def entry_sort(e: tuple[str, str, float | None]) -> tuple[float, str]:
            name, _, price = e
            return (-(price or 0.0), name.lower())
    else:  # name
        def entry_sort(e: tuple[str, str, float | None]) -> str:
            return e[0].lower()

    sections: list[Section] = []

    for code, set_name, released_at, entries in set_items:
        heading_date = f" ({released_at})" if released_at else ""
        title = f"{code} - {set_name}{heading_date}"
        sorted_entries = sorted(entries, key=entry_sort)
        rows = [
            [name, rarity_display_name(rarity), format_price(price)]
            for name, rarity, price in sorted_entries
        ]
        sections.append(
            Section(title=title, headers=["Card", "Rarity", "Price"], rows=rows)
        )
    return sections


def build_sections(cards: list[CardPrintings], group_by: str, sort_by: str) -> list[Section]:
    """Build sections from cards according to group_by ('rarity', 'set', or 'price') and sort_by within each group."""
    if group_by == "set":
        return build_sections_by_set(cards, sort_by)
    if group_by == "price":
        return build_sections_by_price(cards, sort_by)
    return build_sections_by_rarity(cards, sort_by)


def format_sections_markdown(sections: list[Section]) -> str:
    """Render sections as markdown tables."""
    out = []
    for sec in sections:
        out.append(f"\n### {sec.title}\n")
        out.append("| " + " | ".join(sec.headers) + " |")
        out.append("|" + "|".join("------" for _ in sec.headers) + "|")
        for row in sec.rows:
            escaped = [
                cell.replace("|", "\\|").replace("\n", "<br>")
                for cell in row
            ]
            out.append("| " + " | ".join(escaped) + " |")
    return "\n".join(out).strip()


def _column_widths(headers: list[str], rows: list[list[str]]) -> list[int]:
    """Compute max width per column (including header)."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            # Multi-line cells: use max line length
            line_lens = [len(line) for line in cell.split("\n")]
            w = max(line_lens) if line_lens else 0
            if i < len(widths):
                widths[i] = max(widths[i], w)
            else:
                widths.append(w)
    return widths


def format_sections_table(sections: list[Section]) -> str:
    """Render sections as terminal-friendly fixed-width tables. Multi-line cells (e.g. sets) get one line per item."""
    out = []
    for sec in sections:
        if not sec.rows:
            out.append(f"\n{sec.title}\n")
            continue
        widths = _column_widths(sec.headers, sec.rows)
        pad = "  "
        header_line = pad.join(h.ljust(widths[i]) for i, h in enumerate(sec.headers))
        sep = "-" * len(header_line)
        out.append(f"\n{sec.title}\n")
        out.append(header_line)
        out.append(sep)
        for row in sec.rows:
            cell_lines = [cell.split("\n") for cell in row]
            max_lines = max(len(lines) for lines in cell_lines)
            for line_idx in range(max_lines):
                cells = []
                for i, lines in enumerate(cell_lines):
                    w = widths[i] if i < len(widths) else 0
                    line = lines[line_idx] if line_idx < len(lines) else ""
                    cells.append(line.ljust(w))
                out.append(pad.join(cells))
    return "\n".join(out).strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Look up Scryfall printings for a list of card names and output grouped tables."
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
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "-g",
        "--group-by",
        choices=["rarity", "set", "price"],
        default="rarity",
        help="Group output by rarity, set, or price bucket (default: rarity)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "table"],
        default="markdown",
        help="Output format: markdown (pipe tables) or table (terminal-friendly fixed-width) (default: markdown)",
    )
    parser.add_argument(
        "-s",
        "--sort-by",
        choices=["rarity", "name", "price"],
        default="rarity",
        help="Sort within each group: rarity (then name), name, or price descending (default: rarity)",
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

    sections = build_sections(cards, args.group_by, args.sort_by)
    if args.format == "table":
        out.write(format_sections_table(sections))
    else:
        out.write(format_sections_markdown(sections))
    if out != sys.stdout:
        out.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
