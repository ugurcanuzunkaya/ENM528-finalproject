# Parallel Execution Commands

You can copy and paste these blocks into different terminal windows to run experiments in parallel.

## Group 1: Baseline & Scenario 1 (Fast Runs)

**Terminal 1:**

```bash
# Scenario 0: Baseline (Fixed)
uv run python src/main.py --scenario 0 --locator fixed --fleet homog --seed 42

# Scenario 1: Dynamic (Centroid)
uv run python src/main.py --scenario 1 --locator centroid --fleet homog --seed 42

# Scenario 1: Dynamic (P-Median)
uv run python src/main.py --scenario 1 --locator p-median --fleet homog --seed 42
```

## Group 2: Scenario 2 - Centroid (Parametric)

**Terminal 2:**

```bash
# Centroid - Homog
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type closed --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet homog --loop-type open --seed 42

# Centroid - Mix 1
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type closed --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_1 --loop-type open --seed 42

# Centroid - Mix 2
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type closed --seed 42
uv run python src/main.py --scenario 2 --locator centroid --fleet mix_2 --loop-type open --seed 42
```

## Group 3: Scenario 2 - P-Median (Parametric)

**Terminal 3:**

```bash
# P-Median - Homog
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type closed --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet homog --loop-type open --seed 42

# P-Median - Mix 1
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type closed --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_1 --loop-type open --seed 42

# P-Median - Mix 2
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type closed --seed 42
uv run python src/main.py --scenario 2 --locator p-median --fleet mix_2 --loop-type open --seed 42
```

## Group 4: Scenario 3 - LRP (Computationally Intensive)

**Terminal 4:**

```bash
# LRP - Homog Fleet
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet homog --seed 42

# LRP - Mix 1 Fleet
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_1 --seed 42

# LRP - Mix 2 Fleet
uv run python src/main.py --scenario 3 --locator p-median --candidates 4 --fleet mix_2 --seed 42
```
