"""Bounded RFC 9309 path policy: merged groups, longest rule, Allow ties.

This evaluates published policy, not whether a provider's real IP can fetch.
"""
import re
from urllib.parse import quote, urlsplit


def octets(value):
    value = quote(value, safe="/%*?$=&:+,;@!~'()-._")
    def decode(match):
        code = int(match.group(1), 16)
        char = chr(code)
        return char if char.isascii() and (char.isalnum() or char in "-._~") else "%" + match.group(1).upper()
    return re.sub(r"%([0-9a-fA-F]{2})", decode, value)


class RobotsPolicy:
    def __init__(self, body=""):
        self.groups = []
        self.delays = []
        agents, rules = [], []
        seen_rule = False
        for raw in body.splitlines():
            line = raw.split("#", 1)[0].strip().lstrip("\ufeff")
            if ":" not in line: continue
            field, value = (part.strip() for part in line.split(":", 1))
            field = field.lower()
            if field == "user-agent":
                if seen_rule:
                    self.groups.append((agents, rules)); agents, rules, seen_rule = [], [], False
                agents.append(value.lower())
            elif field in {"allow", "disallow"} and agents:
                seen_rule = True
                if value: rules.append((field, value))
            elif field == "crawl-delay" and agents:
                seen_rule = True
                try:
                    delay = float(value)
                    if 0 <= delay < float("inf"): self.delays.append((agents.copy(), delay))
                except ValueError: pass
        if agents: self.groups.append((agents, rules))

    def decision(self, agent, url):
        token = agent.lower().split("/", 1)[0]
        specific = [rules for agents, rules in self.groups if token in agents and token != "*"]
        selected = specific or [rules for agents, rules in self.groups if "*" in agents]
        parsed = urlsplit(url)
        path = octets((parsed.path or "/") + ("?" + parsed.query if parsed.query else ""))
        matches = []
        for rules in selected:
            for field, value in rules:
                normal = octets(value)
                anchored = normal.endswith("$")
                pattern = normal[:-1] if anchored else normal
                regex = "^" + re.escape(pattern).replace(r"\*", ".*") + ("$" if anchored else "")
                if re.search(regex, path):
                    # Percent-encoded sequences each represent a single octet.
                    specificity = len(re.sub(r"%[0-9A-F]{2}", "x", pattern.replace("*", "")))
                    matches.append((specificity, field == "allow", field, value))
        winner = max(matches, default=None)
        return {"allowed": winner[1] if winner else True,
                "matched_rule": f"{winner[2]}: {winner[3]}" if winner else None,
                "group": "specific" if specific else "wildcard" if selected else "none"}

    def can_fetch(self, agent, url):
        return self.decision(agent, url)["allowed"]

    def crawl_delay(self, agent):
        token = agent.lower().split("/", 1)[0]
        specific = any(token in agents for agents, _ in self.groups)
        return max((delay for agents, delay in self.delays if token in agents or (not specific and "*" in agents)), default=0)
