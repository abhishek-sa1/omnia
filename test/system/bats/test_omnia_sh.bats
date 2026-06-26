#!/usr/bin/env bats
# =============================================================================
# omnia.sh — BATS System Tests
# =============================================================================
# Usage:  bats test/system/bats/test_omnia_sh.bats
# Run from the repository root (omnia-bsm/).
#
# Requires: bats-core, bats-support, bats-assert
# Helpers are vendored at test/test_helper/ (shared across all BATS tests).
# One-time setup:  bash test/test_helper/install.sh
# =============================================================================

# Load BATS helpers from shared test/test_helper/
load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

# ── Setup ──
setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../../.." && pwd)"
    OMNIA_SH="$REPO_ROOT/src/main/omnia.sh"
}

# =============================================================================
# 1. File existence & location
# =============================================================================

@test "omnia.sh exists at src/main/omnia.sh" {
    [ -f "$OMNIA_SH" ]
}

@test "omnia.sh is executable" {
    [ -x "$OMNIA_SH" ]
}

@test "omnia.sh has bash shebang" {
    run head -1 "$OMNIA_SH"
    assert_output --partial '#!/bin/bash'
}

@test "omnia.sh is not at repo root (moved to src/main/)" {
    [ ! -f "$REPO_ROOT/omnia.sh" ]
}

# =============================================================================
# 2. CLI options — --build
# =============================================================================

@test "help text includes --build option" {
    run grep -- '--build' "$OMNIA_SH"
    assert_success
}

@test "help text includes -b short option" {
    run grep -- '-b,.*--build' "$OMNIA_SH"
    assert_success
}

@test "--build|-b case handler exists in main()" {
    run grep -- '\-\-build|\-b)' "$OMNIA_SH"
    assert_success
}

@test "main() receives single arg via \$1" {
    run grep 'main "$1"' "$OMNIA_SH"
    assert_success
}

# =============================================================================
# 3. Function definitions
# =============================================================================

@test "build_omnia_core_image() is defined" {
    run grep 'build_omnia_core_image()' "$OMNIA_SH"
    assert_success
}

@test "validate_container_image() is defined" {
    run grep 'validate_container_image()' "$OMNIA_SH"
    assert_success
}

# =============================================================================
# 4. Monorepo path references (container-repo context)
# =============================================================================

@test "prepare_upgrade.yml path uses /omnia/src/playbooks/upgrade/" {
    run grep '/omnia/src/playbooks/upgrade/prepare_upgrade.yml' "$OMNIA_SH"
    assert_success
}

@test "upgrade.yml path uses /omnia/src/playbooks/upgrade/" {
    run grep '/omnia/src/playbooks/upgrade/upgrade.yml' "$OMNIA_SH"
    assert_success
}

@test "oim_cleanup.yml path uses /omnia/src/playbooks/utils/" {
    run grep '/omnia/src/playbooks/utils/oim_cleanup.yml' "$OMNIA_SH"
    assert_success
}

@test "input path references /omnia/src/input/" {
    run grep '/omnia/src/input' "$OMNIA_SH"
    assert_success
}

@test "build function references containers/build_images.sh" {
    run grep 'containers/build_images.sh' "$OMNIA_SH"
    assert_success
}

@test "validate_container_image directs user to omnia.sh --build" {
    run grep 'omnia.sh --build' "$OMNIA_SH"
    assert_success
}

# =============================================================================
# 5. No stale pre-monorepo references
# =============================================================================

@test "no omnia-artifactory references" {
    run grep 'omnia-artifactory' "$OMNIA_SH"
    assert_failure
}

@test "no stale /omnia/upgrade/ paths (without src/)" {
    # grep for /omnia/upgrade/ but exclude lines with /omnia/src/ and comments
    run bash -c "grep '/omnia/upgrade/' '$OMNIA_SH' | grep -v '/omnia/src/' | grep -v '^#'"
    assert_failure
}

@test "no stale /omnia/utils/ paths (without src/)" {
    run bash -c "grep '/omnia/utils/' '$OMNIA_SH' | grep -v '/omnia/src/' | grep -v '^#'"
    assert_failure
}

@test "no stale /omnia/oim_cleanup.yml reference" {
    run grep '/omnia/oim_cleanup.yml' "$OMNIA_SH"
    assert_failure
}

@test "no rm -rf /omnia/omnia.sh" {
    run grep -E 'rm.*-rf.*/omnia/omnia\.sh' "$OMNIA_SH"
    assert_failure
}
