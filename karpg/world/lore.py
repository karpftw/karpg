"""
Lore Descriptions

Race + class combination lore blurbs shown during character creation.
No Evennia imports — pure data.

48 combinations: 6 races × 8 classes.
"""

RACE_CLASS_DESCRIPTIONS = {
    "human": {
        "warrior": (
            "The Human Warrior is the backbone of Newhaven's militia — no frills, no "
            "excuses. What they lack in natural gifts they make up for with relentless "
            "training. Their adaptability lets them master any weapon or tactic."
        ),
        "mage": (
            "Human Mages rise through raw study and sheer persistence. Without elven "
            "memory or gnomish trick, they claw for every arcane advantage. Their "
            "adaptability lets them pivot between schools faster than any other race."
        ),
        "thief": (
            "The Human Thief learned their trade on Newhaven's back streets, where "
            "survival demanded cunning over strength. Adaptable by nature, they can "
            "learn from any guildmaster willing to teach."
        ),
        "druid": (
            "The Human Druid feels the pulse of the wild without any innate attunement "
            "— only patience and practice. Their devotion to nature is chosen, not "
            "inherited, which the old spirits respect above all."
        ),
        "priest": (
            "Human Priests are the most numerous clergy in the realm, filling every "
            "temple from the grand to the roadside. Their faith is ordinary made "
            "extraordinary — no divine bloodline, just stubborn devotion."
        ),
        "warlock": (
            "The Human Warlock made a bargain without the natural resilience to soften "
            "its cost. They endure regardless, fueling their darker gifts through "
            "willpower alone. Adaptability keeps them alive when the pact demands too much."
        ),
        "gypsy": (
            "The Human Gypsy wanders every road and knows every shortcut. Without racial "
            "advantage, they've mastered the art of reading people — the first and last "
            "tool of the trade."
        ),
        "mystic": (
            "The Human Mystic seeks the Way without a natural reservoir of Kai to draw "
            "on. Their discipline is earned grain by grain — proof that the body can be "
            "shaped by the mind alone."
        ),
    },
    "dwarf": {
        "warrior": (
            "Dwarven Warriors were forged in the deep halls long before men raised their "
            "first walls. Stocky and immovable, they outlast every opponent. In the "
            "tunnels they call home, they are terrifying beyond measure."
        ),
        "mage": (
            "A Dwarven Mage is a rare and stubborn contradiction — low natural INT offset "
            "by iron will. They favor earth and fire, spells that feel solid. Other mages "
            "sneer; they are silenced when the mountain moves."
        ),
        "thief": (
            "The Dwarven Thief is slow-footed but sure-handed. In the deep tunnels where "
            "others are blind, they are kings — stonecunning reveals every hidden lock "
            "and trap before it springs."
        ),
        "druid": (
            "Dwarven Druids tend stone and metal rather than leaf and root. They hear the "
            "voice in the seam of ore, the patience in the stalagmite. Nature underground "
            "is their domain."
        ),
        "priest": (
            "The Dwarven Priest serves gods as old as the mountains themselves. Their "
            "healing is practical and unglamorous — no song, no ceremony, just a hand on "
            "the wound and a prayer that works."
        ),
        "warlock": (
            "The Dwarven Warlock binds darker powers with the same stubbornness they "
            "apply to everything else. Their magic resistance makes them hard to curse "
            "and harder to kill. The pact respects durability."
        ),
        "gypsy": (
            "An unusual pairing: the plodding, blunt Dwarf in a vocation requiring charm "
            "and grace. Yet Dwarven Gypsies succeed because their honesty is disarming "
            "— nobody suspects the short one with the beard."
        ),
        "mystic": (
            "The Dwarven Mystic channels Kai through the body's deepest ore — slow to "
            "accumulate, impossible to exhaust. Their unarmed strikes carry the weight "
            "of the mountain itself."
        ),
    },
    "elf": {
        "warrior": (
            "Elven Warriors trade brute force for precision — a thousand cuts where "
            "others swing once. Their agility makes them difficult to pin, and their "
            "battlefield awareness spots every opening. Fragile, yes. Easy to kill, no."
        ),
        "mage": (
            "The Elf and magic are inseparable. Elven Mages are fluid, intuitive, and "
            "precise. Their innate spell resistance protects them from counterspells "
            "and ambient enchantments alike."
        ),
        "thief": (
            "The Elven Thief is the archetype the guild stories are built around — "
            "silent, elegant, and gone before anyone looks up. Their stealth bonus is "
            "not skill; it is simply what they are."
        ),
        "druid": (
            "Elven Druids are the oldest tradition in the realm. They do not study "
            "nature; they remember it, the way they remember three centuries of sunrise. "
            "Every animal, every plant is kin."
        ),
        "priest": (
            "Elven Priests serve gods of beauty and twilight. Their healing carries a "
            "melancholy grace — they know every patient is temporary, every life a brief "
            "candle. They heal anyway."
        ),
        "warlock": (
            "The Elven Warlock binds power through elegance rather than brute compulsion. "
            "Their innate resistance means the pact pushes back less. They are comfortable "
            "in uncomfortable arrangements."
        ),
        "gypsy": (
            "The Elven Gypsy is the fortune-teller who actually sees something. High CHM "
            "and a face that age never touches — merchants open their purses before they "
            "realize it. The curse might even be real."
        ),
        "mystic": (
            "Elven Mystics flow through their forms like water through reed grass — "
            "observing, yielding, never quite where the blow lands. Their Kai is "
            "luminous and fast-cycling."
        ),
    },
    "half_orc": {
        "warrior": (
            "The Half-Orc Warrior is the simplest answer to every problem: hit it until "
            "it stops. High HLT means they absorb punishment that ends lesser fighters, "
            "and blood rage turns near-death into terrifying fury."
        ),
        "mage": (
            "A Half-Orc Mage confounds every assumption. Low INT limits mana, but what "
            "they do cast hits hard — they compensate with aggressive, close-range tactics "
            "most mages consider beneath them."
        ),
        "thief": (
            "Subtlety is not a Half-Orc's natural strength, but neither is being "
            "predictable. The Half-Orc Thief gets what they want one way or another, "
            "and brute force disguised as cunning still works."
        ),
        "druid": (
            "The Half-Orc Druid connects to the raw, violent face of nature — the storm, "
            "the predator, the flood. Their healing is rough and loud; it works anyway. "
            "Animals respect strength."
        ),
        "priest": (
            "The Half-Orc Priest preaches through example. Not beautiful or eloquent, "
            "but their deity chose them for the same reason armies choose shock troops: "
            "effectiveness. They take a punch and keep praying."
        ),
        "warlock": (
            "The Half-Orc Warlock offers the dark patron something most petitioners "
            "cannot: a body that survives the cost. Their durability makes them ideal "
            "hosts for power that would shatter frailer vessels."
        ),
        "gypsy": (
            "A Half-Orc Gypsy works by intimidation rather than charm — fewer 'may I?' "
            "and more 'you will.' Surprisingly effective. Most merchants prefer "
            "negotiating to fighting."
        ),
        "mystic": (
            "The Half-Orc Mystic channels Kai through sheer physical presence. Their "
            "techniques are blunt, brutal, and nearly impossible to redirect. Blood rage "
            "and Kai fury overlap dangerously."
        ),
    },
    "gnome": {
        "warrior": (
            "The Gnome Warrior is small and easily underestimated — the last mistake "
            "opponents make. Their agility compensates for reduced strength, and they "
            "hit gaps in armor other races can't angle into."
        ),
        "mage": (
            "Gnomish Mages are the craft's great tinkerers: they improve on established "
            "formulas and invent shortcuts. Mana affinity means they sustain more spells "
            "per rest than their peers."
        ),
        "thief": (
            "The Gnome Thief is the platonic ideal of the profession. Small hands, nimble "
            "fingers, lockpick affinity, and a face nobody notices. The empty vault leaves "
            "no witnesses."
        ),
        "druid": (
            "Gnome Druids study nature as systematically as they study everything else "
            "— catalogued and cross-referenced. Their spells are precise. Their healing "
            "is administered like medicine."
        ),
        "priest": (
            "The Gnomish Priest runs a small operation but is meticulous about it. Their "
            "faith is documented. Their prayers are filed. Their healing rate is efficient "
            "and reproducible. The gods find this charming."
        ),
        "warlock": (
            "The Gnome Warlock approaches their patron as a research arrangement: mutual "
            "benefit, documented terms, exit clauses. Mana affinity keeps them casting "
            "long after the negotiation is technically over."
        ),
        "gypsy": (
            "Gnome Gypsies know exactly how much a thing costs and exactly what it's "
            "worth — the difference is their profit. Their mana affinity makes even "
            "trivial enchantments last just long enough."
        ),
        "mystic": (
            "The Gnomish Mystic discovers Kai through mechanical observation: angles, "
            "leverage, efficiency. Their techniques are almost architectural. Mana "
            "affinity translates to faster Kai recovery in practice."
        ),
    },
    "halfling": {
        "warrior": (
            "The Halfling Warrior is an absurdity that somehow works. No two-handed "
            "weapons, reduced strength — and yet their luck turns aside blows that "
            "should end them. Opponents grow superstitious."
        ),
        "mage": (
            "Halfling Mages are small in stature, vast in confidence. Their lucky streak "
            "extends to spells, where misfires resolve in their favor more often than "
            "probability allows. They do not question it."
        ),
        "thief": (
            "The Halfling Thief is almost unfair — maximum AGI, stealth bonus, and luck "
            "that borders on divine protection. They are not the best thieves in Newhaven; "
            "they are the ones who never get caught."
        ),
        "druid": (
            "Halfling Druids speak to small things: field mice, garden snakes, house "
            "sparrows. The large predators ignore them. The small ones confide everything. "
            "They know more than they let on."
        ),
        "priest": (
            "The Halfling Priest has an outsized faith in a compact package. Their luck "
            "is interpreted as divine favor, which may be accurate. Their congregation "
            "finds their cheerfulness either reassuring or infuriating."
        ),
        "warlock": (
            "The Halfling Warlock's lucky streak complicates their pact — the patron "
            "expected more suffering in exchange for power. Somehow the cost never quite "
            "lands. Neither party fully understands why."
        ),
        "gypsy": (
            "The Halfling Gypsy is the road's natural element: small, overlooked, gone "
            "before anyone takes inventory. What they don't steal on skill, fortune "
            "provides."
        ),
        "mystic": (
            "The Halfling Mystic is a riddle: the Way teaches discipline; halfling luck "
            "is random and outside any teaching. Yet the two coexist, producing a "
            "practitioner whose outcomes defy prediction."
        ),
    },
}


def get_combo_description(race_key, class_key):
    """Return lore blurb for race+class combo, or generic fallback."""
    race_key = (race_key or "human").lower().strip()
    class_key = (class_key or "warrior").lower().strip()
    race_data = RACE_CLASS_DESCRIPTIONS.get(race_key, {})
    return race_data.get(class_key, "An adventurer of uncertain origin.")
