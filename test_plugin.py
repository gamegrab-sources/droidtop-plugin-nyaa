"""Tests for the Nyaa plugin (python3 test_plugin.py, after build.sh: it also loads the built
plugin.py with gamegrab embedded). The feed below is a small hand-written sample in the
shape the sites' RSS uses, not a copy of a real one."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "common"), os.path.join(HERE, "src")]

import gamegrab as gg  # noqa: E402
import plugin  # noqa: E402
from testing import FakeHost, envelope, install  # noqa: E402

FEED = """<rss xmlns:nyaa="https://nyaa.si/xmlns/nyaa" version="2.0"><channel><title>t</title>
<item><title>Sample Game v1.2 [Group]</title><link>https://nyaa.si/download/1001.torrent</link>
<guid isPermaLink="true">https://nyaa.si/view/1001</guid><pubDate>Wed, 01 Apr 2026 10:00:40 -0000</pubDate>
<nyaa:seeders>4</nyaa:seeders><nyaa:leechers>1</nyaa:leechers><nyaa:downloads>18</nyaa:downloads>
<nyaa:infoHash>3888fbc0f39f807569ae7aa8d21d16a8b4fec56f</nyaa:infoHash><nyaa:categoryId>6_2</nyaa:categoryId>
<nyaa:category>Software - Games</nyaa:category><nyaa:size>564.2 MiB</nyaa:size><nyaa:trusted>Yes</nyaa:trusted></item>
<item><title>Sample Game v1.1</title><guid isPermaLink="true">https://nyaa.si/view/1000</guid>
<nyaa:seeders>9</nyaa:seeders><nyaa:infoHash>0000000000000000000000000000000000000001</nyaa:infoHash>
<nyaa:category>Software - Games</nyaa:category><nyaa:size>1 GiB</nyaa:size><nyaa:trusted>No</nyaa:trusted></item>
<item><title>Broken</title><nyaa:infoHash>nothex</nyaa:infoHash></item>
</channel></rss>"""


def call(point, op, args=None):
    return json.loads(plugin.handle(envelope(point, op, args)))


def job(point, op, args=None):
    return json.loads(plugin.start_job("j", json.loads(envelope(point, op, args)), lambda p, s: None))


class Nyaa(unittest.TestCase):
    def setUp(self):
        self.host = install(gg, FakeHost({plugin.feed_url("nyaa", "sample game", False): FEED}))

    def test_search_reads_the_feed_and_caches_it(self):
        reply = call("library.sources", "search", {"query": "sample game"})
        rows = reply["data"]["results"]
        self.assertEqual([r["title"] for r in rows], ["Sample Game v1.1", "Sample Game v1.2 [Group]"])
        self.assertEqual(rows[1]["badges"], ["Nyaa", "Trusted"])
        self.assertEqual(rows[1]["columns"], ["564.2 MiB", "4 seeders"])
        call("library.sources", "search", {"query": "sample game"})
        self.assertEqual(len(self.host.requests()), 1)

    def test_sukebei_only_when_turned_on(self):
        call("library.sources", "search", {"query": "x"})
        self.assertTrue(all("sukebei" not in u for u in self.host.requests()))
        call("ui.settings", "save", {"values": {"sukebei": "true"}})
        call("library.sources", "search", {"query": "y"})
        self.assertTrue(any(u.startswith("https://sukebei.nyaa.si/?page=rss&q=y&c=1_3") for u in self.host.requests()))

    def test_detail_offers_the_magnet_and_says_droidtop_has_no_client(self):
        ref = call("library.sources", "search", {"query": "sample game"})["data"]["results"][1]["ref"]
        before = len(self.host.requests())
        page = call("library.sources", "detail", {"ref": ref})["data"]
        self.assertEqual(len(self.host.requests()), before)
        button = [n for n in page["sections"][0]["items"] if n["type"] == "button"][0]
        self.assertIn("no torrent client", button["subtitle"])
        uri = button["action"]["args"]["uri"]
        self.assertTrue(uri.startswith("magnet:?xt=urn:btih:3888fbc0f39f807569ae7aa8d21d16a8b4fec56f&dn=Sample+Game"))

    def test_handoff_falls_back_to_the_link(self):
        uri = gg.magnet("3888fbc0f39f807569ae7aa8d21d16a8b4fec56f", "x")
        result = job("library.sources", "handoff", {"uri": uri, "title": "x"})
        self.assertTrue(result["ok"])
        page = json.loads(result["values"]["view"])
        self.assertEqual(page["sections"][0]["items"][1]["value"], uri)
        self.host.handoff = True
        self.assertEqual(job("library.sources", "handoff", {"uri": uri})["values"]["message"], "Opened in your torrent app")

    def test_empty_query_asks_nothing(self):
        self.assertEqual(call("library.sources", "search", {"values": {"query": " "}})["data"]["results"], [])
        self.assertEqual(self.host.requests(), [])


class Built(unittest.TestCase):
    def test_built_plugin_loads(self):
        built = os.path.join(HERE, "build", "plugin.py")
        if not os.path.exists(built):
            self.skipTest("run build.sh first")
        scope = {"__name__": "built"}
        exec(compile(open(built, encoding="utf-8").read(), "plugin.py", "exec"), scope)
        install(scope["gg"], FakeHost())
        reply = json.loads(scope["handle"](envelope("ui.settings", "view")))
        self.assertTrue(reply["ok"])


if __name__ == "__main__":
    unittest.main()
