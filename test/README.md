# Omnia Mono-Repository — Test Directory

> **Structure**: AgentOps 4-Tier Convention | **Convention**: Singular `test/` (not `tests/`)

---

## Directory Layout

```
test/
├── unit/                              # Tier 1: Pure unit tests (structure only)
│   └── bats/
│       └── test_container_structure.bats   # Directory/file existence checks
│
├── system/                            # Tier 2: System tests (script logic, no cluster)
│   └── bats/
│       ├── test_omnia_sh.bats              # omnia.sh CLI, functions, paths
│       ├── test_build_images.bats          # build_images.sh dispatch, params, defaults
│       ├── test_common_sh.bats             # _common.sh functions, variables, colors
│       └── test_container_execution.bats   # Per-container build.sh, context, args
│
├── nft/                               # Tier 3: Non-functional tests
│   ├── bats/
│   │   ├── test_containerfile_security.bats  # Credentials, ADD, cache cleanup
│   │   └── test_shell_quality.bats           # Shebangs, stale refs, consistency
│   └── performance/                          # (future) Build stream benchmarks
│
├── e2e-sanity/                        # Tier 4: End-to-end sanity
│   ├── bats/
│   │   ├── test_container_build_sanity.bats  # Containerfile FROM, LABEL, COPY
│   │   └── test_omnia_sh_sanity.bats         # omnia.sh functions, version, upgrade
│   ├── molecule/                             # (future) Molecule scenarios
│   ├── automation_library/                   # (future) Test helper functions
│   └── datasets/                             # (future) Test input overrides
│
├── test_helper/                       # Shared BATS libraries (vendored)
│   ├── bats-support/
│   ├── bats-assert/
│   └── install.sh
│
├── fixtures/                          # Shared test data across all tiers
├── conftest.py                        # Root pytest fixtures (future)
├── pytest.ini                         # Root pytest config (future)
└── Makefile                           # Test runner targets (future)
```

---

## Setup (One-Time)

```bash
# Install BATS core (npm)
npm install -g bats

# Install shared BATS helper libraries (vendored locally, no submodules)
bash test/test_helper/install.sh
```

---

## Running Tests

All commands assume you are at the **repository root** (`omnia-bsm/`).

### Tier 1 — Unit Tests (structure)

```bash
bats test/unit/bats/test_container_structure.bats
```

### Tier 2 — System Tests (script logic)

```bash
# omnia.sh
bats test/system/bats/test_omnia_sh.bats

# Container build infrastructure
bats test/system/bats/test_build_images.bats
bats test/system/bats/test_common_sh.bats
bats test/system/bats/test_container_execution.bats

# All system tests at once
bats test/system/bats/
```

### Tier 3 — Non-Functional Tests (lint, security)

```bash
# Shell script quality
bats test/nft/bats/test_shell_quality.bats

# Containerfile security checks
bats test/nft/bats/test_containerfile_security.bats

# All NFT tests at once
bats test/nft/bats/
```

### Tier 4 — End-to-End Sanity

```bash
# Container build readiness
bats test/e2e-sanity/bats/test_container_build_sanity.bats

# omnia.sh full sanity
bats test/e2e-sanity/bats/test_omnia_sh_sanity.bats

# All e2e-sanity tests at once
bats test/e2e-sanity/bats/
```

### Run All BATS Tests

```bash
bats test/unit/bats/ \
     test/system/bats/ \
     test/nft/bats/ \
     test/e2e-sanity/bats/
```

### Windows (Git Bash / PowerShell)

If `bats` is installed via npm but `bash` is not in PATH:

```powershell
$env:PATH = "C:\Program Files\Git\bin;C:\Program Files\Git\usr\bin;" + $env:PATH
& "C:\Program Files\Git\bin\bash.exe" -c "npx bats test/unit/bats/test_container_structure.bats"
```

---

## Test Technology Mapping

| Technology | Where It Appears | What It Tests |
|------------|-----------------|---------------|
| **BATS** | `unit/bats/`, `system/bats/`, `nft/bats/`, `e2e-sanity/bats/` | Shell script testing — structure, logic, security, sanity |
| **pytest** | `unit/*` (future), `nft/performance/` (future) | Python unit tests, benchmarks |
| **Molecule** | `e2e-sanity/molecule/` (future) | Full playbook runs on real OIM + compute nodes |
| **Trivy/Grype** | `nft/security/` (future) | Container image CVE scanning |

---

## Tier Summary

| Tier | Directory | Runs When | Tests | Duration |
|------|-----------|-----------|-------|----------|
| 1 | `unit/` | Every PR | Structure: dirs, files, no stale artifacts | ~1s |
| 2 | `system/` | Every PR / nightly | Script logic: dispatch, params, functions, paths | ~5s |
| 3 | `nft/` | Weekly / on-demand | Security, lint, quality checks | ~3s |
| 4 | `e2e-sanity/` | Nightly / manual | Containerfile content, omnia.sh full sanity | ~5s |
