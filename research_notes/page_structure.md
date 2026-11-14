# The page: proposed outline, what changed, and where the next work goes

`interactive.html` is built by `build_interactive.py` (markup and JavaScript), `page_sections.py` (the tables computed from the scenarios) and
`page_scenarios.js` (the switches). This note records how the page is organised and why. Section 1 was written before the reorganisation; the
rest says what was done.

## 1. Proposed outline (written before the change)

### What is wrong with the page as it stood

1. **The answer is not on one screen.** The top of the page was a list of six findings, a long table of bottlenecks and a four-number chain; the
   cost was one number ("the floor") with two alternatives in a side panel. A reader could not see the range of outcomes or what each rests on.
2. **The market-share part is separated from its explanation.** The charts (share by type of meat, share of all meat, adoption over time) sit
   in one block; the reasoning that produced them (price ratio, shopper choice, regional markets, timing) is in the collapsed
   "How the model works" section, hundreds of lines below. Each chart's "how to read this" is a "?" badge.
3. **Charts are numbered in an order that is not the order of reasoning** (1 share by type, 2 share of all meat, 3 cost, 4a/4b shopper choice,
   5 adoption, 6 other products, 7 which products first), and the text refers to them by number.
4. **"What each cost case means" mixes four things in one list**: the tank's operating mode (fed-batch, perfusion, drained and refilled), the plant
   class (clean rooms or not), the cells (efficient or small and slow) and the density. A reader cannot tell which row differs from which in what.
5. **"How the tank is run" is one dropdown in the middle of an expert panel**, with jargon for its two options ("perfusion (cells held back)",
   "drained and refilled"), no picture of what each does, and a single bar in the tornado that bundles three effects: the density limit, the
   fraction of the cycle a tank is productive, and the retention device. It is not among the decisions a reader can compare with the others.
6. **The cells-by-tank grid** showed two figures per cell with no limit named and no sentence under it.
7. **The evidence is scattered**: the reality checks are an unlabelled panel under the charts, the back-test is only in the Python, "what would
   change the conclusions" and "what the model leaves out" are inside the collapsed method.

### The proposed order and why

0. Title, one-paragraph lede, the disclaimer, and a **jump bar** (Answer · What decides it · Cost build-up · Share · Evidence · Method) so a reader
   can find any part from any place on a phone.
1. **The answer** (`#answer`). The scenario table (cost, shop price, share, what must go right and what each needs), the words used, and a
   one-line chain for the scenario chosen. Why first: it is the finding, it is what everyone asks, and the rest of the page is "why".
2. **What decides it** (`#decide`). The ten switches, the live result, the ranked "what to prioritise" chart, two switches against each other,
   and the computed interactions. Why second: it turns the table into something the reader can change, and it is where the page's main new
   information is.
3. **How the cost is built up** (`#build`). The bottlenecks ("what stands in the way"), the cells-by-tank grid redone so each figure is
   readable, cost against medium price (the old chart 3, with the scenarios marked), a clearly separated **Vessel types and operating
   modes** subsection (`#vessels`), and the all-levers panel ("Build your own case") collapsed as an expert tool. Why: it is the engineering
   half of the chain, the cost side, kept together and ordered from "what limits" to "what to try" to "everything adjustable".
4. **From cost to market share** (`#share`), ordered as the chain of reasoning, each chart with its explanation directly under its title:
   the price ratio (the step-by-step calculation and the three headline numbers), how shoppers choose (share against price; why this share),
   share by type of meat and region, share of all meat, adoption over time, and the uncertainty band. Why: today the explanation of each
   step is in the collapsed method; it belongs next to the chart it explains. The assumption sliders stay beside it (the rail).
5. **Evidence and checks** (`#evidence`). Reality checks (what the model reproduces that it was not fitted to), the cross-check against
   other products, which products could go first, the back-test of the cost model against reported runs, what has and has not been
   measured, and the list of experiments that would move the result (lifted from the research notes). Why: a reader who doubts the answer
   goes here.
6. **Method and sources** (collapsed): the equations, the appendices, the references and "About this page", unchanged except that the
   cost steps now describe the scenarios.

Charts get plain titles without numbers; every textual reference to "chart 7" becomes "the which-products-first chart".

### Where vessel types and operating modes go

A later session will add other vessels (airlift, bubble column) and other operating modes (batch, fed-batch, chemostat). The page leaves a
section for them: **3.4 Vessel types and operating modes** (`#vessels`), with its own heading, a table of what the model computes today and
an explicit "not yet in the model" list. What can be fixed now is the clarity of the comparison: the old mixed list becomes a two-way
table, **operating mode** (perfusion; drained and refilled) against **plant class** (lean; sterile; pharma-style), computed for the chosen
scenario's cells, each cell naming the limit that binds. The "How the tank is run" dropdown stays in the all-levers panel but now says in
words what each option does. It is not made an eleventh switch, so that the later session decides how modes combine with vessels.

### Things deliberately not changed

Every chart that was on the page is kept; every figure on it is still computed from the model; the method section, appendices and references are
unchanged apart from cost wording and chart names; the page keeps working at phone width.

## 2. What was done

The page now runs in this order (each part has an id; the jump bar at the top links to them):

| part | id | contents |
|---|---|---|
| The answer | `#answer` | the scenario table (cost with its band, shop price, long-run share, what it needs, what limits the tank; the reference and the reported process as labelled rows; on a phone each row stacks), the words used, the one-line chain for the chosen scenario |
| What decides it | `#decide` | preset buttons; the live result strip; ten switches each with its tag and a one-line note; "what to prioritise" (ranked bars, change in cost and in share points); two switches against each other; the computed interactions |
| How the cost is built up | `#build` | what stands in the way (computed from the central scenario); cells against tank (each cell: cost in a sterile and a lean plant, density, the limit that binds, loads into the switches); cost against medium price; **Vessel types and operating modes** (`#vessels`); "All the levers" (the old Build your own case, collapsed, which starts from the chosen scenario and has a "Start from a scenario" control) |
| From cost to market share | `#share` | the assumption panel beside four steps in order: the price ratio (three headline numbers and the step-by-step calculation); how shoppers choose (share against price, why this share); the result for each kind of meat (share by type, share of all meat, the Monte Carlo toggle); how fast (adoption). Each step has its explanation under its title |
| Evidence and checks | `#evidence` | reality checks; other products and which products could go first; the cost model against reported runs (new on the page, from `floor_physics.backtest`); what has and has not been measured; the measurements that would move the answer, each priced from the switches (`page_sections.experiments`) |
| Method and sources | `#method` | collapsed, as before; the cost steps now describe the scenarios |

Chart titles lost their numbers; the text refers to charts by name. Every chart that was on the page is still there.

**Vessel types and operating modes (`#vessels`).** The old mixed list becomes a two-way table: operating mode (perfusion; drained and refilled) against plant class
(lean; sterile; pharma-style), for the chosen scenario's cells, each cell naming the limit that binds (perfusion $15.8 to $18.8 against $33 to $53
drained and refilled, in the central case). Below it is a dashed box, "Not yet in the model", naming what a later session will add: an airlift, a bubble column,
batch, fed-batch and chemostat. To add them: give `floor_physics.explore` the vessel and mode, add rows or columns to `page_sections.vessels()`, add a
switch to `scenarios.SWITCHES` (the page and the parity test read the switch list from `scenarios.js_model()`), and mirror the new physics in `floorExplore`.
`explore` still knows only perfusion and "anything else" (drained and refilled); `output_per_m3` has a fed-batch formula that `explore` does not use.

## 3. Differences from the proposal

- **"What would change the conclusions" and "What the model leaves out" stay in the collapsed method**, not in the evidence part. They are short method-level
  statements; what the evidence part needed was something a reader can act on, so it has a new table of measurements priced from the switches instead.
- **The cost-against-medium-price chart sits in "How the cost is built up"**, not in the share part: it is a cost chart, and it now marks the scenarios.
- **The Monte Carlo toggle moved** to the step it belongs to (the result for each kind of meat), with its band card.
- **The back-test is on the page.** The proposal said "back-test" under evidence; it had only been in the Python (`floor_physics.backtest`), so a table was added.
- **"How the tank is run" was not made an eleventh switch.** The later session decides how modes combine with vessels; the control stays in the all-levers panel with plain labels
  for its options, and the two-way table above shows what it is worth.
- **The all-levers panel is collapsed** and starts from the chosen scenario (a "Start from a scenario" control), so its tornado is the tornado around the page's default
  case, as the task asked ("tornado base case ... for the new default case").
- **Phone**: the scenario table restacks into cards below 700 px; the share section's assumption panel moves above its charts (as before).
