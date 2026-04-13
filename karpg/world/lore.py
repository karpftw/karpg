"""
Lore Descriptions

Race + class combination lore blurbs shown during character creation.
No Evennia imports — pure data.

112 combinations: 14 races × 8 classes.
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
    "half_elf": {
        "warrior": (
            "The Half-Elf Warrior walks between two worlds and belongs fully to neither. "
            "They fight with elven grace and human grit — a combination that earns respect "
            "on the battlefield if nowhere else."
        ),
        "mage": (
            "The Half-Elf Mage carries just enough elven blood to feel the flow of magic "
            "but must study twice as hard to master it. They are driven by the need to "
            "prove themselves to both races."
        ),
        "thief": (
            "The Half-Elf Thief inherited elven nimbleness and human opportunism. "
            "Overlooked by both communities, they learned early that the best way to "
            "survive is never to be noticed at all."
        ),
        "druid": (
            "The Half-Elf Druid feels the pull of the forest more keenly than most humans "
            "but less wholly than full elves. That bittersweet awareness makes them "
            "devoted stewards — they cherish what they cannot fully claim."
        ),
        "priest": (
            "The Half-Elf Priest seeks belonging in devotion. The gods ask only faith, not "
            "bloodline. Their mixed heritage gives them unusual empathy for all who feel "
            "cast between worlds."
        ),
        "warlock": (
            "The Half-Elf Warlock made their pact partly out of loneliness — power fills "
            "the gap left by a community that never fully accepted them. Elven resilience "
            "steadies them when the bargain demands too much."
        ),
        "gypsy": (
            "The Half-Elf Gypsy was raised on the road, which suited them perfectly — "
            "no town ever felt like home anyway. They read people with elven subtlety "
            "and charm with human warmth."
        ),
        "mystic": (
            "The Half-Elf Mystic finds the Way a rare place of belonging. Kai does not "
            "discriminate by blood. Their dual nature — restless human will, patient elven "
            "stillness — gives them an unusual depth of focus."
        ),
    },
    "dark_elf": {
        "warrior": (
            "The Dark Elf Warrior is a shadow with a blade — faster than any surface "
            "fighter expects, and utterly without mercy. They fight to survive in a world "
            "that fears them on sight, and that suits them fine."
        ),
        "mage": (
            "The Dark Elf Mage is what surface scholars whisper about at night. Untethered "
            "from surface prejudices about which magic is forbidden, they have pursued "
            "every school with equal hunger and emerged lethal."
        ),
        "thief": (
            "The Dark Elf Thief is so naturally gifted at stealth that the guild considers "
            "them almost unsporting. They don't steal for coin alone — disappearing "
            "without a trace is a point of cultural pride."
        ),
        "druid": (
            "A Dark Elf Druid is a rare and unsettling sight. They commune with the deep "
            "places of the earth rather than open sky — the roots beneath the fungal "
            "forest, the cold springs in lightless caverns."
        ),
        "priest": (
            "The Dark Elf Priest serves gods that surface temples do not name. Their "
            "divine power is just as real, their devotion just as absolute. Those who "
            "underestimate them based on which deity they serve rarely do so twice."
        ),
        "warlock": (
            "For the Dark Elf Warlock, the pact is simply business. They have been "
            "trading power and risk since before most surface races built their first "
            "walls. The patron got exactly what it bargained for."
        ),
        "gypsy": (
            "The Dark Elf Gypsy is a contradiction in plain sight: naturally terrifying "
            "yet magnetically charming to those who get close enough. They move between "
            "communities like smoke, taking what they need and vanishing."
        ),
        "mystic": (
            "The Dark Elf Mystic channels Kai through darkness rather than light, "
            "stillness rather than motion. Their forms are angular, conserving energy "
            "for a single devastating release — patience as a weapon."
        ),
    },
    "lizardman": {
        "warrior": (
            "The Lizardman Warrior is a wall of scales and muscle that simply doesn't "
            "stop moving forward. They do not strategize much, but they absorb punishment "
            "that would drop three humans and keep swinging."
        ),
        "mage": (
            "A Lizardman Mage is a rare specimen — the cold blood that makes them such "
            "effective warriors also slows the intuitive leaps that magic demands. "
            "Those who persist become methodical, devastating casters."
        ),
        "thief": (
            "The Lizardman Thief relies less on social grace and more on the simple fact "
            "that no one expects something that large to move silently. They do. "
            "It remains deeply unfair."
        ),
        "druid": (
            "The Lizardman Druid speaks for the marshes, the swamps, and the places where "
            "water and earth blur together. They carry an ancient patience that even the "
            "oldest oaks acknowledge."
        ),
        "priest": (
            "The Lizardman Priest serves primordial powers older than human gods. Their "
            "faith is expressed through endurance and ritual, not oratory. The scars on "
            "their scales are their scripture."
        ),
        "warlock": (
            "The Lizardman Warlock's patron chose well — cold-blooded patience makes them "
            "immune to the emotional torment most pacts use as leverage. They honor their "
            "bargains with reptilian exactness."
        ),
        "gypsy": (
            "The Lizardman Gypsy is an improbable success story. They compensate for "
            "limited social instinct with an almost supernatural ability to read body "
            "language — a skill born in predator country."
        ),
        "mystic": (
            "The Lizardman Mystic found the Way through stillness — motionless for hours "
            "in shallow water, feeling the current rather than fighting it. Their Kai "
            "flows like a river: patient, inevitable, and dangerous when it floods."
        ),
    },
    "minotaur": {
        "warrior": (
            "The Minotaur Warrior was made for this. Horns lowered, hooves churning, "
            "they hit the front line like a siege engine and keep going. Enemies who see "
            "one charging tend to find elsewhere to be."
        ),
        "mage": (
            "A Minotaur Mage is an act of sheer willpower over instinct. The rage wants "
            "to close distance; the craft demands patience. Those who master both are "
            "extraordinary in ways that nothing in the spellbooks prepared anyone for."
        ),
        "thief": (
            "The Minotaur Thief is not subtle. What they lack in grace they compensate "
            "with a terrifying charge — most witnesses are too busy fleeing to remember "
            "what was taken."
        ),
        "druid": (
            "The Minotaur Druid carries a memory of open plains in their blood, a time "
            "before labyrinths and curses. They commune with the wild from grief as much "
            "as reverence, tending what was lost."
        ),
        "priest": (
            "The Minotaur Priest serves their god with the same unstoppable devotion they "
            "bring to everything. They are not subtle theologians — their faith is a "
            "battering ram, and they are comfortable with that."
        ),
        "warlock": (
            "The Minotaur Warlock's patron wanted raw power and got exactly that. The pact "
            "amplifies what was already there — a force of nature that now also casts "
            "spells, which is arguably everyone else's problem."
        ),
        "gypsy": (
            "The Minotaur Gypsy learned charm as a survival skill — it's either that or "
            "clear the room every time you walk in. They became genuinely good at it, "
            "which surprises no one more than themselves."
        ),
        "mystic": (
            "The Minotaur Mystic found the Way through conflict — learning to hold the "
            "charge without releasing it, to let the power build to a point of perfection "
            "rather than explosion. A difficult practice. A terrifying result."
        ),
    },
    "ogre": {
        "warrior": (
            "The Ogre Warrior is what happens when you run out of siege weapons. Thick "
            "hide, massive frame, and an indifference to pain that borders on supernatural. "
            "They don't need tactics — they need a direction to walk toward."
        ),
        "mage": (
            "The Ogre Mage is a legend told to discourage complacency. One in ten thousand "
            "ogres has the patience for it. Those who do are catastrophically dangerous — "
            "brute force combined with arcane amplification."
        ),
        "thief": (
            "The Ogre Thief practices a school of theft best described as 'take it and dare "
            "someone to object.' They are not wrong about the math. Subtlety is what "
            "smaller people fall back on when force isn't available."
        ),
        "druid": (
            "The Ogre Druid is closer to a force of nature than most druids dare admit. "
            "They don't negotiate with the wild — they join it, becoming one of the "
            "largest and most unpredictable things in it."
        ),
        "priest": (
            "The Ogre Priest's god is either very brave or very patient. Their devotion is "
            "absolute and their methods are blunt. Temple walls creak when they pray. "
            "Miracles tend to be structural events."
        ),
        "warlock": (
            "The Ogre Warlock's patron made a miscalculation — they expected fear as the "
            "leverage point. Ogres don't frighten easily. The pact remains, binding on "
            "both sides, and the patron has learned to work with what it has."
        ),
        "gypsy": (
            "The Ogre Gypsy relies on a simple truth: mark-up your prices enough and the "
            "customer decides buying is safer than negotiating. They have never lost a "
            "bargaining session. They have no idea why."
        ),
        "mystic": (
            "The Ogre Mystic bends the Way through raw mass. Their Kai techniques are "
            "slow, deliberate, and hit like a falling boulder. They are not graceful. "
            "They do not need to be."
        ),
    },
    "troll": {
        "warrior": (
            "The Troll Warrior is a nightmare to fight: hit them hard enough to stop them "
            "and they start healing. They have outlasted opponents who should have won "
            "by simple arithmetic, which they find philosophically interesting."
        ),
        "mage": (
            "The Troll Mage heals from the burns and cuts that focus-work inflicts on "
            "imperfect practitioners. This makes them uniquely resilient to the "
            "self-inflicted hazards of serious arcane research."
        ),
        "thief": (
            "The Troll Thief has the patience of something that regenerates — they can "
            "afford to wait. Traps that would discourage others are merely setbacks. "
            "Eventually, they get what they came for."
        ),
        "druid": (
            "The Troll Druid embodies the most ancient quality of the wild: persistence. "
            "They do not hurry. They do not give up. The forest respects what refuses "
            "to stop growing back."
        ),
        "priest": (
            "The Troll Priest sees their regeneration as proof of divine favor and takes "
            "this as license to throw themselves into danger on behalf of the faithful. "
            "Their god has not discouraged this interpretation."
        ),
        "warlock": (
            "The Troll Warlock's pact is unusually balanced — they offer the patron "
            "longevity and patience in exchange for power. A troll that regenerates and "
            "casts spells is a contract that works out for everyone. Except enemies."
        ),
        "gypsy": (
            "The Troll Gypsy never permanently loses anything — including their shirt. "
            "Bad trades, failed swindles, and escaped marks are all temporary setbacks "
            "to something that will still be operating in a century."
        ),
        "mystic": (
            "The Troll Mystic found enlightenment in endurance. The Way is not a peak "
            "to be reached but a process to be sustained. They sustain it longer than "
            "almost anyone else, because they can afford the time."
        ),
    },
    "centaur": {
        "warrior": (
            "The Centaur Warrior is speed and force unified. Their charge covers ground "
            "faster than most fighters can react to, and when they arrive, the impact "
            "is considerable. Getting away from them is its own problem."
        ),
        "mage": (
            "The Centaur Mage carries their library in saddlebags and has a reputation "
            "for appearing suddenly at critical moments. The ability to cover ground "
            "fast has practical applications in arcane research too."
        ),
        "thief": (
            "The Centaur Thief excels at the smash-and-sprint model — hit a target, "
            "collect the goods, and be gone before the dust settles. Their escape "
            "success rate is legendary and deeply frustrating to guards."
        ),
        "druid": (
            "The Centaur Druid is the plains incarnate — wind, grass, open sky, and "
            "the rhythm of hooves. They range farther than any other druid, seeing "
            "the health of whole regions in a single long circuit."
        ),
        "priest": (
            "The Centaur Priest travels from settlement to settlement, carrying their "
            "god's word faster than any mounted messenger could follow. They see their "
            "range as their divine mandate."
        ),
        "warlock": (
            "The Centaur Warlock signed the pact on the move — literally. Their patron "
            "appeared on a long ride, and the deal was struck at a canter. They bring "
            "the same energy to everything that follows."
        ),
        "gypsy": (
            "The Centaur Gypsy covers more ground than any other entertainer or trader "
            "and knows every crossroads market between here and the horizon. Their "
            "network of contacts is vast simply because they never stop moving."
        ),
        "mystic": (
            "The Centaur Mystic meditates at a gallop — the rhythm of hooves on earth "
            "is their mantra, motion their stillness. Their Kai flows with a momentum "
            "that is unique among practitioners of the Way."
        ),
    },
    "vampire": {
        "warrior": (
            "The Vampire Warrior fights with centuries of learned technique and the "
            "unsettling advantage of healing from every wound they inflict. Their "
            "opponents tire. They do not."
        ),
        "mage": (
            "The Vampire Mage has had lifetimes to study — literal lifetimes, not "
            "the metaphorical kind. They remember spells that were lost before current "
            "civilizations were founded, and they are not inclined to share."
        ),
        "thief": (
            "The Vampire Thief is the reason locked doors were invented. They move "
            "without sound through places that should not permit entry, take what they "
            "want, and leave nothing behind except an uneasy feeling."
        ),
        "druid": (
            "The Vampire Druid is a paradox — nominally undead, yet drawn to the life "
            "force flowing through forests and rivers. They tend what they can no longer "
            "fully be, which gives them an intensity that living druids lack."
        ),
        "priest": (
            "The Vampire Priest is a creature of uncomfortable theological complexity. "
            "The divine power flows — that cannot be denied. What the god thinks of "
            "their servant's condition is a question the priest avoids examining closely."
        ),
        "warlock": (
            "The Vampire Warlock made a second pact on top of the original one that "
            "made them what they are. Whatever they paid, they clearly got value — "
            "their power exceeds what either contract should have granted."
        ),
        "gypsy": (
            "The Vampire Gypsy has the ultimate long con: charm that literally takes "
            "the will out of a target, and centuries of practice reading what people "
            "want. They have swindled whole dynasties and outlived all witnesses."
        ),
        "mystic": (
            "The Vampire Mystic channels Kai through the paradox of unliving life — "
            "technically dead, yet burning with power. The Way does not distinguish. "
            "The force that flows is real, whatever vessel carries it."
        ),
    },
}


def get_combo_description(race_key, class_key):
    """Return lore blurb for race+class combo, or generic fallback."""
    race_key = (race_key or "human").lower().strip()
    class_key = (class_key or "warrior").lower().strip()
    race_data = RACE_CLASS_DESCRIPTIONS.get(race_key, {})
    return race_data.get(class_key, "An adventurer of uncertain origin.")
