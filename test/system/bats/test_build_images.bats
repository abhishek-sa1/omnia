#!/usr/bin/env bats
# =============================================================================
# test_build_images.bats — Tier 2: System tests for build_images.sh
# =============================================================================
# CLI dispatch, parameter parsing, default values, sourcing, validation.
#
# Usage:  bats test/system/bats/test_build_images.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    CONTAINERS_DIR="${REPO_ROOT}/src/containers"
    BUILD_IMAGES="${CONTAINERS_DIR}/build_images.sh"
}

# =============================================================================
# 1. Shebang & basic properties
# =============================================================================

@test "build_images.sh has bash shebang" {
    run head -1 "$BUILD_IMAGES"
    assert_output --partial '#!/bin/bash'
}

# =============================================================================
# 2. Source statements — all build scripts sourced
# =============================================================================

@test "sources _common.sh" {
    run grep 'source.*_common.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources omnia_core/build.sh" {
    run grep 'source.*omnia_core/build.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources omnia_auth/build.sh" {
    run grep 'source.*omnia_auth/build.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources omnia_build_stream/build.sh" {
    run grep 'source.*omnia_build_stream/build.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources ldms/build.sh" {
    run grep 'source.*ldms/build.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources kafkapump/build.sh" {
    run grep 'source.*kafkapump/build.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources victoriapump/build.sh" {
    run grep 'source.*victoriapump/build.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources telemetry_receiver/build.sh" {
    run grep 'source.*telemetry_receiver/build.sh' "$BUILD_IMAGES"
    assert_success
}

@test "sources image_builder/build.sh" {
    run grep 'source.*image_builder/build.sh' "$BUILD_IMAGES"
    assert_success
}

# =============================================================================
# 3. Default tag values
# =============================================================================

@test "default CORE_TAG is 2.2" {
    run grep 'CORE_TAG="2.2"' "$BUILD_IMAGES"
    assert_success
}

@test "default AUTH_TAG is 1.1" {
    run grep 'AUTH_TAG="1.1"' "$BUILD_IMAGES"
    assert_success
}

@test "default LDMS_TAG is 1.1" {
    run grep 'LDMS_TAG="1.1"' "$BUILD_IMAGES"
    assert_success
}

@test "default KAFKAPUMP_TAG is 1.3" {
    run grep 'KAFKAPUMP_TAG="1.3"' "$BUILD_IMAGES"
    assert_success
}

@test "default VICTORIAPUMP_TAG is 1.3" {
    run grep 'VICTORIAPUMP_TAG="1.3"' "$BUILD_IMAGES"
    assert_success
}

@test "default TELEMETRY_RECEIVER_TAG is 1.3" {
    run grep 'TELEMETRY_RECEIVER_TAG="1.3"' "$BUILD_IMAGES"
    assert_success
}

@test "default IMAGE_BUILDER_TAG is 1.1" {
    run grep 'IMAGE_BUILDER_TAG="1.1"' "$BUILD_IMAGES"
    assert_success
}

@test "default BUILD_STREAM_TAG is 1.1" {
    run grep 'BUILD_STREAM_TAG="1.1"' "$BUILD_IMAGES"
    assert_success
}

@test "default BUILD_TOOL is podman" {
    run grep 'BUILD_TOOL="podman"' "$BUILD_IMAGES"
    assert_success
}

@test "default BUILD_ACTION is load" {
    run grep 'BUILD_ACTION="load"' "$BUILD_IMAGES"
    assert_success
}

@test "default OMNIA_DOCKER_REGISTERY is set" {
    run grep 'OMNIA_DOCKER_REGISTERY="docker.io/dellhpcomniaaisolution"' "$BUILD_IMAGES"
    assert_success
}

# =============================================================================
# 4. VALID_CONTAINERS list
# =============================================================================

@test "VALID_CONTAINERS includes core" {
    run grep 'VALID_CONTAINERS=' "$BUILD_IMAGES"
    assert_output --partial '"core"'
}

@test "VALID_CONTAINERS includes auth" {
    run grep 'VALID_CONTAINERS=' "$BUILD_IMAGES"
    assert_output --partial '"auth"'
}

@test "VALID_CONTAINERS includes ldms" {
    run grep 'VALID_CONTAINERS=' "$BUILD_IMAGES"
    assert_output --partial '"ldms"'
}

@test "VALID_CONTAINERS includes telemetry" {
    run grep 'VALID_CONTAINERS=' "$BUILD_IMAGES"
    assert_output --partial '"telemetry"'
}

@test "VALID_CONTAINERS includes image-builder" {
    run grep 'VALID_CONTAINERS=' "$BUILD_IMAGES"
    assert_output --partial '"image-builder"'
}

@test "VALID_CONTAINERS includes build-stream" {
    run grep 'VALID_CONTAINERS=' "$BUILD_IMAGES"
    assert_output --partial '"build-stream"'
}

@test "VALID_CONTAINERS does NOT include pcs" {
    run bash -c "grep 'VALID_CONTAINERS=' '$BUILD_IMAGES' | grep 'pcs'"
    assert_failure
}

@test "VALID_CONTAINERS does NOT include ubuntu-ldms" {
    run bash -c "grep 'VALID_CONTAINERS=' '$BUILD_IMAGES' | grep 'ubuntu-ldms'"
    assert_failure
}

# =============================================================================
# 5. VALID_PARAMS list
# =============================================================================

@test "VALID_PARAMS includes core_tag" {
    run grep 'VALID_PARAMS=' "$BUILD_IMAGES"
    assert_output --partial 'core_tag'
}

@test "VALID_PARAMS includes ldms_tag" {
    run grep 'VALID_PARAMS=' "$BUILD_IMAGES"
    assert_output --partial 'ldms_tag'
}

@test "VALID_PARAMS includes build_tool" {
    run grep 'VALID_PARAMS=' "$BUILD_IMAGES"
    assert_output --partial 'build_tool'
}

@test "VALID_PARAMS includes build_action" {
    run grep 'VALID_PARAMS=' "$BUILD_IMAGES"
    assert_output --partial 'build_action'
}

@test "VALID_PARAMS does NOT include omnia_branch (removed)" {
    run bash -c "grep 'VALID_PARAMS=' '$BUILD_IMAGES' | grep 'omnia_branch'"
    assert_failure
}

@test "VALID_PARAMS does NOT include pcs_tag" {
    run bash -c "grep 'VALID_PARAMS=' '$BUILD_IMAGES' | grep 'pcs_tag'"
    assert_failure
}

@test "VALID_PARAMS does NOT include ubuntu_ldms_tag" {
    run bash -c "grep 'VALID_PARAMS=' '$BUILD_IMAGES' | grep 'ubuntu_ldms_tag'"
    assert_failure
}

# =============================================================================
# 6. Parameter parsing
# =============================================================================

@test "parses core_tag parameter" {
    run grep 'core_tag=' "$BUILD_IMAGES"
    assert_success
    run grep 'CORE_TAG=' "$BUILD_IMAGES"
    assert_success
}

@test "parses build_tool parameter" {
    run grep 'build_tool=' "$BUILD_IMAGES"
    assert_success
    run grep 'BUILD_TOOL=' "$BUILD_IMAGES"
    assert_success
}

@test "parses build_action parameter" {
    run grep 'build_action=' "$BUILD_IMAGES"
    assert_success
    run grep 'BUILD_ACTION=' "$BUILD_IMAGES"
    assert_success
}

@test "no omnia_branch parsing (removed)" {
    run grep 'omnia_branch=' "$BUILD_IMAGES"
    assert_failure
}

@test "no OMNIA_VERSION assignment (removed)" {
    run grep 'OMNIA_VERSION=' "$BUILD_IMAGES"
    assert_failure
}

# =============================================================================
# 7. Input validation
# =============================================================================

@test "validate_container_params function is defined" {
    run grep 'validate_container_params()' "$BUILD_IMAGES"
    assert_success
}

@test "build_tool validation rejects invalid values" {
    run grep 'Invalid build_tool' "$BUILD_IMAGES"
    assert_success
}

@test "build_action validation rejects invalid values" {
    run grep 'Invalid build_action' "$BUILD_IMAGES"
    assert_success
}

@test "push requires docker (not podman)" {
    run grep 'build_action=push requires build_tool=docker' "$BUILD_IMAGES"
    assert_success
}

@test "invalid container error shows available options" {
    run grep 'Invalid container' "$BUILD_IMAGES"
    assert_success
    assert_output --partial 'ldms'
}

@test "invalid container error excludes pcs" {
    run bash -c "grep 'Invalid container' '$BUILD_IMAGES' | grep -w 'pcs'"
    assert_failure
}

# =============================================================================
# 8. CLI dispatch — container groups
# =============================================================================

@test "default dispatch is oim" {
    run grep 'CONTAINER_ARG="${1:-oim}"' "$BUILD_IMAGES"
    assert_success
}

@test "oim builds core + auth + image-builder" {
    run grep -A5 '^\s*oim)' "$BUILD_IMAGES"
    assert_success
    assert_output --partial 'build_omnia_core'
    assert_output --partial 'build_omnia_auth'
    assert_output --partial 'build_image_builder'
}

@test "all builds all containers" {
    run bash -c "sed -n '/^    all)/,/;;/p' '$BUILD_IMAGES'"
    assert_success
    assert_output --partial 'build_omnia_core'
    assert_output --partial 'build_ldms'
    assert_output --partial 'build_kafkapump'
    assert_output --partial 'build_image_builder'
}

@test "telemetry builds kafkapump + victoriapump + telemetry_receiver" {
    run bash -c "sed -n '/^    telemetry)/,/;;/p' '$BUILD_IMAGES'"
    assert_success
    assert_output --partial 'build_kafkapump'
    assert_output --partial 'build_victoriapump'
    assert_output --partial 'build_telemetry_receiver'
}

# =============================================================================
# 9. Comma-separated container support
# =============================================================================

@test "supports comma-separated container list" {
    run grep "IFS=',' read -r -a containers" "$BUILD_IMAGES"
    assert_success
}

@test "comma handler dispatches core" {
    run bash -c "grep -A2 'core).*build_omnia_core' '$BUILD_IMAGES' | tail -1"
    assert_success
}

# =============================================================================
# 10. Build summary
# =============================================================================

@test "calls print_build_summary at the end" {
    run tail -5 "$BUILD_IMAGES"
    assert_output --partial 'print_build_summary'
}

# =============================================================================
# 11. No stale references
# =============================================================================

@test "no pcs references" {
    run grep -i 'pcs' "$BUILD_IMAGES"
    assert_failure
}

@test "no ubuntu-ldms references" {
    run grep 'ubuntu-ldms' "$BUILD_IMAGES"
    assert_failure
}

@test "no ubuntu_ldms references" {
    run grep 'ubuntu_ldms' "$BUILD_IMAGES"
    assert_failure
}

@test "no PCS_TAG" {
    run grep 'PCS_TAG' "$BUILD_IMAGES"
    assert_failure
}

@test "no UBUNTU_LDMS_TAG" {
    run grep 'UBUNTU_LDMS_TAG' "$BUILD_IMAGES"
    assert_failure
}

@test "no omnia-artifactory references" {
    run grep 'omnia-artifactory' "$BUILD_IMAGES"
    assert_failure
}
