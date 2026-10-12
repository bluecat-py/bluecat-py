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
    (f"{BASE}/api/v1/users/U0C6PHZMMHN/stats", False),
    (f"{BASE}/api/hackatime/v1/users/current/stats?start_date=2020-01-01", True),
    (f"{BASE}/api/hackatime/v1/users/current/stats/last_7_days", True),
]

def fetch(url, auth):
    headers = {"User-Agent": "profile-readme-stats", "Accept":
