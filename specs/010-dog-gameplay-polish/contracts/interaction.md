# Player Interaction Contract

This feature changes the existing Windows desktop game controls and visual feedback. It adds no external API or network contract.

## Plant-card drag

1. Press and hold a visible plant card to begin drag.
2. The translucent dog preview follows the logical pointer continuously during movement. The lawn candidate cell may be highlighted and marked valid/invalid without moving the preview to that cell's center.
3. On release inside the lawn, evaluate the geometrically nearest cell only. A deterministic tie rule applies at exact boundaries.
4. If that cell is occupied, out of bounds, unaffordable, or otherwise invalid, show the existing reason and do not consume sun or cooldown. Never redirect to a nearby empty cell.
5. Releasing outside the lawn cancels/rejects placement. Card-to-card release and drag cancellation retain their existing behavior.

## Sun pickup

- Sky sun keeps its existing drop motion.
- Sun produced by 被窝 first appears at/next to its visible body, follows a short smooth hop to its resting grass position, then bobs as before.
- The clickable region follows the displayed position. Collecting it once increases sun once; expiry and pause timing do not change.

## Appearance selection

- Keep the current global choices for classic, cartoon dogs, and photo dogs.
- When dog cartoon assets are available, show separate selectable previews for 胖宝宝·土豆雷 and 黄黄·寒冰射手. Selecting one focuses its own preview and role label.
- Preview focus does not replace another role or alter its mechanics. The existing global dog cartoon choice remains responsible for enabling the dog-only plant cards; classic and photo choices remain available.

## Wave feedback

- Show current wave out of total waves in the existing HUD and briefly announce each wave when it begins.
- The wave cue identifies the approaching challenge but does not pause simulation or block player input.
- Enemy type cues remain visible during movement, biting, hit and death transitions; all enemy types still approach from the right toward the left.

## Existing behavior preserved

Pause/resume, sun collection, selection cancellation, shovel behavior, placement validation, win/loss overlay, restart, and return-to-menu remain available.
