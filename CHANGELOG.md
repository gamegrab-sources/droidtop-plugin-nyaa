# Changelog

Every working build of `main` is a release (`v<version>-<CI run>`); the
declared version moves with every change to the plugin's sources.

## 0.5.0

- `featured` (droidtop docs/plugin-api.md 1.8, Droidtop/tracker#612): the turned-on sites' newest games, their RSS
  feed with no query, newest first, at most the `limit` droidtop asks for (up to 60), for droidtop's Get new games
  page. Only for that page as a whole and for PC: a torrent's title does not reliably say which system it is for, so
  a console's page gets none.

## 0.4.1

- The release of 0.4.0's facets and contract 3 changes. 0.4.0's two commits shared one declared version, so CI's version rule refused the second
  and 0.4.0 was never released; this version carries both unchanged.

## 0.4.0

- The settings are `settings.page` facets (droidtop docs/plugin-api.md 1.10) in place of the `ui.settings` view: the
  same three switches, each saved on its own as it is turned (`set`, with droidtop's `value`).
- The manifest says `"contractVersion": 3`: it needs facets, so a droidtop built before them refuses this version
  and keeps the one installed, rather than install a plugin whose settings it cannot draw (droidtop docs/plugin-api.md
  7, "Contract 3").

## 0.3.2

- Names its kind for droidtop's Plugins page (`category`, docs/plugin-api.md 1.2, Droidtop/tracker#179).

## 0.3.1

- Declares that it serves every system (`"*"`): its torrents cover consoles and PC.
  Needs a droidtop that reads `systems` on `library.sources` (docs/plugin-api.md 1.6); an older
  droidtop ignores the field and lists the source everywhere, as before.

## 0.3.0

- Shorter text: a one-line description (the catalog already marks the plugin
  Unofficial), short settings, no repeated torrent note.
- Failures in plain words ("Nyaa is not answering right now") instead of
  "answered HTTP 503".
- Shared module 0.3.0: droidtop's contract 2.1 host names (needs droidtop
  0.2.0-dev.1767 or newer) and smaller data reads.

## 0.2.0

- Open in a torrent app now opens the magnet link through Android's chooser
  (droidtop's apps.view, permission "Open links in other apps"). The link
  is shown to copy only when droidtop is older, the permission is off, or
  no installed app takes magnet links, and the page says which.

## 0.1.1

- The shared module's tests run from the plugin's own folder in CI (no
  change to what the plugin does). 0.1.0 never got a release.

## 0.1.0

- First version: Get games searches Nyaa's and Sukebei's games categories
  through their RSS search feeds (Sukebei off at first); a result offers its
  torrent to a torrent app through droidtop, or shows the magnet link to copy
  while droidtop cannot open links in other apps; settings for each site and
  for trusted uploaders only.
