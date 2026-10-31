# Dog Plants and Sun Visual Contract

This is an internal gameplay/UI contract; there is no new external API or save format.

## Appearance and cards

- The `dogs` plant skin shows the existing dog cards plus 胖宝宝 and 黄黄; both new cards remain unavailable outside that skin.
- 胖宝宝 represents Potato Mine behavior and does not replace 坚果墙.
- 黄黄 represents Snow Pea behavior and does not replace 豌豆射手.
- All dog body silhouettes in both `dogs` and `dogs_photo` remain inside the visible canvas; size comparison is within each skin. Nearby bodies may overlap slightly without losing identity. 胖宝宝 and 黄黄 remain `dogs`-only.

## Potato Mine

1. A successful plant command pays the configured price and starts preparation.
2. While preparing, the mine cannot explode but remains vulnerable to zombie bites through the existing plant target behavior.
3. When armed and a zombie enters configured contact range in the same lane, the mine triggers once, damages configured nearby same-lane zombies, then is removed.
4. Insufficient sun, cooldown, or occupied tile retains existing placement rejection and no-cost behavior.

## Snow Pea

1. The plant fires only under the existing same-lane/front-target rule.
2. A hit applies normal configured damage and a temporary reduction to zombie movement speed and bite frequency.
3. Repeated hits refresh effect duration without stacking slow strength; after expiry, base zombie movement speed and bite frequency resume.
4. Ordinary Peashooter projectiles and attacks remain unchanged.

## Sun presentation and input

- Both sky-origin and plant-origin pickups show an entry/fall motion, land on the lawn, and gently bob while collectible.
- The current rendered position equals the position used for pointer hit-testing.
- Collection changes the balance once; original value, spawn frequency, expiry, and paused-time behavior are unchanged.

## Performance and release

- Begin/menu switch visibly starts within 500 ms on the target desktop.
- In a standard 10-second window observation, most frame intervals are at most 20 ms and no unexplained interval exceeds 100 ms.
- Release remains an offline Windows playable folder/EXE. Temporary test EXEs and ZIPs are removed after verification; the user-facing package is retained.
