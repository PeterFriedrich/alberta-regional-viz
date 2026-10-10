# Findings: the jumps in the spending series (2026-10-10, S10)

`notebooks/01_first_look` showed five unexplained moves in `spending_per_capita.csv`.
Each was checked two ways:
- **inside FIR**: every Schedule C line of the city that year. A move that another
  line cancels is a filing classification, not spending.
- **against the city's audited annual report**, where it breaks the item out.

Sources and the extraction script are in
`/home/opc/research/alberta-regional-viz/spending_jumps_2026-10-10/` (README inside).
The annual reports' total expenses tie to FIR line 01580 to the thousand dollars
(Calgary 2016 $3,694.5M, 2022 $4,337.2M, 2025 $5,370.6M), so the two describe the
same books.

## Verdict

| Series | Move | Verdict | Evidence |
|---|---|---|---|
| Calgary core housing | 2016: $142.6M → $38.6M → $119.9M | **Classification** | FCSS + housing + economic development (01460) is $216.8M → $213.1M → $231.7M; 01460 jumps $7.2M → $83.6M → $14.4M that year. Calgary Housing Company's audited expenses are flat ($86.1M in 2015, $84.9M in 2016). |
| Calgary core housing | 2022: $105.0M → $19.7M → $106.5M | **Classification** | Revenue falls with it ($94.2M → $19.8M → $125.8M). FCSS + housing is $234.5M → $253.0M (expense) and $175.4M → $178.6M (revenue). CHC alone spent $111.6M in 2022 (2022 annual report p. 66), so FIR's $19.7M cannot hold it. |
| Calgary core FCSS | 2022–2025: $129.5M → $233.3M → $185.1M → $136.1M → $244.8M | **Mostly classification** | 2022 is the housing move above. In 2025 FCSS rises $108.7M while the 01400–01490 block (FCSS, housing, planning, land & housing rentals) rises $32.3M; land & housing rentals (01490) falls $53.7M. The annual reports don't break FCSS out; their community-services segment grows 5%, 13%, 4% and 16% in 2022–2025. FCSS + housing still moves +15% (2023) and −13% (2024), which is unexplained. |
| Calgary core FCSS and housing | 2020 | **Classification, small on our basis** | About $19M of expense and $12M of amortization moved from housing to FCSS (FCSS amortization $0.1M → $20.7M, housing $12.1M → $0). On gross = expense − amortization, FCSS goes $92.8M → $91.0M and housing $109.2M → $102.6M. |
| Edmonton core housing | 2021–2023: $47.5M → $87.5M → $153.8M → $88.2M | **Real spending** | 2021: about $20M more in Affordable Housing Investment Plan grants, plus spending funded by the federal Rapid Housing Initiative ($26.9M recognized in 2021; 2021 annual report). 2022: "transfer of land and assets related to permanent supportive housing of approximate value of $70.0 million to Homeward Trust", built with RHI funds and transferred at nominal value (2022 annual report). This is a one-time, non-cash expense. |
| Edmonton core FCSS | 2005–2007: $15.0M → $20.8M → $42.6M | **Likely classification** (medium confidence) | The 2007 annual report's "Community and family" line is $33.2M → $35.0M → $38.2M over 2005–2007 (+9% in 2007). In FIR, parks & recreation, economic development, culture and other expenditures fall $24.5M in 2007 against FCSS's +$21.8M. Community Services set up a new Neighbourhood and Community Development Branch that year. No single line offsets it cleanly. |

## What it breaks

- **Calgary's FCSS and housing lines are not comparable year to year.** Calgary
  moves amounts between FCSS, housing, economic development, planning and land &
  housing rentals. Combining FCSS and housing fixes 2020 and 2022 but not 2016
  (economic development) or 2025 (land & housing rentals). The per-year Calgary-core
  FCSS and housing series as built are wrong in 2016, 2022 and probably 2025.
- **Edmonton FCSS before 2007 is probably not on the same basis as after.**
- **Edmonton housing is real but includes a $70.0M non-cash item in 2022.** A chart
  of it needs that caption, or the series needs a one-off marker.
- **Not checked:** ring members, police, transit. Police and transit show no
  comparable jumps in the notebook. Ring lines are small; the same kind of
  classification noise would be smaller in dollars but not ruled out.

## Options (Peter's call; nothing changed in `src/` yet)

- **A. Drop the Calgary-core FCSS and housing series from charts.** The
  split-screen comparison uses police and transit for Calgary. Edmonton FCSS starts in
  2007. Edmonton housing keeps the 2022 caption. *(Recommended: no hand corrections,
  and every remaining series has a source-backed explanation of its moves.)*
- **B. Combine FCSS + housing into one "social and housing" function for both
  regions, from 2009,** with Calgary 2016 and 2025 shown as gaps. Keeps a social line
  for Calgary, but the gaps are hand-picked from this check, and 2023–2024 stay
  unexplained.
- **C. Keep the series as built and mark 2016, 2020, 2022 and 2025 on Calgary's
  charts.** Readers would still see swings that aren't spending.
