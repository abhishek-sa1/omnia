#!/usr/bin/env bats
# =============================================================================
# test_container_structure.bats — Tier 1: Unit tests (structure only)
# =============================================================================
# Validates directory layout, file existence, and no stale artifacts.
# No script execution, no content parsing — pure filesystem checks.
#
# Usage:  bats test/unit/bats/test_container_structure.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    CONTAINERS_DIR="${REPO_ROOT}/src/containers"
}

# =============================================================================
# 1. Top-level files
# =============================================================================

@test "src/containers/ directory exists" {
    [ -d "$CONTAINERS_DIR" ]
}

@test "build_images.sh exists" {
    [ -f "${CONTAINERS_DIR}/build_images.sh" ]
}

@test "_common.sh exists" {
    [ -f "${CONTAINERS_DIR}/_common.sh" ]
}

@test "README.md exists" {
    [ -f "${CONTAINERS_DIR}/README.md" ]
}

# =============================================================================
# 2. Container directories — all 8 must exist
# =============================================================================

@test "omnia_core directory exists" {
    [ -d "${CONTAINERS_DIR}/omnia_core" ]
}

@test "omnia_auth directory exists" {
    [ -d "${CONTAINERS_DIR}/omnia_auth" ]
}

@test "omnia_build_stream directory exists" {
    [ -d "${CONTAINERS_DIR}/omnia_build_stream" ]
}

@test "ldms directory exists" {
    [ -d "${CONTAINERS_DIR}/ldms" ]
}

@test "kafkapump directory exists" {
    [ -d "${CONTAINERS_DIR}/kafkapump" ]
}

@test "victoriapump directory exists" {
    [ -d "${CONTAINERS_DIR}/victoriapump" ]
}

@test "telemetry_receiver directory exists" {
    [ -d "${CONTAINERS_DIR}/telemetry_receiver" ]
}

@test "image_builder directory exists" {
    [ -d "${CONTAINERS_DIR}/image_builder" ]
}

# =============================================================================
# 3. Each container has a build.sh
# =============================================================================

@test "omnia_core/build.sh exists" {  [ -f "${CONTAINERS_DIR}/omnia_core/build.sh" ]; }
@test "omnia_auth/build.sh exists" {  [ -f "${CONTAINERS_DIR}/omnia_auth/build.sh" ]; }
@test "omnia_build_stream/build.sh exists" {  [ -f "${CONTAINERS_DIR}/omnia_build_stream/build.sh" ]; }
@test "ldms/build.sh exists" {  [ -f "${CONTAINERS_DIR}/ldms/build.sh" ]; }
@test "kafkapump/build.sh exists" {  [ -f "${CONTAINERS_DIR}/kafkapump/build.sh" ]; }
@test "victoriapump/build.sh exists" {  [ -f "${CONTAINERS_DIR}/victoriapump/build.sh" ]; }
@test "telemetry_receiver/build.sh exists" {  [ -f "${CONTAINERS_DIR}/telemetry_receiver/build.sh" ]; }
@test "image_builder/build.sh exists" {  [ -f "${CONTAINERS_DIR}/image_builder/build.sh" ]; }

# =============================================================================
# 4. Containerfiles exist
# =============================================================================

@test "omnia_core/Containerfile exists" {  [ -f "${CONTAINERS_DIR}/omnia_core/Containerfile" ]; }
@test "omnia_auth/Containerfile exists" {  [ -f "${CONTAINERS_DIR}/omnia_auth/Containerfile" ]; }
@test "omnia_build_stream/Containerfile exists" {  [ -f "${CONTAINERS_DIR}/omnia_build_stream/Containerfile" ]; }
@test "ldms/Containerfile.bld_n_run.ubuntu26.04 exists" {  [ -f "${CONTAINERS_DIR}/ldms/Containerfile.bld_n_run.ubuntu26.04" ]; }
@test "image_builder/Containerfile.el10 exists" {  [ -f "${CONTAINERS_DIR}/image_builder/Containerfile.el10" ]; }

# =============================================================================
# 5. Supporting files
# =============================================================================

@test "omnia_core/entrypoint.sh exists" {  [ -f "${CONTAINERS_DIR}/omnia_core/entrypoint.sh" ]; }
@test "omnia_core/cert-copy.sh exists" {  [ -f "${CONTAINERS_DIR}/omnia_core/cert-copy.sh" ]; }
@test "omnia_core/pyproject.toml exists" {  [ -f "${CONTAINERS_DIR}/omnia_core/pyproject.toml" ]; }
@test "omnia_core/uv.lock exists" {  [ -f "${CONTAINERS_DIR}/omnia_core/uv.lock" ]; }
@test "omnia_build_stream/init_s3cfg.sh exists" {  [ -f "${CONTAINERS_DIR}/omnia_build_stream/init_s3cfg.sh" ]; }
@test "omnia_build_stream/pyproject.toml exists" {  [ -f "${CONTAINERS_DIR}/omnia_build_stream/pyproject.toml" ]; }
@test "omnia_build_stream/uv.lock exists" {  [ -f "${CONTAINERS_DIR}/omnia_build_stream/uv.lock" ]; }
@test "ldms/configure.aggregator.sh exists" {  [ -f "${CONTAINERS_DIR}/ldms/configure.aggregator.sh" ]; }
@test "image_builder/requirements.txt exists" {  [ -f "${CONTAINERS_DIR}/image_builder/requirements.txt" ]; }

# =============================================================================
# 6. No stale Dockerfiles (migration complete)
# =============================================================================

@test "no Dockerfile under src/containers/" {
    run find "${CONTAINERS_DIR}" -maxdepth 2 -name "Dockerfile" -type f
    assert_output ""
}

@test "no Dockerfile.* under src/containers/" {
    run find "${CONTAINERS_DIR}" -maxdepth 2 -name "Dockerfile.*" -type f
    assert_output ""
}

# =============================================================================
# 7. Removed / renamed containers must not exist
# =============================================================================

@test "omnia_pcs directory does not exist (removed)" {  [ ! -d "${CONTAINERS_DIR}/omnia_pcs" ]; }
@test "ubuntu_ldms directory does not exist (renamed)" {  [ ! -d "${CONTAINERS_DIR}/ubuntu_ldms" ]; }
