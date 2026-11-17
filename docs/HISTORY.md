# History

## The source

*Il versificatore* ("The Versifier") is a satirical science-fiction story by the Italian chemist and writer **Primo Levi** (1919-1987), written around 1960 and later collected in *Storie naturali* (1966, first published under the pseudonym Damiano Malabaila) and available in English in Levi's story collections (e.g. *The Sixth Day and Other Tales*; check your edition). A poet, pressed by deadlines, buys a desk machine that produces verse from a subject, a register, a metre and an era; he comes to depend on it for his accounts and correspondence too, and the story closes by hinting that the narrative itself may be the machine's output.

Levi trained as a chemist and worked in industry for decades. The story's affection for workshops, parts and jargon comes from that life.

> **Verify before you cite.** Publication details above are given from general knowledge. The project brief that started this repo described the work both as a "screenplay" and as a short story, and spelled the jargon word both *brossa* and *bosón*. This repo uses *brossa*. Check against the printed text before quoting any of it.

## Why a chatbot

Levi's machine anticipates several things now familiar from language models:

| In the story | In an LLM |
|---|---|
| Subject / register / metre / era entered by the operator | A structured prompt |
| Red knob for "licence" | Sampling temperature |
| Coined words to complete a rhyme | Hallucination / out-of-vocabulary generation |
| Workshop words leaking into poems | Training-data contamination |
| Poet dependent on the machine for correspondence and accounts | Task creep |
| Narration that may be machine output | Authorship ambiguity |

## Project changelog

### v1.0.0 (2026-11-16)
- Offline engine: 40 registers, 6 metric forms, 4 eras, 6 semantic fields, rhyme families, licence/coinage, jargon insertion.
- Interactive chat CLI with the four-command protocol and the red knob.
- Fault pleas with spelled-out serial numbers; prose-memo mode.
- Optional Claude-powered mode with a full system prompt.
- 20-test pytest suite, GitHub Actions CI, MIT licence.
- Logo, banner, sample card and architecture diagram.

### Design decisions
- **Zero runtime dependencies** for the offline mode so the machine "plugs in and works".
- **Seeded randomness** for reproducible output and tests.
- **Everything logged**: every licence or jargon intrusion is reported, so the operator can see where the machine bent the rules.
- **No source text copied**: all verse and prose is original.
