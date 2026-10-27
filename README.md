# paper-anatomy

A [Claude Code](https://claude.com/claude-code) skill that turns an AI paper into a structured reading note. **Notes are written in Chinese**, with technical terms kept in English.

Each note has three parts:

1. **地基 (foundation)**: the 3–8 concepts you need before the paper makes sense.
2. **骨干 (backbone)**: the paper's logical tree (task, the 2–3 prior works that give the method its frame and the one change its result rests on, challenges, key insight, pipeline, contributions with evidence, results). Every node cites its location in the paper.
3. **领域知识卡 (field card)**: challenges, solutions and failure cases stated about the field, each tagged as stated by the paper or inferred, with testable failure hypotheses.

Up to three key figures (teaser, method overview, a result figure) are embedded where they belong, each with a one-line reading hint.

## Install

```bash
git clone https://github.com/frickyinn/paper-anatomy ~/paper-anatomy
ln -s ~/paper-anatomy ~/.claude/skills/paper-anatomy
```

Requires `python3` and `curl`. The scripts use only the standard library.

## Use

```bash
cd ~/my-paper-vault
claude
> /paper-anatomy 2502.19645
> /paper-anatomy https://arxiv.org/abs/2502.19645 --out ~/vaults/vla
```

Notes go into a **vault**: the current directory, or `--out <dir>`. A vault is marked by an empty `.paper-anatomy` file; the first run in an unmarked directory asks before creating one. Layout:

```
vault/
  .paper-anatomy
  2502.19645-openvla-oft.md      # the note, one per paper
  assets/2502.19645/figs/        # embedded figures
  assets/2502.19645/src/         # fetched full text
```

Re-running a paper asks before overwriting its note and reuses what is already in `assets/`. The vault works as an Obsidian folder.

## Files

- `SKILL.md`: the instructions the agent follows.
- `fetch_arxiv.py`: flattens an arXiv HTML paper to text, with math as TeX and figures as `[image: URL]`.
- `check_math.py`: flags math written outside `$...$` in a note.

Both scripts have a `--selftest`.

## License

MIT
