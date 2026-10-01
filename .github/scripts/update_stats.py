import configparser, json, os, re, sys, urllib.request

BASE = "https://hackatime.hackclub.com"
USER = os.environ.get("HACKATIME_USER", "mnurfathurrahim")

def get_key():
    key = os.environ.get("HACKATIME_API_KEY", "").strip()
    if key:
        return key
    cfg = configparser.ConfigParser()
    cfg.read(os.path.expanduser("~/.wakatime.cfg"))
    return cfg.get("settings", "api_key", fallback="").strip()

KEY = get_key()

ENDPOINTS = [
    (f"{BASE}/api/v1/stats", True),
    (f"{BASE}/api/hackatime/v1/users/current/stats/last_7_days", True),
    (f"{BASE}/api/v1/users/{USER}/stats", False),
]

def fetch(url, auth):
    headers = {"User-Agent": "profile-readme-stats", "Accept": "application/json"}
    if auth:
        if not KEY:
            raise RuntimeError("no API key available")
        headers["Authorization"] = f"Bearer {KEY}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def secs(i):
    return i.get("total_seconds") or i.get("seconds") or 0

def parse(data):
    d = data.get("data", data) if isinstance(data, dict) else {}
    langs = d.get("languages", [])
    if isinstance(langs, dict):
        langs = [{"name": k, "seconds": v} for k, v in langs.items()]
    langs = [l for l in langs if isinstance(l, dict) and l.get("name")]
    langs.sort(key=secs, reverse=True)
    total = d.get("total_seconds") or sum(secs(l) for l in langs)
    return total, langs[:5]

def fmt(sec):
    h, m = divmod(int(sec) // 60, 60)
    if h:
        return f"{h} hr{'s' if h != 1 else ''} {m} min{'s' if m != 1 else ''}"
    return f"{m} min{'s' if m != 1 else ''}"

errors = []
total, langs = 0, []
for url, auth in ENDPOINTS:
    try:
        total, langs = parse(fetch(url, auth))
        if total and langs:
            print(f"Using {url}")
            break
        errors.append(f"{url}: no usable stats in response")
    except Exception as e:
        errors.append(f"{url}: {e}")
else:
    sys.exit("All endpoints failed:\n  " + "\n  ".join(errors))

lines = [f"Total Time: {fmt(total)}", ""]
for l in langs:
    s = secs(l)
    pct = 100 * s / total
    n = round(pct / 4)
    lines.append(f"{l['name']:<12}{fmt(s):<16}{'█' * n}{'░' * (25 - n)}   {pct:6.2f} %")
block = "```txt\n" + "\n".join(lines) + "\n```"

readme = open("README.md", encoding="utf-8").read()
new = re.sub(
    r"(<!--START_SECTION:waka-->).*?(<!--END_SECTION:waka-->)",
    lambda m: f"{m.group(1)}\n\n{block}\n\n{m.group(2)}",
    readme, flags=re.S,
)
open("README.md", "w", encoding="utf-8").write(new)
print("README updated")
