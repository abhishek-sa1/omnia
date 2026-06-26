#!/usr/bin/env bats
# =============================================================================
# test_shell_quality.bats — Tier 3: NFT lint / quality checks
# =============================================================================
# Shell script quality: shebangs, no stale cross-repo refs, naming conventions.
#
# Usage:  bats test/nft/bats/test_shell_quality.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    CONTAINERS_DIR="${REPO_ROOT}/src/containers"
    OMNIA_SH="${REPO_ROOT}/src/main/omnia.sh"
}

# =============================================================================
# 1. All shell scripts have proper shebang
# =============================================================================

@test "build_images.sh has bash shebang" {
    run head -1 "${CONTAINERS_DIR}/build_images.sh"
    assert_output --partial '#!/bin/bash'
}

@test "_common.sh has bash shebang" {
    run head -1 "${CONTAINERS_DIR}/_common.sh"
    assert_output --partial '#!/bin/bash'
}

@test "omnia.sh has bash shebang" {
    run head -1 "$OMNIA_SH"
    assert_output --partial '#!/bin/bash'
}

@test "all container build.sh have bash shebang" {
    for dir in omnia_core omnia_auth omnia_build_stream ldms kafkapump victoriapump telemetry_receiver image_builder; do
        run head -1 "${CONTAINERS_DIR}/${dir}/build.sh"
        assert_output --partial '#!/bin/bash'
    done
}

# =============================================================================
# 2. No stale cross-repo references anywhere
# =============================================================================

@test "no omnia-artifactory in build_images.sh" {
    run grep 'omnia-artifactory' "${CONTAINERS_DIR}/build_images.sh"
    assert_failure
}

@test "no omnia-artifactory in _common.sh" {
    run grep 'omnia-artifactory' "${CONTAINERS_DIR}/_common.sh"
    assert_failure
}

@test "no omnia-artifactory in omnia.sh" {
    run grep 'omnia-artifactory' "$OMNIA_SH"
    assert_failure
}

# =============================================================================
# 3. No stale Dockerfile references in shell scripts
# =============================================================================

@test "no Dockerfile word in _common.sh" {
    run grep -i 'dockerfile' "${CONTAINERS_DIR}/_common.sh"
    assert_failure
}

@test "no Dockerfile word in build_images.sh" {
    run grep -i 'dockerfile' "${CONTAINERS_DIR}/build_images.sh"
    assert_failure
}

# =============================================================================
# 4. Removed features — omnia_branch fully purged
# =============================================================================

@test "no omnia_branch in build_images.sh" {
    run grep 'omnia_branch' "${CONTAINERS_DIR}/build_images.sh"
    assert_failure
}

@test "no omnia_branch in omnia_core/build.sh" {
    run grep 'omnia_branch' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_failure
}

@test "no OMNIA_VERSION in build_images.sh" {
    run grep 'OMNIA_VERSION=' "${CONTAINERS_DIR}/build_images.sh"
    assert_failure
}

# =============================================================================
# 5. Removed containers — no pcs or ubuntu_ldms
# =============================================================================

@test "no pcs references in build_images.sh" {
    run grep -i 'pcs' "${CONTAINERS_DIR}/build_images.sh"
    assert_failure
}

@test "no ubuntu-ldms in build_images.sh" {
    run grep 'ubuntu-ldms\|ubuntu_ldms\|UBUNTU_LDMS' "${CONTAINERS_DIR}/build_images.sh"
    assert_failure
}

# =============================================================================
# 6. Script consistency — all build.sh call container_build
# =============================================================================

@test "omnia_core/build.sh calls container_build" {
    run grep 'container_build' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_success
}

@test "omnia_auth/build.sh calls container_build" {
    run grep 'container_build' "${CONTAINERS_DIR}/omnia_auth/build.sh"
    assert_success
}

@test "omnia_build_stream/build.sh calls container_build" {
    run grep 'container_build' "${CONTAINERS_DIR}/omnia_build_stream/build.sh"
    assert_success
}

@test "ldms/build.sh calls container_build" {
    run grep 'container_build' "${CONTAINERS_DIR}/ldms/build.sh"
    assert_success
}

@test "kafkapump/build.sh calls container_build" {
    run grep 'container_build' "${CONTAINERS_DIR}/kafkapump/build.sh"
    assert_success
}

@test "image_builder/build.sh calls container_build" {
    run grep 'container_build' "${CONTAINERS_DIR}/image_builder/build.sh"
    assert_success
}

# =============================================================================
# 7. Script consistency — all build.sh call print_build_info
# =============================================================================

@test "omnia_core/build.sh calls print_build_info" {
    run grep 'print_build_info' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_success
}

@test "omnia_auth/build.sh calls print_build_info" {
    run grep 'print_build_info' "${CONTAINERS_DIR}/omnia_auth/build.sh"
    assert_success
}

@test "ldms/build.sh calls print_build_info" {
    run grep 'print_build_info' "${CONTAINERS_DIR}/ldms/build.sh"
    assert_success
}
