# droidtop-plugin-nyaa

An **unofficial** plugin for [droidtop](https://github.com/Droidtop/droidtop) from
gamegrab-sources. It is not part of droidtop and is not affiliated with Nyaa or
Sukebei.

## What it does

- **Get games** (droidtop's `library.sources`): searches the games categories of
  Nyaa (Software - Games) and, when you turn it on, Sukebei (Art - Games) through
  their public RSS search feeds. Results show size, seeders and the site; searches
  are kept for 30 minutes.
- **A result** shows its size, seeders, category and upload date, and offers
  **Open in a torrent app**: droidtop has no torrent client, so the torrent's
  magnet link is handed to a torrent app you have installed. The game lands
  where that app saves it; add that folder to droidtop's game folders to see it
  in your library.
- **Settings**: Nyaa on or off, Sukebei on or off (off at first), trusted
  uploaders only.

The magnet link opens through Android's chooser. When that is not possible
(an older droidtop, the permission turned off, or no torrent app installed) the
button shows the link to copy and says why.

## Permissions

- Connect to nyaa.si and sukebei.nyaa.si.
- Open links in other apps (the magnet link, to your torrent app).

It runs contained in droidtop (no network or files of its own) and makes one
request per search per site, at most one request every 2 seconds per site.

## Building

`./build.sh` writes `build/manifest.json` and `build/plugin.py` (the source with
the shared `gamegrab` module from the `common` submodule embedded); `./sign.sh`
signs and packs it. CI does both and publishes every working build of `main` as
a release; the gamegrab-sources catalog lists it from there. Tests:
`python3 common/test_gamegrab.py && python3 test_plugin.py`.

## Licence

GPL-3.0, see LICENSE and NOTICE.
