#!/usr/bin/env bats
# =============================================================================
# test_container_build_sanity.bats — Tier 4: E2E sanity for container builds
# =============================================================================
# Validates Containerfile content, FROM instructions, LABEL metadata,
# multi-stage builds, COPY directives, and build readiness.
#
# Usage:  bats test/e2e-sanity/bats/test_container_build_sanity.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    CONTAINERS_DIR="${REPO_ROOT}/src/containers"
}

# =============================================================================
# 1. FROM instructions — base images defined
# =============================================================================

@test "omnia_core/Containerfile has FROM instruction" {
    run grep -c '^FROM ' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_auth/Containerfile has FROM instruction" {
    run grep -c '^FROM ' "${CONTAINERS_DIR}/omnia_auth/Containerfile"
    assert_success
}

@test "omnia_build_stream/Containerfile has FROM instruction" {
    run grep -c '^FROM ' "${CONTAINERS_DIR}/omnia_build_stream/Containerfile"
    assert_success
}

@test "ldms/Containerfile is multi-stage (2+ FROM)" {
    local count
    count=$(grep -c '^FROM ' "${CONTAINERS_DIR}/ldms/Containerfile.bld_n_run.ubuntu26.04")
    [ "$count" -ge 2 ]
}

@test "image_builder/Containerfile.el10 has FROM instruction" {
    run grep -c '^FROM ' "${CONTAINERS_DIR}/image_builder/Containerfile.el10"
    assert_success
}

# =============================================================================
# 2. LABEL / OCI metadata
# =============================================================================

@test "omnia_core/Containerfile has LABEL instruction" {
    run grep '^LABEL ' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_build_stream/Containerfile has OCI labels" {
    run grep 'org.opencontainers.image' "${CONTAINERS_DIR}/omnia_build_stream/Containerfile"
    assert_success
}

# =============================================================================
# 3. Python tooling
# =============================================================================

@test "omnia_core/Containerfile installs Python uv" {
    run grep 'uv' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_core/Containerfile COPYs pyproject.toml" {
    run grep 'COPY.*pyproject.toml' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_build_stream/Containerfile COPYs pyproject.toml" {
    run grep 'COPY.*pyproject.toml' "${CONTAINERS_DIR}/omnia_build_stream/Containerfile"
    assert_success
}

# =============================================================================
# 4. Container-specific requirements
# =============================================================================

@test "omnia_core/Containerfile configures SSH" {
    run grep 'sshd_config' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_auth/Containerfile installs openldap" {
    run grep -i 'openldap' "${CONTAINERS_DIR}/omnia_auth/Containerfile"
    assert_success
}

@test "omnia_core/Containerfile has EXPOSE instruction" {
    run grep '^EXPOSE' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_core/Containerfile has WORKDIR instruction" {
    run grep '^WORKDIR' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_build_stream/Containerfile has WORKDIR instruction" {
    run grep '^WORKDIR' "${CONTAINERS_DIR}/omnia_build_stream/Containerfile"
    assert_success
}

# =============================================================================
# 5. Entrypoint / CMD
# =============================================================================

@test "omnia_core/Containerfile has entrypoint or CMD" {
    run bash -c "grep -E '^(ENTRYPOINT|CMD)' '${CONTAINERS_DIR}/omnia_core/Containerfile'"
    assert_success
}

@test "omnia_auth/Containerfile has entrypoint or CMD" {
    run bash -c "grep -E '^(ENTRYPOINT|CMD)' '${CONTAINERS_DIR}/omnia_auth/Containerfile'"
    assert_success
}

@test "omnia_build_stream/Containerfile has entrypoint or CMD" {
    run bash -c "grep -E '^(ENTRYPOINT|CMD)' '${CONTAINERS_DIR}/omnia_build_stream/Containerfile'"
    assert_success
}

# =============================================================================
# 6. COPY directives — supporting files referenced
# =============================================================================

@test "omnia_core/Containerfile copies entrypoint.sh" {
    run grep 'COPY.*entrypoint.sh' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_core/Containerfile copies cert-copy.sh" {
    run grep 'COPY.*cert-copy.sh' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_build_stream/Containerfile copies init_s3cfg.sh" {
    run grep 'COPY.*init_s3cfg.sh' "${CONTAINERS_DIR}/omnia_build_stream/Containerfile"
    assert_success
}

# =============================================================================
# 7. No stale Dockerfile references inside Containerfiles
# =============================================================================

@test "omnia_core/Containerfile has no stale Dockerfile comment" {
    run bash -c "grep -i 'dockerfile' '${CONTAINERS_DIR}/omnia_core/Containerfile' | grep -v '#.*[Cc]ontainerfile'"
    assert_failure
}

@test "omnia_build_stream/Containerfile has no stale Dockerfile instruction" {
    run bash -c "grep -i 'dockerfile' '${CONTAINERS_DIR}/omnia_build_stream/Containerfile' | grep -v '^#\|^[[:space:]]*#'"
    assert_failure
}
