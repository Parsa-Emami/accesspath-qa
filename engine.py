from html.parser import HTMLParser


class PageChecks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_language = False
        self.missing_alt = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.has_language = bool((attributes.get("lang") or "").strip())
        if tag == "img" and attributes.get("alt") is None:
            self.missing_alt += 1


def evaluate(data, fixture_path):
    if not isinstance(data["steps"], list) or not data["steps"]:
        raise ValueError("at least one journey step is required")
    findings = []
    step_ids = set()
    for step in data["steps"]:
        identifier = step["id"]
        if not isinstance(identifier, str) or not identifier or identifier in step_ids:
            raise ValueError("steps require unique non-empty IDs")
        step_ids.add(identifier)
        parser = PageChecks()
        parser.feed(step["html"])
        parser.close()
        if not parser.has_language:
            findings.append({"code": "document_language_missing", "step": identifier})
        if parser.missing_alt:
            findings.append({"code": "image_alt_missing", "step": identifier, "count": parser.missing_alt})
    return findings
