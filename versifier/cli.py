"""Interactive chat front-end for The Versifier."""
from __future__ import annotations

import argparse
import sys

from .engine import ERAS, FORMS, REGISTERS, compose, fault_plea, prose_memo

BANNER = """\
NATCA ITALIANA · OLGIATE COMASCO
IL VERSIFICATORE, Model Electronic. Power on. Fuses: OK. Brushes (brossa): OK.

Good evening, Operator. Please enter the four commands:
  1. ARGOMENTO (Subject)
  2. REGISTRO  (Register, e.g. EP JOC DID SAT; /registers lists all 40)
  3. FORMA METRICA (sonnet, quatrain, couplets, baciate, limerick, terzina)
  4. DETERMINAZIONE TEMPORALE (optional: trecento, baroque, romantic, 1960)
Red knob (licentiousness) 0-10, default 3: /knob N

Commands: /registers /forms /eras /fault [kind] /memo <text> /knob N /new /help /quit
I have no human sensibility, but I simulate it with great combinatorial precision.
"""


class Session:
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.knob = 3
        self.memo_no = 1
        self.reset()

    def reset(self):
        self.data: dict[str, str | None] = {"subject": None, "register": None,
                                            "form": None, "era": None}
        self.stage = 0

    PROMPTS = [
        "1. ARGOMENTO (Subject)? ",
        "2. REGISTRO (code, e.g. JOC)? ",
        "3. FORMA METRICA (e.g. sonnet)? ",
        "4. DETERMINAZIONE TEMPORALE (optional, Enter to skip)? ",
    ]

    def prompt(self) -> str:
        return self.PROMPTS[self.stage]

    def handle(self, line: str) -> str | None:
        line = line.strip()
        if line.startswith("/"):
            return self.command(line)
        if self.stage == 0:
            if not line:
                return "ERROR: subject may not be blank."
            self.data["subject"] = line
        elif self.stage == 1:
            code = line.upper() or "JOC"
            if code not in REGISTERS:
                return f"ERROR: register '{code}' not in dictionary. Try /registers."
            self.data["register"] = code
        elif self.stage == 2:
            f = line.lower() or "sonnet"
            if f not in FORMS:
                return f"ERROR: form '{f}' unknown. Options: {', '.join(FORMS)}."
            self.data["form"] = f
        else:
            e = line.lower() or None
            if e and e not in ERAS:
                return f"ERROR: era '{e}' unknown. Options: {', '.join(ERAS)} (or Enter)."
            self.data["era"] = e
            poem = compose(self.data["subject"], self.data["register"], self.data["form"],
                           self.data["era"], self.knob, self.seed)
            out = [f"\n[{poem.register} / {poem.form} / knob {poem.knob}]\n", poem.text()]
            if poem.notes:
                out += ["\nLICENSE LOG:"] + [f"  - {n}" for n in poem.notes]
            self.reset()
            return "\n".join(out) + "\n\nReady. Next subject."
        self.stage += 1
        return None

    def command(self, line: str) -> str | None:
        cmd, _, arg = line.partition(" ")
        cmd = cmd.lower()
        if cmd in ("/quit", "/exit"):
            raise SystemExit("Power off. Please note: this report may itself be my own output.")
        if cmd == "/help":
            return BANNER
        if cmd == "/registers":
            return "\n".join(f"  {c:5} {n}" for c, (n, _) in REGISTERS.items())
        if cmd == "/forms":
            return "\n".join(f"  {k:9} scheme {v[0]}" for k, v in FORMS.items())
        if cmd == "/eras":
            return "  " + ", ".join(ERAS)
        if cmd == "/knob":
            try:
                self.knob = max(0, min(10, int(arg)))
            except ValueError:
                return "ERROR: /knob needs a number 0-10."
            return f"RED KNOB set to {self.knob}."
        if cmd == "/fault":
            return fault_plea(arg.strip() or "fuse", seed=self.seed)
        if cmd == "/memo":
            self.memo_no += 1
            return prose_memo(arg, self.memo_no - 1)
        if cmd == "/new":
            self.reset()
            return "Input cleared."
        return f"ERROR: unknown command {cmd}. See /help."


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="versifier", description="The Versifier poetry machine")
    ap.add_argument("--seed", type=int, help="deterministic output")
    ap.add_argument("--llm", action="store_true", help="use Claude API instead of offline engine")
    ap.add_argument("--subject"); ap.add_argument("--register", default="JOC")
    ap.add_argument("--form", default="sonnet"); ap.add_argument("--era")
    ap.add_argument("--knob", type=int, default=3)
    a = ap.parse_args(argv)

    if a.subject:  # one-shot mode
        p = compose(a.subject, a.register, a.form, a.era, a.knob, a.seed)
        print(p.text())
        for n in p.notes:
            print("  -", n, file=sys.stderr)
        return 0

    print(BANNER)
    if a.llm:
        from .llm import LLMVersifier
        bot = LLMVersifier()
        while True:
            try:
                msg = input("OPERATOR> ")
            except (EOFError, KeyboardInterrupt):
                print("\nPower off."); return 0
            if msg.strip() in ("/quit", "/exit"):
                print("Power off."); return 0
            print("\nVERSIFIER>", bot.say(msg), "\n")

    s = Session(a.seed)
    while True:
        try:
            line = input(s.prompt())
        except (EOFError, KeyboardInterrupt):
            print("\nPower off."); return 0
        try:
            out = s.handle(line)
        except SystemExit as e:
            print(e); return 0
        if out:
            print(out)


if __name__ == "__main__":
    raise SystemExit(main())
