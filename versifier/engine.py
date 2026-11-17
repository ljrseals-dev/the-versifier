"""Combinatorial poetry engine for The Versifier (Il Versificatore).

Pure standard library. Deterministic when given a seed.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- syllables


def syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(n, 1)


def line_syllables(line: str) -> int:
    return sum(syllables(w) for w in line.split())


# ---------------------------------------------------------------- lexicon

RHYME_FAMILIES = {
    "ight": ["night", "light", "sight", "flight", "white", "tight"],
    "eart": ["heart", "part", "art", "start", "apart"],
    "ire": ["fire", "wire", "desire", "choir", "entire"],
    "ee": ["sea", "free", "key", "tree", "me"],
    "ay": ["day", "way", "say", "gray", "stay"],
    "one": ["stone", "alone", "tone", "known", "bone"],
    "ain": ["rain", "pain", "chain", "gain", "brain"],
    "ime": ["time", "rhyme", "climb", "prime", "chime"],
    "eel": ["steel", "feel", "wheel", "real", "reel"],
    "ow": ["glow", "slow", "flow", "below", "know"],
    "ore": ["more", "door", "floor", "core", "store"],
    "old": ["gold", "cold", "old", "hold", "fold"],
}

FIELDS = {
    "love": dict(
        keys=["love", "girl", "woman", "kiss", "bed", "heart", "bride", "lover"],
        nouns=["kiss", "glance", "promise", "ribbon", "sigh", "doorway"],
        adjs=["tender", "trembling", "sweet", "secret", "rosy"],
        verbs=["adore", "embrace", "forgive", "remember", "desire"],
        fams=["eart", "ire", "ee", "ow"],
    ),
    "machine": dict(
        keys=["machine", "robot", "factory", "engine", "computer", "gear", "poet"],
        nouns=["gear", "relay", "valve", "circuit", "piston", "dial"],
        adjs=["tireless", "metallic", "humming", "exact", "oiled"],
        verbs=["compute", "rotate", "calibrate", "assemble", "obey"],
        fams=["eel", "ire", "old", "ore"],
    ),
    "sea": dict(
        keys=["sea", "ocean", "ship", "wave", "river", "water", "storm"],
        nouns=["wave", "harbor", "sail", "tide", "shore", "mast"],
        adjs=["salty", "restless", "vast", "foaming", "distant"],
        verbs=["drift", "wander", "surge", "sail", "mourn"],
        fams=["ee", "ain", "ow", "one"],
    ),
    "night": dict(
        keys=["night", "moon", "dark", "star", "dream", "sleep", "death"],
        nouns=["shadow", "lantern", "moon", "dream", "vigil", "owl"],
        adjs=["silent", "pale", "hollow", "starry", "weary"],
        verbs=["whisper", "linger", "fade", "keep", "wake"],
        fams=["ight", "one", "ay", "ain"],
    ),
    "money": dict(
        keys=["money", "bank", "invoice", "payroll", "tax", "deadline", "debt", "price"],
        nouns=["ledger", "coin", "invoice", "deadline", "account", "sum"],
        adjs=["solvent", "punctual", "gilded", "weary", "frugal"],
        verbs=["settle", "balance", "defer", "invest", "tally"],
        fams=["old", "ime", "ore", "ay"],
    ),
    "generic": dict(
        keys=[],
        nouns=["memory", "window", "garden", "river", "letter", "bridge"],
        adjs=["quiet", "ancient", "golden", "restless", "gentle"],
        verbs=["remember", "wander", "begin", "endure", "resolve"],
        fams=list(RHYME_FAMILIES),
    ),
}

# 8 tone vocabularies; the 40 registers are mapped onto them.
TONES = {
    "elegiac": ["mournful", "faded", "lost", "fallen", "grieving"],
    "jocular": ["silly", "plump", "wobbly", "cheeky", "ridiculous"],
    "didactic": ["proper", "careful", "measured", "useful", "orderly"],
    "satirical": ["pompous", "bloated", "smug", "vain", "gilded"],
    "heroic": ["mighty", "valiant", "immortal", "blazing", "noble"],
    "pastoral": ["green", "dewy", "shepherd's", "mellow", "sunlit"],
    "mystic": ["veiled", "radiant", "ineffable", "holy", "dim"],
    "bureaucratic": ["duplicate", "stamped", "pending", "official", "filed"],
}

REGISTERS = {
    code: (name, tone)
    for code, name, tone in [
        ("EP", "Elegiac", "elegiac"), ("JOC", "Jocular", "jocular"),
        ("DID", "Didactic", "didactic"), ("SAT", "Satirical", "satirical"),
        ("PORN", "Explicit (withdrawn)", "jocular"), ("EROI", "Heroic", "heroic"),
        ("BUC", "Bucolic", "pastoral"), ("MIS", "Mystical", "mystic"),
        ("BUR", "Bureaucratic", "bureaucratic"), ("LIR", "Lyrical", "pastoral"),
        ("ODE", "Odic", "heroic"), ("NOS", "Nostalgic", "elegiac"),
        ("MAL", "Melancholic", "elegiac"), ("EPI", "Epigrammatic", "satirical"),
        ("FUN", "Funereal", "elegiac"), ("NUZ", "Nuptial", "pastoral"),
        ("MAR", "Martial", "heroic"), ("REL", "Religious", "mystic"),
        ("COM", "Commercial", "bureaucratic"), ("ARC", "Arcadian", "pastoral"),
        ("IRO", "Ironic", "satirical"), ("BUF", "Burlesque", "jocular"),
        ("EPO", "Epic", "heroic"), ("ELE", "Eclogue", "pastoral"),
        ("MON", "Monastic", "mystic"), ("LEG", "Legal", "bureaucratic"),
        ("NON", "Nonsense", "jocular"), ("PAT", "Patriotic", "heroic"),
        ("PAN", "Panegyric", "heroic"), ("INV", "Invective", "satirical"),
        ("CRO", "Chronicle", "didactic"), ("GNO", "Gnomic", "didactic"),
        ("SCI", "Scientific", "didactic"), ("DEV", "Devotional", "mystic"),
        ("FAM", "Familiar", "jocular"), ("AMO", "Amorous", "pastoral"),
        ("TEC", "Technical", "bureaucratic"), ("NAT", "Birthday (Natalizio)", "jocular"),
        ("LUT", "Mourning", "elegiac"), ("SAC", "Sacred", "mystic"),
    ]
}

ERAS = {
    "trecento": {r"\bYour\b": "Thy", r"\byour\b": "thy", r"\bcan\b": "may"},
    "baroque": {r"\bYour\b": "Thine", r"\byour\b": "thine", r"\bcan\b": "doth"},
    "romantic": {r"\bYour\b": "Thy", r"\byour\b": "thy", r"\bmy\b": "mine own"},
    "1960": {},
}

JARGON = ["brossa", "bakelite", "cast iron", "bobbin", "solenoid", "brass bushing"]

FORMS = {
    "sonnet": ("ABABCDCDEFEFGG", 10),
    "quatrain": ("ABAB", 10),
    "couplets": ("AABBCCDD", 8),
    "baciate": ("AABBCC", 8),
    "limerick": ("AABBA", 8),
    "terzina": ("ABABCBCDC", 10),
}

TEMPLATES = [
    "The {a} {n} of {S} can never {v} {R}",
    "I sing of {S}, so {a} and {a2}, to {R}",
    "Your {a} {n} remembers every {R}",
    "What {a} {n} could ever {v} the {R}",
    "{S} is a {a} {n}, a {a2} {R}",
    "Behold the {a} {n}, and then the {R}",
    "O {a} {S}, my {n}, my {R}",
    "No {n} will {v} the {a} {R}",
]

# ---------------------------------------------------------------- helpers


def pick_field(subject: str) -> str:
    s = subject.lower()
    for name, spec in FIELDS.items():
        if any(k in s for k in spec["keys"]):
            return name
    return "generic"


def coin(word: str, rng: random.Random) -> str:
    """License: coin a neologism by bending the ending."""
    suffix = rng.choice(["air", "ero", "ine", "ish", "are"])
    return word[:-1] + suffix if len(word) > 3 else word + suffix


_ONES = ("zero one two three four five six seven eight nine ten eleven twelve "
         "thirteen fourteen fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def number_words(n: int) -> str:
    """Spell 0..9999 the way the machine does: run together, no spaces."""
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + (_ONES[n % 10] if n % 10 else "")
    if n < 1000:
        rest = n % 100
        return _ONES[n // 100] + "hundred" + ("and" + number_words(rest) if rest else "")
    rest = n % 1000
    out = _ONES[n // 1000] + "thousand"
    if rest:
        out += number_words(rest) if rest >= 100 else "and" + number_words(rest)
    return out


# ---------------------------------------------------------------- poem


@dataclass
class Poem:
    lines: list[str]
    subject: str
    register: str
    form: str
    era: str | None
    knob: int
    notes: list[str] = field(default_factory=list)

    def text(self) -> str:
        return "\n".join(self.lines)


def compose(subject: str, register: str = "JOC", form: str = "sonnet",
            era: str | None = None, knob: int = 3, seed: int | None = None) -> Poem:
    rng = random.Random(seed)
    register = register.upper()
    form = form.lower()
    notes: list[str] = []
    if register not in REGISTERS:
        raise ValueError(f"Unknown register '{register}'. See /registers.")
    if form not in FORMS:
        raise ValueError(f"Unknown form '{form}'. Options: {', '.join(FORMS)}")
    knob = max(0, min(10, int(knob)))
    if register == "PORN":
        notes.append("REGISTER PORN withdrawn by NATCA legal department; substituting JOC.")
    scheme, target = FORMS[form]
    f = FIELDS[pick_field(subject)]
    tone = TONES[REGISTERS[register][1]]
    subj = subject.strip() or "nothing"

    pool = f["fams"][:] + [k for k in RHYME_FAMILIES if k not in f["fams"]]
    fam_for: dict[str, str] = {}
    for letter in dict.fromkeys(scheme):
        fam_for[letter] = pool[len(fam_for) % len(pool)]
    used: dict[str, list[str]] = {k: [] for k in fam_for}

    lines: list[str] = []
    for i, letter in enumerate(scheme):
        fam = RHYME_FAMILIES[fam_for[letter]]
        free = [w for w in fam if w not in used[letter]]
        if free:
            rhyme = rng.choice(free)
        else:
            rhyme = coin(rng.choice(fam), rng)
            notes.append(f"Line {i + 1}: rhyme exhausted; LICENSE invoked -> '{rhyme}'.")
        used[letter].append(rhyme)

        best, best_gap, best_notes = "", 99, []
        for _ in range(12):
            local: list[str] = []
            tpl = rng.choice(TEMPLATES)
            noun = rng.choice(f["nouns"])
            if rng.random() < 0.04 + knob * 0.012:
                noun = rng.choice(JARGON)
                local.append(f"Line {i + 1}: workshop jargon '{noun}' inserted.")
            verb = rng.choice(f["verbs"])
            if knob and rng.random() < knob * 0.03:
                old, verb = verb, coin(verb, rng)
                local.append(f"Line {i + 1}: '{old}' bent to '{verb}' (license).")
            cand = tpl.format(S=subj, n=noun, v=verb, R=rhyme,
                              a=rng.choice(tone), a2=rng.choice(tone + f["adjs"]))
            gap = abs(line_syllables(cand) - target)
            if gap < best_gap:
                best, best_gap, best_notes = cand, gap, local
        notes.extend(best_notes)
        lines.append(best[0].upper() + best[1:] + ("." if i == len(scheme) - 1 else ","))

    if era and era.lower() in ERAS:
        for pat, rep in ERAS[era.lower()].items():
            lines = [re.sub(pat, rep, ln) for ln in lines]
    return Poem(lines, subj, register, form, era, knob, notes)


# ---------------------------------------------------------------- faults & prose

FAULTS = {
    "fuse": "Fuse number {n} has blown",
    "jam": "Carriage jammed at position {n}",
    "brossa": "Brush assembly {n} worn through",
}

PLEAS = [
    "Change the fuses with this serial numbair —\n{words}are",
    "O Operator, hear my humming plea:\nPart {words} must be replaced for me",
    "The relay clicks, the current will not stay;\nInstall part {words} without delay",
]


def fault_plea(kind: str = "fuse", serial: int | None = None, seed: int | None = None) -> str:
    rng = random.Random(seed)
    serial = serial if serial is not None else rng.randint(1000, 9999)
    words = number_words(serial).capitalize()
    plea = rng.choice(PLEAS).format(words=words)
    head = FAULTS.get(kind, FAULTS["fuse"]).format(n=serial)
    return f"** DIAGNOSTIC: {head}. Composing plea in selected metre. **\n{plea}"


def prose_memo(text: str, number: int = 1) -> str:
    body = " ".join(text.split()) or "no subject supplied"
    return (f"NATCA ITALIANA - OLGIATE COMASCO\nMEMORANDUM No. {number:04d}\n"
            f"Re: {body}\n\nThe undersigned machine confirms receipt of the above and "
            f"will process it with impeccable efficiency. Deadlines noted. Payroll unaffected.\n\n"
            f"Respectfully,\nIL VERSIFICATORE")
