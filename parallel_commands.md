# Parallel Execution Commands

You can copy and paste these blocks into different terminal windows to run experiments in parallel.
Total Experiments: ~48 (16 per data mode).

---

# Part A: Uniform Data (Default)

## Group 1: Baseline & S1 (Uniform)

**Terminal 1:**

```bash
# Scenario 0: Baseline (Fixed)
uv run python src/main.py --scenario 0 --locator fixed --fleet homog --data-mode uniform --seed 42

# Scenario 1: Dynamic (Centroid)
uv run python src/main.py --scenario 1 --locator centroid --fleet homog --data-mode uniform --seed 42

# Scenario 1: Dynamic (P-Median)
uv run python src/main.py --scenario 1 --locator p-median --fleet homog --data-mode uniform --seed 42
```

## Group 2: S2 Centroid (Uniform)

**Terminal 2:**

```bash
# Centroid - Homog
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type closed --data-mode uniform --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type open --data-mode uniform --seed 42

# Centroid - Mix 1
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type closed --data-mode uniform --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type open --data-mode uniform --seed 42

# Centroid - Mix 2
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type closed --data-mode uniform --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type open --data-mode uniform --seed 42
```

## Group 3: S2 P-Median (Uniform)

**Terminal 3:**

```bash
# P-Median - Homog
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type closed --data-mode uniform --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type open --data-mode uniform --seed 42

# P-Median - Mix 1
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type closed --data-mode uniform --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type open --data-mode uniform --seed 42

# P-Median - Mix 2
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type closed --data-mode uniform --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type open --data-mode uniform --seed 42
```

## Group 4: S3 LRP (Uniform)

**Terminal 4:**

```bash
# LRP - Homog Fleet
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet homog --data-mode uniform --seed 42

# LRP - Mix 1 Fleet
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_1 --data-mode uniform --seed 42

# LRP - Mix 2 Fleet
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_2 --data-mode uniform --seed 42
```

---

# Part B: Clustered Data

## Group 5: Baseline & S1 (Clustered)

**Terminal 5:**

```bash
# Scenario 0
uv run python src/main.py --scenario 0 --locator fixed --fleet homog --data-mode clustered --seed 42

# Scenario 1 (Centroid & P-Median)
uv run python src/main.py --scenario 1 --locator centroid --fleet homog --data-mode clustered --seed 42
uv run python src/main.py --scenario 1 --locator p-median --fleet homog --data-mode clustered --seed 42
```

## Group 6: S2 Centroid (Clustered)

**Terminal 6:**

```bash
# Homog
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type closed --data-mode clustered --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type open --data-mode clustered --seed 42

# Mix 1
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type closed --data-mode clustered --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type open --data-mode clustered --seed 42

# Mix 2
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type closed --data-mode clustered --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type open --data-mode clustered --seed 42
```

## Group 7: S2 P-Median (Clustered)

**Terminal 7:**

```bash
# Homog
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type closed --data-mode clustered --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type open --data-mode clustered --seed 42

# Mix 1
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type closed --data-mode clustered --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type open --data-mode clustered --seed 42

# Mix 2
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type closed --data-mode clustered --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type open --data-mode clustered --seed 42
```

## Group 8: S3 LRP (Clustered)

**Terminal 8:**

```bash
# LRP Fleets
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet homog --data-mode clustered --seed 42
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_1 --data-mode clustered --seed 42
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_2 --data-mode clustered --seed 42
```

---

# Part C: Solomon Data (c101.txt)

## Group 9: Baseline & S1 (Solomon)

**Terminal 9:**

```bash
# Scenario 0
uv run python src/main.py --scenario 0 --locator fixed --fleet homog --data-mode solomon --data-file c101.txt --seed 42

# Scenario 1
uv run python src/main.py --scenario 1 --locator centroid --fleet homog --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 1 --locator p-median --fleet homog --data-mode solomon --data-file c101.txt --seed 42
```

## Group 10: S2 Centroid (Solomon)

**Terminal 10:**

```bash
# Homog
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type closed --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type open --data-mode solomon --data-file c101.txt --seed 42

# Mix 1
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type closed --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type open --data-mode solomon --data-file c101.txt --seed 42

# Mix 2
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type closed --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type open --data-mode solomon --data-file c101.txt --seed 42
```

## Group 11: S2 P-Median (Solomon)

**Terminal 11:**

```bash
# Homog
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type closed --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type open --data-mode solomon --data-file c101.txt --seed 42

# Mix 1
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type closed --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type open --data-mode solomon --data-file c101.txt --seed 42

# Mix 2
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type closed --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type open --data-mode solomon --data-file c101.txt --seed 42
```

## Group 12: S3 LRP (Solomon)

**Terminal 12:**

```bash
# LRP Fleets
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet homog --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_1 --data-mode solomon --data-file c101.txt --seed 42
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_2 --data-mode solomon --data-file c101.txt --seed 42
```
