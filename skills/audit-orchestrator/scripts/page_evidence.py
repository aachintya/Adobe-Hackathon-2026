"""HTML evidence for agent reasoning, using only the Python standard library.

This is source-HTML extraction, not a visibility or accessibility-tree engine.
Selectors and passages let a browser-capable agent verify material observations.
"""
import json
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCKS = {"p", "li", "td", "th", "dt", "dd", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"}
SUPPRESSED = {"script", "style", "svg", "template", "head"}
BOILERPLATE = {"nav", "header", "footer", "aside"}


def clean(value):
    return " ".join(value.split())


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.link_details, self.text, self.title, self.h1 = [], [], [], [], []
        self.jsonld, self.meta, self.canon, self.img, self.landmarks = [], [], [], [], []
        self.passages, self.controls, self.hreflang = [], [], []
        self.tables, self.relationship_candidates = [], []
        self.lang = ""
        self.base_href = None
        self._stack, self._counts, self._heading = [], {}, ""
        self._json, self._buf = False, []

    def handle_starttag(self, tag, attrs):
        # HTMLParser represents a present attribute without a value as None.
        a = {key: value if value is not None else "" for key, value in attrs}
        self._counts[tag] = self._counts.get(tag, 0) + 1
        selector = f"#{a['id']}" if a.get("id") else f"{tag} [source occurrence {self._counts[tag]}]"
        style = re.sub(r"\s+", "", a.get("style", "").lower())
        hidden = "hidden" in a or "display:none" in style or "visibility:hidden" in style
        frame = {"tag": tag, "attrs": a, "selector": selector, "parts": [], "hidden": hidden,
                 "boilerplate": tag in BOILERPLATE or any(x["boilerplate"] for x in self._stack),
                 "heading": self._heading}
        if tag == "html": self.lang = a.get("lang", "")
        if tag == "base" and "href" in a and self.base_href is None: self.base_href = a["href"]
        if tag in {"main", "nav", "header", "footer", "article", "aside"}: self.landmarks.append(tag)
        if tag == "meta": self.meta.append(a)
        if tag == "link":
            rel = a.get("rel", "").lower().split()
            if "canonical" in rel: self.canon.append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append({"lang": a["hreflang"], "href": a.get("href", "")})
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        readable = not hidden and not any(x["hidden"] or x["tag"] in SUPPRESSED for x in self._stack)
        table = next((x.get("table_data") for x in reversed(self._stack) if x.get("table_data") is not None), None)
        if tag == "table" and readable:
            frame["table_data"] = {"selector": selector, "caption": "", "rows": [], "ambiguities": [], "truncated": False}
            if table is not None:
                table["ambiguities"].append("nested_table")
                frame["table_data"]["ambiguities"].append("nested_table")
        elif tag in {"tr", "td", "th", "caption"} and table is not None and readable:
            frame["table_owner"] = table
            if tag == "tr":
                if any(x.get("table_owner") is table and x["tag"] == "tr" for x in self._stack):
                    table["ambiguities"].append("unclosed_row")
                row = []
                frame["row_data"] = row
                if len(table["rows"]) < 40: table["rows"].append(row)
                else: table["truncated"] = True
            elif tag in {"td", "th"}:
                if any(x.get("table_owner") is table and x["tag"] in {"td", "th"} for x in self._stack):
                    table["ambiguities"].append("unclosed_cell")
                row_frame = next((x for x in reversed(self._stack) if x.get("table_owner") is table and "row_data" in x), None)
                if row_frame is not None: frame["cell_row"] = row_frame["row_data"]
                else: table["ambiguities"].append("cell_without_row")
        if tag == "img":
            self.img.append({"src": a.get("src", ""), "alt": a.get("alt"), "selector": selector})
            if a.get("alt"):
                for parent in self._stack:
                    if parent["tag"] in {"a", "button"}: parent["parts"].append(a["alt"])
        if tag in {"input", "select", "textarea"}:
            self.controls.append({"tag": tag, "selector": selector, "type": a.get("type", ""),
                                  "id": a.get("id", ""), "name": a.get("name", ""),
                                  "aria_label": a.get("aria-label", ""), "placeholder": a.get("placeholder", "")})
        if tag == "script" and "ld+json" in a.get("type", "").lower(): self._json, self._buf = True, []
        if tag not in VOID: self._stack.append(frame)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID: self.handle_endtag(tag)

    def _finish(self, frame):
        tag, a, value = frame["tag"], frame["attrs"], clean(" ".join(frame["parts"]))
        if tag == "title": self.title.append(value)
        if tag == "h1" and value: self.h1.append(value)
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and value: self._heading = value
        if tag in BLOCKS and value and not frame["boilerplate"]:
            self.passages.append({"selector": frame["selector"], "heading": frame["heading"], "text": value[:3000]})
        if tag == "a":
            href = a.get("href") if "href" in a else None
            self.link_details.append({"href": href, "text": value[:300], "aria_label": a.get("aria-label", ""),
                                      "selector": frame["selector"], "region": "navigation" if frame["boilerplate"] else "content"})
            if len(self.relationship_candidates) < 100:
                # Compare literal email addresses, not generic words such as "email".
                addresses = re.findall(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value)
                if isinstance(href, str) and href.lower().startswith("mailto:") and len(addresses) == 1:
                    recipients = [x.strip() for x in unquote(urlsplit(href).path).split(",")]
                    if len(recipients) == 1 and "@" in recipients[0] and addresses[0].casefold() != recipients[0].casefold():
                        self.relationship_candidates.append({"type": "email_address_mismatch", "selector": frame["selector"],
                            "text": value[:300], "href": href, "status": "candidate",
                            "reason": "Displayed email address differs from the source mailto recipient; verify the intended routing."})
                hint = clean(value or a.get("aria-label", "")).lower()
                if href in (None, "") and any(x in hint for x in ("buy", "apply", "start", "sign up", "contact", "learn more")):
                    self.relationship_candidates.append({"type": "empty_cta_link", "selector": frame["selector"],
                        "text": value[:300], "href": href, "status": "candidate",
                        "reason": "CTA-like anchor has no source href; JavaScript behavior requires browser review."})
        table = frame.get("table_owner")
        if table is not None:
            if tag == "caption":
                table["caption"] = value[:1000]
                table["truncated"] |= len(value) > 1000
            elif tag in {"td", "th"} and "cell_row" in frame:
                row = frame["cell_row"]
                if len(row) < 20:
                    row.append({"value": value[:1000], "tag": tag, "scope": a.get("scope", ""), "selector": frame["selector"]})
                else: table["truncated"] = True
                table["truncated"] |= len(value) > 1000
                for span in ("rowspan", "colspan"):
                    try:
                        if int(a.get(span, "1")) != 1: table["ambiguities"].append("spanned_cells")
                    except ValueError: table["ambiguities"].append("invalid_span")
                if a.get("headers"): table["ambiguities"].append("explicit_header_mapping_requires_review")
        if tag == "table" and "table_data" in frame:
            self.tables.append(self._build_table(frame["table_data"]))
        if tag == "button":
            self.controls.append({"tag": tag, "selector": frame["selector"], "text": value[:300], "aria_label": a.get("aria-label", "")})

    def handle_endtag(self, tag):
        if tag == "script" and self._json:
            self.jsonld.append("".join(self._buf)); self._json, self._buf = False, []
        indices = [i for i, frame in enumerate(self._stack) if frame["tag"] == tag]
        if indices:
            for frame in reversed(self._stack[indices[-1]:]): self._finish(frame)
            del self._stack[indices[-1]:]
    def handle_data(self, data):
        if self._json:
            self._buf.append(data)
            return
        value = clean(data)
        if not value: return
        if any(x["tag"] == "title" for x in self._stack):
            for frame in self._stack:
                if frame["tag"] == "title": frame["parts"].append(value)
            return
        if any(x["tag"] in SUPPRESSED or x["hidden"] for x in self._stack): return
        for frame in self._stack: frame["parts"].append(value)
        if not any(x["boilerplate"] for x in self._stack): self.text.append(value)

    def _build_table(self, table):
        """Infer relationships only for complete rectangular, simple header tables."""
        rows = table["rows"]
        if not rows or not any(cell["tag"] == "th" for row in rows for cell in row):
            table["ambiguities"].append("missing_headers")
        if rows and any(len(row) != len(rows[0]) for row in rows):
            table["ambiguities"].append("irregular_rows")
        if rows and any(cell["scope"] not in {"", "row", "col"} for row in rows for cell in row):
            table["ambiguities"].append("complex_header_scope")
        # Do not let a later header overwrite an earlier relationship.
        if any(cell["tag"] == "th" and cell["scope"] == "col" for row in rows[1:] for cell in row):
            table["ambiguities"].append("multiple_header_rows")
        if any(cell["tag"] == "th" and cell["scope"] != "row" for row in rows[1:] for cell in row[1:]):
            table["ambiguities"].append("ambiguous_body_headers")
        records = []
        if not table["ambiguities"] and not table["truncated"]:
            headers = rows[0] if rows else []
            for ri, row in enumerate(rows):
                for ci, cell in enumerate(row):
                    if cell["tag"] != "td": continue
                    row_header = row[0]["value"] if row and row[0]["tag"] == "th" and row[0]["scope"] in {"", "row"} else ""
                    col_header = headers[ci]["value"] if headers[ci]["tag"] == "th" and headers[ci]["scope"] in {"", "col"} else ""
                    if len(records) == 200:
                        table["truncated"] = True
                        break
                    records.append({"row": ri, "column": ci, "value": cell["value"],
                                    "row_header": row_header, "column_header": col_header,
                                    "qualifiers": [x for x in (row_header, col_header) if x],
                                    "value_path": f"rows.{ri}.{ci}.value",
                                    "context": " | ".join(x for x in (row_header, col_header, cell["value"]) if x),
                                    "context_is_derived": True})
                if table["truncated"]: break
        if table["truncated"]: records = []
        return {**table, "records": records, "ambiguities": sorted(set(table["ambiguities"])),
                "relationship_status": "requires_review" if table["ambiguities"] or table["truncated"] else "simple_headers",
                "note": "Context joins captured header/cell values; it is not a contiguous website quote. Cite raw cells and headers separately."}

    def close(self):
        super().close()
        for frame in reversed(self._stack):
            if "table_data" in frame: frame["table_data"]["ambiguities"].append("unclosed_table")
            self._finish(frame)
        self._stack.clear()


def jsonld_types(value):
    found = set()
    def walk(item):
        if isinstance(item, dict):
            kind = item.get("@type")
            if isinstance(kind, str): found.add(kind)
            elif isinstance(kind, list): found.update(x for x in kind if isinstance(x, str))
            for child in item.values(): walk(child)
        elif isinstance(item, list):
            for child in item: walk(child)
    walk(value)
    return sorted(found)


def page_fields(html):
    parser = PageParser(); parser.feed(html); parser.close()
    meta = {}
    for item in parser.meta:
        name = item.get("name", item.get("property", "")).lower()
        if name: meta.setdefault(name, []).append(item.get("content", ""))
    ld, ld_errors = [], []
    for index, block in enumerate(parser.jsonld):
        try: ld.append(json.loads(block))
        except (ValueError, RecursionError) as error: ld_errors.append({"block": index + 1, "error": str(error)[:200]})
    text = " ".join(parser.text)
    return parser, {
        "title": " ".join(parser.title)[:300], "h1": parser.h1[:10], "language": parser.lang,
        "base_href": parser.base_href,
        "hreflang": parser.hreflang[:30], "word_count": len(re.findall(r"\b[\w'-]+\b", text)), "text_length": len(text),
        "landmarks": sorted(set(parser.landmarks)), "meta_robots": ", ".join(meta.get("robots", [])),
        "meta_robot_directives": {k: ", ".join(meta.get(k, [])) for k in ("robots", "googlebot", "bingbot")},
        "description": " ".join(meta.get("description", [])), "canonical": parser.canon,
        "links_count": len(parser.links), "anchor_count": parser._counts.get("a", 0),
        "links": parser.link_details[:150], "controls": parser.controls[:40],
        "tables": parser.tables[:20], "relationship_candidates": parser.relationship_candidates[:100],
        "images": {"count": len(parser.img), "missing_alt": sum(x["alt"] is None for x in parser.img),
                   "empty_alt": sum(x["alt"] == "" for x in parser.img), "items": parser.img[:40]},
        "jsonld": {"blocks": len(parser.jsonld), "parse_errors": len(ld_errors), "errors": ld_errors,
                   "types": jsonld_types(ld), "data": ld if len(json.dumps(ld)) <= 40000 else [],
                   "data_omitted": len(json.dumps(ld)) > 40000},
        "text_sample": text[:1200], "main_text": text[:24000], "passages": parser.passages[:100],
        "evidence_truncated": len(text) > 24000 or len(parser.passages) > 100 or len(parser.link_details) > 150 or len(parser.tables) > 20 or any(t["truncated"] for t in parser.tables),
        "extraction_note": "Source HTML including noscript fallback; excludes semantic navigation/footer, scripts and explicit inline hidden content. CSS and JavaScript-enabled visibility require a browser."
    }
