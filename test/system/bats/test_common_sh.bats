#!/usr/bin/env bats
# =============================================================================
# test_common_sh.bats — Tier 2: System tests for _common.sh
# =============================================================================
# Function definitions, variables, color codes, podman/docker support.
#
# Usage:  bats test/system/bats/test_common_sh.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    COMMON_SH="${REPO_ROOT}/src/containers/_common.sh"
}

# =============================================================================
# 1. Shebang
# =============================================================================

@test "_common.sh has bash shebang" {
    run head -1 "$COMMON_SH"
    assert_output --partial '#!/bin/bash'
}

# =============================================================================
# 2. Function definitions
# =============================================================================

@test "defines container_build()" {
    run grep -c '^container_build()' "$COMMON_SH"
    assert_output "1"
}

@test "defines print_build_info()" {
    run grep -c '^print_build_info()' "$COMMON_SH"
    assert_output "1"
}

@test "defines clone_repo_at_commit()" {
    run grep -c '^clone_repo_at_commit()' "$COMMON_SH"
    assert_output "1"
}

@test "defines print_build_summary()" {
    run grep -c '^print_build_summary()' "$COMMON_SH"
    assert_output "1"
}

# =============================================================================
# 3. Path variables
# =============================================================================

@test "defines CONTAINERS_DIR" {
    run grep -c 'CONTAINERS_DIR=' "$COMMON_SH"
    assert_success
}

@test "defines REPO_ROOT" {
    run grep -c 'REPO_ROOT=' "$COMMON_SH"
    assert_success
}

# =============================================================================
# 4. Build tracking arrays
# =============================================================================

@test "initializes SUCCESSFUL_BUILDS array" {
    run grep 'SUCCESSFUL_BUILDS=()' "$COMMON_SH"
    assert_success
}

@test "initializes FAILED_BUILDS array" {
    run grep 'FAILED_BUILDS=()' "$COMMON_SH"
    assert_success
}

@test "initializes LOADED_IMAGES array" {
    run grep 'LOADED_IMAGES=()' "$COMMON_SH"
    assert_success
}

@test "initializes PUSHED_IMAGES array" {
    run grep 'PUSHED_IMAGES=()' "$COMMON_SH"
    assert_success
}

# =============================================================================
# 5. container_build — podman & docker support
# =============================================================================

@test "container_build supports podman" {
    run grep 'podman build' "$COMMON_SH"
    assert_success
}

@test "container_build supports docker buildx" {
    run grep 'docker buildx build' "$COMMON_SH"
    assert_success
}

@test "container_build supports load action" {
    run grep -- '--load' "$COMMON_SH"
    assert_success
}

@test "container_build supports push action" {
    run grep -- '--push' "$COMMON_SH"
    assert_success
}

@test "container_build uses --file for containerfile" {
    run grep -- '--file.*containerfile' "$COMMON_SH"
    assert_success
}

@test "container_build uses --platform" {
    run grep -- '--platform' "$COMMON_SH"
    assert_success
}

@test "container_build defaults platform to linux/amd64" {
    run grep 'linux/amd64' "$COMMON_SH"
    assert_success
}

# =============================================================================
# 6. Build result tracking
# =============================================================================

@test "tracks success in SUCCESSFUL_BUILDS" {
    run grep 'SUCCESSFUL_BUILDS+=(' "$COMMON_SH"
    assert_success
}

@test "tracks failure in FAILED_BUILDS" {
    run grep 'FAILED_BUILDS+=(' "$COMMON_SH"
    assert_success
}

# =============================================================================
# 7. Color codes
# =============================================================================

@test "defines RED color" {
    run grep "RED='" "$COMMON_SH"
    assert_success
}

@test "defines GREEN color" {
    run grep "GREEN='" "$COMMON_SH"
    assert_success
}

@test "defines YELLOW color" {
    run grep "YELLOW='" "$COMMON_SH"
    assert_success
}

@test "defines NC (no color) reset" {
    run grep "NC='" "$COMMON_SH"
    assert_success
}

# =============================================================================
# 8. print_build_summary sections
# =============================================================================

@test "print_build_summary shows BUILD SUMMARY header" {
    run grep 'BUILD SUMMARY' "$COMMON_SH"
    assert_success
}

@test "print_build_summary reports successful builds" {
    run grep 'Successfully built containers' "$COMMON_SH"
    assert_success
}

@test "print_build_summary reports failed builds" {
    run grep 'Failed builds' "$COMMON_SH"
    assert_success
}

@test "print_build_summary shows build statistics" {
    run grep 'Build Statistics' "$COMMON_SH"
    assert_success
}

@test "print_build_summary shows omnia_core next step" {
    run grep 'omnia.sh --install' "$COMMON_SH"
    assert_success
}

# =============================================================================
# 9. No stale references
# =============================================================================

@test "no omnia-artifactory references" {
    run grep 'omnia-artifactory' "$COMMON_SH"
    assert_failure
}

@test "no stale Dockerfile word in comments" {
    run grep -i 'dockerfile' "$COMMON_SH"
    assert_failure
}
