# Changelog

Every working build of `main` is a release (`v<version>-<CI run>`); the
declared version moves with every change to the plugin's sources.

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
