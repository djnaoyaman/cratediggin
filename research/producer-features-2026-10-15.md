# Producer features and requested catalog additions

Version 14.2. Catalog 262 tracks, all with a YouTube ID. This update adds 11 requested DJ Shadow/UNKLE songs and 25 J Dilla/Madlib-related entries. Existing IDs and URLs remain stable. Producer features show DJ Shadow (19 tracks), J Dilla/Jay Dee (16), and Madlib (16). Features now sort chronologically and include post-1999 works.

## Source and version decisions

- DJ Shadow's album Part 1 / Blue Sky Revisit now has the 1996 album title/year and matching Topic audio `DyzGu8ZaCrw`. It retains the existing page ID. Building Steam is not described as the first album track; Best Foot Forward precedes it.
- The Number Song and Cut Chemist Remix retain the two user-specified IDs from PR 5.
- Got 'Til It's Gone original has Janet Jackson/Jimmy Jam/Terry Lewis production, per Universal Music's credits. It is in the catalog but not the Dilla production feature. The Ummah Jay Dee's Revenge Mix is added separately and appears in that feature.
- Find a Way remains credited to The Ummah. The Dilla feature includes the team credit explicitly without silently converting it to an individual production credit.
- De La Soul's supplied title The Knock could not be matched to The Grind Date. Shopping Bags (She Got from You) is included instead; the artist's official video explicitly credits Madlib. No fictitious song was created.
- The Red uses Stones Throw's original-version upload `VRzRSCRZweY`. Production is J Dilla; Madlib raps. It appears in both features as a Jaylib collaboration, with that exception described in the Madlib feature note.
- Thuggin' is dated 2011 (EP), with Piñata's 2014 album appearance distinguished. Road of the Lonely Ones is dated 2020 (single), with Sound Ancestors' 2021 date distinguished. Microphone Mathematics and Low Class Conspiracy are dated to the 1999 single, not the 2000 album. America's Most Blunted is dated to the 2003 single, not the 2004 album.
- Donuts entries do not claim that every track was made in a hospital on an MPC. Workinonit is identified as CD track 2, after Donuts (Outro). The suggested So Far to Go / Bye sample relationship is not added as an established fact.

## Verification and limits

All 36 newly added songs plus the corrected Shadow Part 1 were checked with YouTube oEmbed for title and uploader. An additional original Janet version is included in those 25 Dilla/Madlib-related entries. Official artist/label/VEVO/Topic uploads were found except Auditorium, where an ordinary-user upload `11q1woSYCKg` is explicitly labeled reference audio, with `official: false`, after searching for an official upload. This is not a claim that an official upload cannot exist.

oEmbed does not verify actual audible contents, Japanese regional availability, or successful playback. Sample-by-sample recording identities remain unverified and are not invented. Local build, catalog audit and the actual producer feature selection code are checked. `scripts/verify_producer_features.js` guards the requested song lists, audio IDs, generated pages, chronological order, and the credit distinctions above during deployment.

Primary references are embedded in each track. Key references include Stones Throw's Jaylib announcement and catalog, DJ Shadow's official album pages and Bandcamp, Madlib's Bandcamp, Universal Music's Janet credits and anniversary announcement, and De La Soul's official Shopping Bags video description.
