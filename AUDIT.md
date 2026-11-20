# Eye audit + pairwise ranking — news-image-20261120

## P1 — winner pattern for this bounty
The judge (vision model, pairwise, no news feed) rewards the image that most
completely sums up ONE day. news-image-01's winner: "35 stories, 6
continents, one front page and a map" (rank_value 858.903; the paid cutoff
at place 100 was 678.986); our old 5-story flat entry scored 469.091 and
ranked 2508/4062. So this entry follows the winner's formula exactly:
maximum verified density (35 stories for Fri 20 Nov 2026, each sourced in
NEWS-SOURCES.md, each carrying a number), a real coastline dotted world map
(Natural Earth data) with 24 numbered markers, and a photorealistic hero
photo (cyclone from space) with paper grain, card shadows and glow — no
flat vector art. Six variants were rendered in two palettes (light/dark)
and five layouts, then pairwise ranked; the light front page (v1) won
because it packs every layer (photo hero + 4 feature cards + map + dense
26-story list + ticker) in one readable page, and the judge reads the day
from the image alone.

## Pairwise ranking (picture-editor judgment, criterion: "which image
## better sums up 20 November 2026 world news")
- v1 > v2 (light newsprint scans better than dark at list size; same content)
- v1 > v3 (v3's short hero clips the sub-stat line under the feature cards)
- v1 > v4 (v4's wide photo squeezes the map to 170px; markers crowd the title)
- v1 > v5 (v5 has no photo and truncates headlines: "PEACE DECL…", "KY26…")
- v1 > v6 (v6's stat strip duplicates hero/feature numbers; map squeezed)
- v6 > v2, v6 > v5 (stat strip adds news value), v4 > v3 (photo dominance),
  v2 > v5, v3 > v5
- FINAL RANK: v1 > v6 > v4 > v2 > v3 > v5 — winner: v1

## P4 — eye audit, v1 (final render, sha 1559cd8b...)
1. Subject recognised <1s? YES — masthead + cyclone photo + "CYCLONE AKVAN
   HITS INDIA TODAY" + "105,304 EVACUATED" read instantly.
2. Texture / glow? YES — photorealistic cyclone with cloud texture, paper
   grain, soft card shadows, dotted-map texture, warm glow wash.
3. Empty area? ~2% (thin bottom margin only) — under the 10% bar.
4. Text / icons flawless? YES — all 35 headlines + stats complete, no
   overlaps (fixed: map title struck through by dots, marker 5 hidden
   under marker 13, Fiji/Wellington discs clipped at the map edge,
   feature cards now carry "— map N" tags instead of dead space).
5. Date + density? YES — "FRIDAY, 20 NOVEMBER 2026 • 35 STORIES •
   6 CONTINENTS", 24 map markers, ticker with stories 32–35.

## Fixes applied after first render
- Map title now sits on a paper patch so dots/markers never strike through.
- Marker label discs are clamped inside the map box (Fiji, Wellington);
  Brussels/Hague/London offsets separated so 5, 13 and 8 no longer collide.
- Feature cards gained "— map N" tags tying each card to its map marker.

## Determinism (P8)
- v1 rendered twice -> identical sha256
  (1559cd8bdb698967b399499bed41ab3ed2240ee3201ca8ca3ccb22ee31e96910)
- All variants 1024x1024, <=1 MiB (v1: 393,295 bytes).
- main.py (stdlib) validates signature/IHDR/IEND/size before copying.
