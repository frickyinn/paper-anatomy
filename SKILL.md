---
name: paper-anatomy
description: Digest an AI paper into a Chinese reading note — foundation concepts first, then the paper's backbone tree, then a field card of challenges, solutions and failure-case hypotheses. Use when the user gives an arXiv ID/URL or a PDF and asks to read, summarize, or explain the paper.
---

# paper-anatomy

Reading a paper has two stages. First the reader needs the **地基** (foundation): the concepts the paper stands on. Only then can they follow the **增量** (delta): what this paper adds to its field. The note serves both stages in that order, then distills what the reader came for: the field's challenges and solutions.

The reader is an AI graduate student who knows deep learning fundamentals. The note is Chinese prose; technical terms keep their English form, with a Chinese gloss on first use.

Math is TeX inside delimiters, always: every symbol, subscript, Greek letter, operator and formula, even a lone variable in prose or a model name like $\pi_{0.6}$. Inline math is `$\gamma^{t}$`, with no space just inside either `$`. A formula worth its own line is a display block, with `$$` on separate lines:

```
$$
\hat{Q} = \sum_{t'=1}^{C} \gamma^{t'-1} r_{t'}
$$
```

Arguments: $ARGUMENTS (`<arXiv ID, URL or PDF path> [--out <dir>]`)

`<skill>` below is this skill's base directory, shown when the skill loads. `<id>` is the arXiv ID, or the local PDF's basename.

## Steps

### 0. Resolve the vault

The vault is the `--out` directory when given, else the current working directory. A vault has an empty `.paper-anatomy` marker file at its root; check that directory only, never its parents.

- Marker present: continue.
- Marker absent, or the directory does not exist: ask the user 「在 <absolute path> 新建 paper vault？」. On yes, `mkdir -p <vault> && touch <vault>/.paper-anatomy`; on no, stop.

Then, if `<vault>/<id>-*.md` already exists, ask the user whether to overwrite it; on no, stop.

Done when the vault holds the marker and any overwrite is approved.

### 1. Get the full text

- **arXiv ID or URL**: `mkdir -p <vault>/assets/<id>/src && python3 -I <skill>/fetch_arxiv.py <id> <vault>/assets/<id>/src`. It writes the paper as plain text (math as `$TeX$`, tables as `| cell |` rows, figures as `[image: URL]`) and prints the path; when `<id>.txt` is already there, read it instead of fetching again. Exit code 2 means arXiv has no HTML version: `curl -sL -o <vault>/assets/<id>/src/<id>.pdf https://arxiv.org/pdf/<id>` and read the PDF instead.
- **Local PDF**: read it directly, 20 pages per Read call.

Read the main text end to end, including every table. Read the appendix where a claim needs its evidence.

Then choose up to 3 figures by role. Each `[image: URL]` line is followed by its `Fig. N:` caption, which tells you what the figure shows:

- **teaser**: what the task or the result looks like, usually Fig. 1.
- **overview**: the method pipeline or system architecture.
- **result**: evidence for one Contribution or Finding that no table carries.

A role with no fitting figure stays empty. Download every image of a chosen figure to `<vault>/assets/<id>/figs/fig<N>.<ext>`, with subfigure panels as `fig<N>a`, `fig<N>b`, … (`mkdir -p <vault>/assets/<id>/figs && curl -sL -o <vault>/assets/<id>/figs/fig<N>.<ext> <URL>`), skipping files already there, and Read each image.

Done when you have read every section of the main text and seen every chosen figure.

### 2. Classify the paper

Pick the dominant type; it selects the backbone tree in step 3.

- **方法类**: proposes a new method, model, or system.
- **Benchmark/数据集类**: its main product is an evaluation or a dataset.
- **分析类**: its main product is findings about existing methods.

A mixed paper takes the tree of its dominant type; its secondary product becomes one Contribution or Finding.

### 3. Extract the backbone

Build the tree for the paper's type from the templates below. Organise it by logical role, not by section order: abstract, introduction and method restate the same nodes at increasing detail, so merge them into one node and cite the most specific location.

Every node carries its **出处** (location) in parentheses: `(§3.2)`, `(Table 2)`, `(Fig. 3)`, `(Eq. 4)`. Write `论文未说明` when the paper is silent. An empty node is better than an invented one.

**方法类**

```
- **Task**：输入 … → 输出 …；应用场景 …
- **Challenge 1**：<一句话>
  - 旧方法：<代表方法>
  - 失败情况：<在什么情况下失败>
  - 技术原因：<为什么会失败>
- **Challenge 2** …
- **Key insight**：<一句话，可迁移的高层思想，区别于具体技术贡献>
- **Pipeline**：第一步 … → 第二步 … → 第三步 …
- **Contribution 1**：<名称>
  - 解决：Challenge <n>
  - 做法：…
  - 为什么 work：…
  - 证据：<哪个对比或消融支持它，带数字>；没有实验单独验证它时写「无直接证据」
- **Contribution 2** …
- **Results**：<主对比实验的结论，带关键数字>
- **Limitations**：见「三、Failure cases」
```

**Benchmark/数据集类**

```
- **Target**：要评测或支撑的能力
- **Gap 1**：<一句话>
  - 现有评测：…
  - 缺什么：…
  - 为什么重要：…
- **Key insight**：<设计原则>
- **Construction**：数据来源 / 标注方式 / 指标 / 质量控制
- **Finding 1**：<发现>
  - 证据：…
- **Finding 2** …
```

**分析类**

```
- **Question**：<要回答的问题>
- **Why it matters**：<领域原有的默认看法，以及答案会改变什么>
- **Setup**：模型 / 数据 / 控制变量
- **Finding 1**：<结论>
  - 证据：…
  - 适用边界：…
- **Finding 2** …
- **Implications**：<对领域意味着什么>
```

A term the paper coins (its own module names, loss names, model names) is defined inside the backbone node where it first appears.

Done when every node has content or `论文未说明`, every node has an 出处, and every Contribution has its 解决 and 证据 lines.

### 4. Choose the foundation

With the backbone in hand, list the concepts a reader must already hold to follow it. A concept enters the **地基** only when both hold:

- It is beyond standard deep learning coursework. Transformer, attention, diffusion basics, fine-tuning, MDP and policy are the baseline; subfield machinery is not.
- Some backbone node becomes unreadable without it. The paper's preliminaries or background section is the usual source.

Keep 3–8 concepts. Terms the paper coins already live in the backbone. Order them so each builds only on concepts listed before it. For each concept write:

- 是什么：one-sentence definition
- 直觉：a concrete example, or the defining formula with its symbols explained

### 5. Write the field card

The field card is the reason the note exists: knowledge about the **field** that outlives this one paper. Phrase each item as a statement about the field, not a description of the paper ("长时程任务中稀疏奖励使 credit assignment 失效", not "论文指出 baseline 不行").

Tag every item `[论文]` when the paper states it, or `[推断]` when you infer it. Every `[推断]` names its **依据**, the paper location it rests on. An inference without an 依据 is left out.

- **Challenges**: open problems drawn from the motivation, the stated limitations, and the failure cases.
- **Solutions**: the method as a reusable technique, the key insight in a form applicable beyond this task, and the future directions the paper names.
- **Failure cases**:
  - `[论文]` the failure cases and limitations the paper admits, each with its 出处.
  - `[推断]` up to 3 **failure hypotheses**: predictions that can be tested, not verdicts. Each one has all four fields:

    ```
    1. [推断] 依赖前提：<方法依赖的假设>（依据：§…）
       可能失败的数据：<哪类数据会打破这个前提>
       预测的失败表现：<会怎样失败>
       验证实验：<用什么数据或设置测试>
    ```

    Good sources: a premise the method needs but never tests, an evaluation set narrower than the claim, weak or missing baselines, a claim broader than its table shows. Zero hypotheses is a valid outcome.

### 6. Write the TL;DR

One sentence stating the 增量. For a method paper: 在 <task> 上，针对 <challenge>，用 <insight>，做到 <result>. For other types, use the same shape: what was missing, what the paper supplies, and what it showed.

### 7. Write the note and check it

Write `<vault>/<id>-<slug>.md`. The slug is the method or model name, else 2–4 words of the title, lowercase and hyphenated: `2502.19645-openvla-oft.md`. Layout:

```
# <论文标题>

> arXiv:<id> · <类型> · 摘要于 <YYYY-MM-DD>

**TL;DR**：…

![teaser](assets/<id>/figs/fig1.png)
*（Fig. 1）<读图提示>*

## 一、地基
### 1. <Concept>（中文）
…
## 二、骨干
…
- **Pipeline**：…

  ![overview](assets/<id>/figs/fig2.png)
  *（Fig. 2）<读图提示>*
…
## 三、领域知识卡
### Challenges
### Solutions
### Failure cases
```

Each chosen figure sits at its slot: the teaser under the TL;DR, the overview inside the Pipeline node, a result figure inside the node whose 证据 it is, indented to that node. Image paths are relative to the note. Under each image, one italic 读图提示 line gives the Fig. number and says what to look at and which backbone node it maps to; the paper's caption stays in the paper.

Budget: 地基 about 25%, 骨干 about 45%, 知识卡 about 30%. `wc -m` on the note falls between 2500 and 6000. When over budget, cut detail inside nodes; every node stays.

Check the note against every line below and fix each miss:

- [ ] Every backbone node has an 出处 or `论文未说明`.
- [ ] Every Contribution names the Challenge it solves and its 证据.
- [ ] The 地基 has 3–8 concepts. None is coined by the paper and none is baseline knowledge.
- [ ] Every field-card item is tagged, and every `[推断]` names an 依据.
- [ ] There are at most 3 failure hypotheses, each with all four fields.
- [ ] Every chosen figure is embedded at its slot, its file exists under `<vault>/assets/<id>/figs/`, and a 读图提示 line follows it.
- [ ] `wc -m` is between 2500 and 6000.
- [ ] `python3 -I <skill>/check_math.py <note>` prints nothing.

Done when every box passes. Reply with the TL;DR and the note's path only.
