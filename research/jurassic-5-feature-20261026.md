# Jurassic 5 artist feature — 2026-10-26

## Scope

One dependent release: the requested artist feature, five newly needed recording pages, the exact requested replacement for existing Jayou, and shared rendering for an optional name-tag hero and a feature-specific listening order. PUTS and Cut Chemist feature publications are separate. No supplied photo yet: no portrait fabricated or imported. Held PR #100 is not part of this work.

Base: 5db099cfa8a8fb66f0f4a63eb3ff507b02388fda / 641 records / v22.228.
Candidate: 646 records / 23 Jurassic 5 records / v22.229.

## Exact user-selected audio

- The Game: n1Q958eWCxA
- Lausd: JjyUI40Umg8
- Contact: egtB6CzGkHY
- Canto De Ossanha: -dZQgvRMFIA
- Existing Jayou replacement: 2ZuN8rc6y7s
- New Jayou (Remix): pSUeddnqv6o

All returned HTTP 200 from YouTube oEmbed on 2026-10-26 with exact titles and Jurassic 5 - Topic / UCiXGLhdMax4XsC8JBo9PZ4A. PIAS deliveries for the first four; Symphonic Distribution / Mass Appeal for Jayou editions. The website-authenticated @J5Official channel is a separate identity; Topic is not called a direct artist upload. Metadata checks do not establish playback, Japanese-region playback, embedding success or master identity.

## Sources and edition decisions

- https://medium.com/cuepoint/check-the-technique-jurassic-5-s-quality-control-f6933702c2dd — Brian Coleman liner notes for Get On Down's 2015 reissue, developed with all six members. Establishes distinct track production and guest credits. Lausd and Contact: Cut Chemist. The Game: Cut Chemist, co-produced DJ Nu-Mark; guests Shawny Mac and Marvski.
- https://music.apple.com/us/album/quality-control/1673109195 — selected 2000 album catalog and actual cover visually inspected.
- https://music.apple.com/us/album/feedback/1673100965 — 2006 catalog and actual cover visually inspected.
- https://djnu-mark.com/discography/ — maker's catalog includes Canto De Ossanha. Selected PIAS metadata credits DJ Nu-Mark and composers Baden Powell / Vinicius de Moraes. No unverified sampled performance is inserted.
- https://music.apple.com/us/album/j5-deluxe-edition/1777704233 — selected J5 / 2008 Mass Appeal catalog; actual bronze/black cover inspected.
- https://www.hhv.de/records/artikel/jurassic-5-jayou-cut-chemist-remix-164256 — supplemental retail evidence of a 2005 remix issue. Equality to selected digital remix is NOT established. 2008 is explicitly a selected-edition year, not an asserted remix first release.

Original Jayou preserves existing text/artwork and the 1998 compilation context, now explicitly qualified. The 1997 EP and selected 2008 distribution are separately described. No existing Jayou art is recolored to pretend it was made for a different cover.

## Artwork

Built-in imagegen only. Original flat hand-painted letterforms, black/white counters and spray; no scenery, people, props, 3D extrusion, shadow or site signature. Each track has its exact title plus JURASSIC 5; REMIX is prominent on the separate remix image. Accent palette is an editorial approximation after viewing the official catalog covers. Original PNGs retained. Repository artwork_display.normalize performs canvas-only alpha>=8 bbox normalization with 7% safe margins; visible lettering pixels are not rescaled or redrawn.

The artist feature's monochrome name tag is a new original, not a copy of the J5 logo. Photos can later use the existing visual.photo/precomposed path without replacing this tag.

## Preservation

Existing 641 records remain byte-for-byte equivalent as parsed dictionaries except the specifically requested Jayou audio/edition fields. Old image blobs and all photos remain identical. Lesson 4 keeps its existing Cut Chemist main credit and selected uqq6Yg-2XC0. Schooled in the Trade and Sunroof retain the exact user-selected ZqpqMKKrbJs and 8TBVH6XRVaI. Existing player/router and HYBRID overlay code remain unchanged.

## Checks

scripts/verify_jurassic_feature.py covers 646-record identity/edition preservation, selected IDs, producer separation, all old image hashes, new alpha/canvas sizing, existing feature preservation, nine-track route and generated direct pages. Browser coverage is scripts/verify_jurassic_feature_browser.cjs at 390/1280px, direct/SPA entry, no read autoplay, route play, remix, Back and overflow. Actual browser checks run in existing GitHub Actions; local Chromium socket-launch workaround is not attempted.
