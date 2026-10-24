"""Nyaa and Sukebei for droidtop: an unofficial gamegrab-sources plugin, not part of droidtop
and not affiliated with either site.

A python-kind source (droidtop docs/plugin-api.md 3 A2, `library.sources`): Get games
searches the sites' public RSS search feeds, and a result offers its torrent. droidtop
has no torrent client, so the torrent is handed to a torrent app the person installed
(a magnet link through Android's chooser); nothing is downloaded into a game folder.

It runs contained (5.3): every request goes through droidtop's `net.http`, every byte
it keeps through droidtop's data API, and it draws nothing itself.
"""
import json
import re
import time
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

import gamegrab as gg  # embedded by build.sh

SITES = {
    "nyaa": {
        "label": "Nyaa",
        "host": "nyaa.si",
        # Software - Games
        "category": "6_2",
    },
    "sukebei": {
        "label": "Sukebei",
        "host": "sukebei.nyaa.si",
        # Art - Games
        "category": "1_3",
    },
}

SETTINGS = "settings.json"
DEFAULTS = {"nyaa": True, "sukebei": False, "trustedOnly": False}
SEARCH_CACHE_S = 30 * 60
MAX_QUERY = 100

plugin = gg.Plugin("Nyaa")


def settings():
    kept = gg.read_json(SETTINGS, {}) or {}
    return {key: bool(kept.get(key, value)) for key, value in DEFAULTS.items()}


def feed_url(site, query, trusted_only):
    s = SITES[site]
    return "https://%s/?page=rss&q=%s&c=%s&f=%d" % (s["host"], quote_plus(query), s["category"], 2 if trusted_only else 0)


def parse_feed(site, xml_text):
    """The torrents one RSS answer lists, as the plugin keeps them (all a result needs, so
    the detail page asks the site nothing)."""
    out = []
    for item in gg.rss_items(xml_text, tags=("nyaa:infoHash", "nyaa:seeders", "nyaa:leechers", "nyaa:downloads", "nyaa:size", "nyaa:category", "nyaa:trusted", "nyaa:remake")):
        info_hash = (item.get("nyaa:infoHash") or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{40}", info_hash):
            continue
        view_id = re.search(r"/view/(\d+)", item.get("guid") or "")
        out.append(
            {
                "site": site,
                "id": view_id.group(1) if view_id else info_hash,
                "title": item["title"],
                "hash": info_hash,
                "size": gg.human_size(item.get("nyaa:size")),
                "seeders": _int(item.get("nyaa:seeders")),
                "leechers": _int(item.get("nyaa:leechers")),
                "downloads": _int(item.get("nyaa:downloads")),
                "category": (item.get("nyaa:category") or "").strip(),
                "trusted": (item.get("nyaa:trusted") or "").strip() == "Yes",
                "date": item.get("pubDate") or "",
                "page": item.get("guid") or "",
            }
        )
    return out


def _int(value):
    try:
        return int((value or "").strip())
    except ValueError:
        return 0


def search_sites(query, sites, trusted_only):
    results = []
    failures = []
    for site in sites:
        url = feed_url(site, query, trusted_only)

        def produce(url=url, site=site):
            answer = gg.http(url)
            if not answer.ok:
                raise gg.HostError("FAILED", gg.http_error(SITES[site]["label"], answer.status))
            return parse_feed(site, answer.body)

        try:
            results.extend(gg.cached("search-" + url, SEARCH_CACHE_S, produce))
        except gg.HostError as e:
            # One site down does not hide the other's results.
            failures.append(e)
    if failures and len(failures) == len(sites):
        raise failures[0]
    results.sort(key=lambda r: (-r["seeders"], r["title"].lower()))
    return results


def _uploaded(r):
    """When a torrent was uploaded, as a number to sort by; 0 when its date cannot be read."""
    try:
        return parsedate_to_datetime(r.get("date") or "").timestamp()
    except (TypeError, ValueError, IndexError, OverflowError):
        return 0


def latest_sites(sites, trusted_only):
    """The newest torrents of the turned-on sites: their RSS feed with no query, newest first."""
    results = []
    failures = []
    for site in sites:
        url = feed_url(site, "", trusted_only)

        def produce(url=url, site=site):
            answer = gg.http(url)
            if not answer.ok:
                raise gg.HostError("FAILED", gg.http_error(SITES[site]["label"], answer.status))
            return parse_feed(site, answer.body)

        try:
            results.extend(gg.cached("latest-" + url, SEARCH_CACHE_S, produce))
        except gg.HostError as e:
            failures.append(e)
    if failures and len(failures) == len(sites):
        raise failures[0]
    results.sort(key=lambda r: -_uploaded(r))
    return results


def result_row(r):
    badges = [SITES[r["site"]]["label"]]
    if r["trusted"]:
        badges.append("Trusted")
    return {
        "id": "%s-%s" % (r["site"], r["id"]),
        "title": r["title"],
        "subtitle": r["category"] or None,
        "columns": [c for c in (r["size"], "%d seeders" % r["seeders"]) if c],
        "badges": badges,
        "ref": r,
    }


# ------------------------------------------------------------------ library.sources (A2)


@plugin.on("library.sources", "form")
def _form(args):
    s = settings()
    enabled = [k for k in SITES if s[k]]
    options = [("all", "All sites")] + [(k, SITES[k]["label"]) for k in SITES]
    return gg.ok(
        gg.view(
            "Search Nyaa",
            [
                gg.text("query", "Search", ""),
                gg.choice("site", "Where", options, value="all"),
                None if enabled else gg.info("none", "No site is on", subtitle="Turn one on in Settings."),
            ],
        )
    )


@plugin.on("library.sources", "search")
def _search(args):
    values = args.get("values") or {}
    query = (args.get("query") or values.get("query") or "").strip()[:MAX_QUERY]
    if not query:
        return gg.ok({"results": []})
    s = settings()
    which = values.get("site") or "all"
    sites = [k for k in SITES if (s[k] if which == "all" else k == which)]
    results = search_sites(query, sites, s["trustedOnly"])
    return gg.ok({"results": [result_row(r) for r in results[:100]]})


# The platforms `featured` answers for: none named (Get new games' own page) and PC. A torrent's title does not say
# reliably which system it is for, so a console's page gets nothing rather than PC games.
FEATURED_PLATFORMS = ("", "pc", "windows")


@plugin.on("library.sources", "featured")
def _featured(args):
    """What the sites list newest (droidtop docs/plugin-api.md 1.8, Droidtop/tracker#612), for Get new games."""
    if str(args.get("platform") or "").strip() not in FEATURED_PLATFORMS:
        return gg.ok({"results": []})
    try:
        limit = max(1, min(int(args.get("limit") or 20), 60))
    except (TypeError, ValueError):
        limit = 20
    s = settings()
    sites = [k for k in SITES if s[k]]
    if not sites:
        return gg.ok({"results": []})
    results = latest_sites(sites, s["trustedOnly"])
    return gg.ok({"results": [result_row(r) for r in results[:limit]]})


@plugin.on("library.sources", "detail")
def _detail(args):
    r = args.get("ref") or {}
    if not re.fullmatch(r"[0-9a-f]{40}", str(r.get("hash") or "")) or r.get("site") not in SITES:
        return gg.error("INVALID_ARGS", "Missing torrent")
    uri = gg.magnet(r["hash"], r.get("title"))
    return gg.ok(
        gg.view(
            gg.cut(r.get("title") or "Torrent", 200),
            [
                gg.info("site", "Site", SITES[r["site"]]["label"] + (" (trusted uploader)" if r.get("trusted") else "")),
                gg.info("category", "Category", r.get("category") or None),
                gg.info("size", "Size", r.get("size") or None),
                gg.info("peers", "Seeders and leechers", "%d / %d" % (r.get("seeders") or 0, r.get("leechers") or 0)),
                gg.info("date", "Uploaded", r.get("date") or None),
                gg.button(
                    "handoff",
                    "Open in a torrent app",
                    gg.job("handoff", "Open in a torrent app", {"uri": uri, "title": r.get("title") or ""}),
                    subtitle="Add that app's download folder to your game folders to see the game here.",
                ),
            ],
        )
    )


@plugin.job("library.sources", "handoff")
def _handoff(args, report):
    uri = str(args.get("uri") or "")
    if not uri.startswith("magnet:?xt=urn:btih:"):
        return gg.failed("Missing magnet link")
    title = str(args.get("title") or "Torrent")
    return gg.handoff_result(uri, title, "Opened in your torrent app", "Install a torrent app to open magnet links.")


# ------------------------------------------------------------------ settings (C)


SETTINGS_TARGET = "settings.page"
SWITCHES = [
    ("nyaa", "Nyaa", "Games"),
    ("sukebei", "Sukebei", "Adult games"),
    ("trustedOnly", "Trusted uploaders only", None),
]


def settings_facets():
    """The settings page (droidtop plugin-api 1.10, ui.facets target settings.page): its three switches."""
    s = settings()
    facets = []
    for key, label, sub in SWITCHES:
        facet = {"id": key, "kind": "toggle", "v": 1, "targets": [SETTINGS_TARGET], "label": label, "value": s[key], "call": {"op": "set", "args": {"key": key}}}
        if sub:
            facet["sub"] = sub
        facets.append(facet)
    return {"facets": facets}


@plugin.on("ui.facets", "get")
def _facets(args):
    if args.get("target") != SETTINGS_TARGET:
        return gg.ok({"facets": []})
    return gg.ok(settings_facets())


@plugin.on("ui.facets", "set")
def _set(args):
    """One switch: droidtop sends its new value as `value`."""
    key = args.get("key")
    if key not in DEFAULTS:
        return gg.error("INVALID_ARGS", "Unknown setting")
    s = settings()
    s[key] = args.get("value") is True or str(args.get("value")).lower() == "true"
    gg.write_json(SETTINGS, s)
    return gg.ok(settings_facets())


handle, start_job, cancel_job = plugin.entry_points()
