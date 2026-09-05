"""HTML evidence for agent reasoning, using only the Python standard library.

This is source-HTML extraction, not a visibility or accessibility-tree engine.
Selectors and passages let a browser-capable agent verify material observations.
"""
import json
import re
from html.parser import HTMLParser


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
        self.lang = ""
        self._stack, self._counts, self._heading = [], {}, ""
        self._json, self._buf = False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._counts[tag] = self._counts.get(tag, 0) + 1
        selector = f"#{a['id']}" if a.get("id") else f"{tag} [source occurrence {self._counts[tag]}]"
        style = re.sub(r"\s+", "", a.get("style", "").lower())
        hidden = "hidden" in a or "display:none" in style or "visibility:hidden" in style
        frame = {"tag": tag, "attrs": a, "selector": selector, "parts": [], "hidden": hidden,
                 "boilerplate": tag in BOILERPLATE or any(x["boilerplate"] for x in self._stack),
                 "heading": self._heading}
        if tag == "html": self.lang = a.get("lang", "")
        if tag in {"main", "nav", "header", "footer", "article", "aside"}: self.landmarks.append(tag)
        if tag == "meta": self.meta.append(a)
        if tag == "link":
            rel = a.get("rel", "").lower().split()
            if "canonical" in rel: self.canon.append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append({"lang": a["hreflang"], "href": a.get("href", "")})
        if tag == "a" and a.get("href"): self.links.append(a["href"])
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
        if tag == "a" and a.get("href"):
            self.link_details.append({"href": a["href"], "text": value[:300], "aria_label": a.get("aria-label", ""),
                                      "selector": frame["selector"], "region": "navigation" if frame["boilerplate"] else "content"})
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

    def close(self):
        super().close()
        for frame in reversed(self._stack): self._finish(frame)
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
        "hreflang": parser.hreflang[:30], "word_count": len(re.findall(r"\b[\w'-]+\b", text)), "text_length": len(text),
        "landmarks": sorted(set(parser.landmarks)), "meta_robots": ", ".join(meta.get("robots", [])),
        "meta_robot_directives": {k: ", ".join(meta.get(k, [])) for k in ("robots", "googlebot", "bingbot")},
        "description": " ".join(meta.get("description", [])), "canonical": parser.canon,
        "links_count": len(parser.links), "links": parser.link_details[:150], "controls": parser.controls[:40],
        "images": {"count": len(parser.img), "missing_alt": sum(x["alt"] is None for x in parser.img),
                   "empty_alt": sum(x["alt"] == "" for x in parser.img), "items": parser.img[:40]},
        "jsonld": {"blocks": len(parser.jsonld), "parse_errors": len(ld_errors), "errors": ld_errors,
                   "types": jsonld_types(ld), "data": ld if len(json.dumps(ld)) <= 40000 else [],
                   "data_omitted": len(json.dumps(ld)) > 40000},
        "text_sample": text[:1200], "main_text": text[:24000], "passages": parser.passages[:100],
        "evidence_truncated": len(text) > 24000 or len(parser.passages) > 100 or len(parser.link_details) > 150,
        "extraction_note": "Source HTML including noscript fallback; excludes semantic navigation/footer, scripts and explicit inline hidden content. CSS and JavaScript-enabled visibility require a browser."
    }
