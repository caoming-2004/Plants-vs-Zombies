# Visual and Audio Presentation Contract

## Scope

Windows desktop only. Rendering and music are presentation concerns and must not mutate simulation rules or outcomes.

## Text rendering

- All game text continues through the shared renderer text path and existing Noto Sans SC asset.
- The logical 1050×600 scene remains authoritative for layout and pointer coordinates.
- Window scaling uses a quality-preserving path; cached text rendering remains bounded and must not allocate/re-rasterize an unbounded surface every frame.
- Missing glyph/font resources use the existing resource error handling and a compatible fallback where available.

## Backgrounds

- Background selection identifiers remain `day`, `night`, `dusk`; current menu selection behavior and stored choice remain compatible.
- Each manifest item points to an offline bundled 2560×1440 or larger image and thumbnail, with integrity hash and provenance/license metadata.
- Catalog validation failure resolves to an available default and does not block the game loop.
- Background selection changes only rendering and existing background preference; it cannot change grid geometry or simulation state.

## Music

- Input to music playback is the current UI/game state and persisted `music_enabled`/`music_volume` preference.
- Main menu and active gameplay may play their respective bundled loops. Pause suspends or stops gameplay music; resume continues without a duplicate channel. Result transition stops the loop; victory plays one cue, defeat does not.
- Disabling music immediately silences music. Volume is clamped to 0.0–1.0 and applied consistently to current and subsequent tracks.
- Missing/invalid audio, mixer initialization error, or unavailable audio device degrades to silent play without blocking startup or gameplay.
- No runtime downloads. Any optional Junliang/dog voice clip must be supplied by the user or have explicit permission and be documented in provenance.

## Packaging

- Desktop assets are included by the existing Windows PyInstaller data collection.
- The directory package includes required font/music license and attribution/provenance notices.
- Android packaging is unchanged and outside acceptance scope.
