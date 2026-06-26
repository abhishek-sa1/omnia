#!/usr/bin/env bats
# =============================================================================
# test_container_execution.bats — Tier 2: System tests for per-container build.sh
# =============================================================================
# Function definitions, container_build invocations, build contexts,
# Containerfile references, build args, and external repo clones.
#
# Usage:  bats test/system/bats/test_container_execution.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    CONTAINERS_DIR="${REPO_ROOT}/src/containers"
}

# =============================================================================
# 1. All build.sh have bash shebang
# =============================================================================

@test "all build.sh files have bash shebang" {
    for dir in omnia_core omnia_auth omnia_build_stream ldms kafkapump victoriapump telemetry_receiver image_builder; do
        run head -1 "${CONTAINERS_DIR}/${dir}/build.sh"
        assert_output --partial '#!/bin/bash'
    done
}

# =============================================================================
# 2. Function definitions — one per container
# =============================================================================

@test "omnia_core/build.sh defines build_omnia_core()" {
    run grep 'build_omnia_core()' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_success
}

@test "omnia_auth/build.sh defines build_omnia_auth()" {
    run grep 'build_omnia_auth()' "${CONTAINERS_DIR}/omnia_auth/build.sh"
    assert_success
}

@test "omnia_build_stream/build.sh defines build_omnia_build_stream()" {
    run grep 'build_omnia_build_stream()' "${CONTAINERS_DIR}/omnia_build_stream/build.sh"
    assert_success
}

@test "ldms/build.sh defines build_ldms()" {
    run grep 'build_ldms()' "${CONTAINERS_DIR}/ldms/build.sh"
    assert_success
}

@test "kafkapump/build.sh defines build_kafkapump()" {
    run grep 'build_kafkapump()' "${CONTAINERS_DIR}/kafkapump/build.sh"
    assert_success
}

@test "victoriapump/build.sh defines build_victoriapump()" {
    run grep 'build_victoriapump()' "${CONTAINERS_DIR}/victoriapump/build.sh"
    assert_success
}

@test "telemetry_receiver/build.sh defines build_telemetry_receiver()" {
    run grep 'build_telemetry_receiver()' "${CONTAINERS_DIR}/telemetry_receiver/build.sh"
    assert_success
}

@test "image_builder/build.sh defines build_image_builder()" {
    run grep 'build_image_builder()' "${CONTAINERS_DIR}/image_builder/build.sh"
    assert_success
}

# =============================================================================
# 3. Containerfile references — correct file names
# =============================================================================

@test "omnia_core uses src/containers/omnia_core/Containerfile" {
    run grep 'Containerfile' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_success
    assert_output --partial 'src/containers/omnia_core/Containerfile'
}

@test "omnia_auth uses Containerfile" {
    run grep 'Containerfile' "${CONTAINERS_DIR}/omnia_auth/build.sh"
    assert_success
}

@test "omnia_build_stream uses Containerfile" {
    run grep 'Containerfile' "${CONTAINERS_DIR}/omnia_build_stream/build.sh"
    assert_success
}

@test "ldms uses Containerfile.bld_n_run.ubuntu26.04" {
    run grep 'Containerfile.bld_n_run.ubuntu26.04' "${CONTAINERS_DIR}/ldms/build.sh"
    assert_success
}

@test "image_builder uses Containerfile.el10" {
    run grep 'Containerfile.el10' "${CONTAINERS_DIR}/image_builder/build.sh"
    assert_success
}

# =============================================================================
# 4. Build context paths
# =============================================================================

@test "omnia_core uses REPO_ROOT as build context" {
    run grep 'REPO_ROOT' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_success
}

@test "omnia_auth uses CONTAINERS_DIR as build context" {
    run grep 'CONTAINERS_DIR' "${CONTAINERS_DIR}/omnia_auth/build.sh"
    assert_success
}

@test "ldms uses CONTAINERS_DIR/ldms as build context" {
    run grep 'CONTAINERS_DIR.*ldms' "${CONTAINERS_DIR}/ldms/build.sh"
    assert_success
}

@test "kafkapump uses IDRAC_TELEMETRY_CLONE_DIR" {
    run grep 'IDRAC_TELEMETRY_CLONE_DIR' "${CONTAINERS_DIR}/kafkapump/build.sh"
    assert_success
}

@test "image_builder uses IMAGE_BUILDER_CLONE_DIR" {
    run grep 'IMAGE_BUILDER_CLONE_DIR' "${CONTAINERS_DIR}/image_builder/build.sh"
    assert_success
}

# =============================================================================
# 5. Build args & flags
# =============================================================================

@test "omnia_build_stream uses --network=host" {
    run grep 'network=host' "${CONTAINERS_DIR}/omnia_build_stream/build.sh"
    assert_success
}

@test "kafkapump uses --build-arg CMD=kafkapump" {
    run grep 'CMD=kafkapump' "${CONTAINERS_DIR}/kafkapump/build.sh"
    assert_success
}

@test "victoriapump uses --build-arg CMD=victoriapump" {
    run grep 'CMD=victoriapump' "${CONTAINERS_DIR}/victoriapump/build.sh"
    assert_success
}

# =============================================================================
# 6. External repo clones
# =============================================================================

@test "kafkapump defines IDRAC_TELEMETRY_COMMIT" {
    run grep 'IDRAC_TELEMETRY_COMMIT=' "${CONTAINERS_DIR}/kafkapump/build.sh"
    assert_success
}

@test "kafkapump calls clone_repo_at_commit" {
    run grep 'clone_repo_at_commit' "${CONTAINERS_DIR}/kafkapump/build.sh"
    assert_success
}

@test "victoriapump calls clone_repo_at_commit" {
    run grep 'clone_repo_at_commit' "${CONTAINERS_DIR}/victoriapump/build.sh"
    assert_success
}

@test "telemetry_receiver calls clone_repo_at_commit" {
    run grep 'clone_repo_at_commit' "${CONTAINERS_DIR}/telemetry_receiver/build.sh"
    assert_success
}

@test "image_builder defines IMAGE_BUILDER_COMMIT" {
    run grep 'IMAGE_BUILDER_COMMIT=' "${CONTAINERS_DIR}/image_builder/build.sh"
    assert_success
}

@test "image_builder clones OpenCHAMI repo" {
    run grep 'OpenCHAMI/image-builder' "${CONTAINERS_DIR}/image_builder/build.sh"
    assert_success
}

@test "telemetry containers clone iDRAC repo" {
    run grep 'iDRAC-Telemetry-Reference-Tools' "${CONTAINERS_DIR}/kafkapump/build.sh"
    assert_success
}

# =============================================================================
# 7. ldms naming consistency
# =============================================================================

@test "ldms/build.sh uses LDMS_TAG (not UBUNTU_LDMS_TAG)" {
    run grep 'LDMS_TAG' "${CONTAINERS_DIR}/ldms/build.sh"
    assert_success
    run grep 'UBUNTU_LDMS_TAG' "${CONTAINERS_DIR}/ldms/build.sh"
    assert_failure
}

# =============================================================================
# 8. No stale references in build scripts
# =============================================================================

@test "no build.sh references old ContainerFile/ directory" {
    for dir in omnia_core omnia_auth omnia_build_stream ldms; do
        run grep -c 'ContainerFile/' "${CONTAINERS_DIR}/${dir}/build.sh"
        assert_output "0"
    done
}

@test "omnia_core/build.sh has no omnia_branch reference" {
    run grep 'omnia_branch' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_failure
}

@test "omnia_core/build.sh has no OMNIA_VERSION reference" {
    run grep 'OMNIA_VERSION' "${CONTAINERS_DIR}/omnia_core/build.sh"
    assert_failure
}
