#!/usr/bin/env bats
# =============================================================================
# test_containerfile_security.bats — Tier 3: NFT security checks
# =============================================================================
# Validates Containerfiles for security best practices:
# no hardcoded credentials, no root-only USER, CVE fix patterns, etc.
#
# Usage:  bats test/nft/bats/test_containerfile_security.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    CONTAINERS_DIR="${REPO_ROOT}/src/containers"
}

# =============================================================================
# 1. No hardcoded passwords or secrets
# =============================================================================

@test "omnia_core/Containerfile has no hardcoded PASSWORD" {
    run bash -c "grep -i 'PASSWORD=' '${CONTAINERS_DIR}/omnia_core/Containerfile' | grep -v 'ARG\|ENV.*=\$\|#'"
    assert_failure
}

@test "omnia_build_stream/Containerfile has no hardcoded PASSWORD" {
    run bash -c "grep -i 'PASSWORD=' '${CONTAINERS_DIR}/omnia_build_stream/Containerfile' | grep -v 'ARG\|ENV.*=\$\|#'"
    assert_failure
}

@test "omnia_auth/Containerfile has no hardcoded PASSWORD" {
    run bash -c "grep -i 'PASSWORD=' '${CONTAINERS_DIR}/omnia_auth/Containerfile' | grep -v 'ARG\|ENV.*=\$\|#'"
    assert_failure
}

# =============================================================================
# 2. No hardcoded API keys or tokens
# =============================================================================

@test "no hardcoded API_KEY in any Containerfile" {
    run bash -c "find '${CONTAINERS_DIR}' -name 'Containerfile*' -exec grep -l 'API_KEY=' {} \\; | grep -v '#'"
    assert_output ""
}

@test "no hardcoded SECRET in any Containerfile" {
    run bash -c "find '${CONTAINERS_DIR}' -name 'Containerfile*' -exec grep -l 'SECRET_KEY=.' {} \\; | grep -v '#'"
    assert_output ""
}

# =============================================================================
# 3. No ADD instruction (prefer COPY)
# =============================================================================

@test "omnia_core/Containerfile uses COPY not ADD for local files" {
    run bash -c "grep '^ADD ' '${CONTAINERS_DIR}/omnia_core/Containerfile' | grep -v 'http'"
    assert_failure
}

@test "omnia_build_stream/Containerfile uses COPY not ADD for local files" {
    run bash -c "grep '^ADD ' '${CONTAINERS_DIR}/omnia_build_stream/Containerfile' | grep -v 'http'"
    assert_failure
}

# =============================================================================
# 4. Package cache cleanup
# =============================================================================

@test "omnia_core/Containerfile cleans dnf cache" {
    run grep 'dnf clean\|rm.*cache' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

@test "omnia_auth/Containerfile cleans dnf cache" {
    run grep 'dnf clean\|rm.*cache' "${CONTAINERS_DIR}/omnia_auth/Containerfile"
    assert_success
}

# =============================================================================
# 5. Security labels (if present)
# =============================================================================

@test "omnia_core/Containerfile has security-related labels" {
    run grep -i 'security\|LABEL' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_success
}

# =============================================================================
# 6. No .git directories copied
# =============================================================================

@test "omnia_core/Containerfile does not COPY .git" {
    run grep 'COPY.*\.git' "${CONTAINERS_DIR}/omnia_core/Containerfile"
    assert_failure
}

# =============================================================================
# 7. No curl | bash anti-pattern
# =============================================================================

@test "omnia_core/Containerfile has no curl|bash pattern" {
    run bash -c "grep 'curl.*|.*bash\|wget.*|.*bash' '${CONTAINERS_DIR}/omnia_core/Containerfile'"
    assert_failure
}

@test "omnia_build_stream/Containerfile has no curl|bash pattern" {
    run bash -c "grep 'curl.*|.*bash\|wget.*|.*bash' '${CONTAINERS_DIR}/omnia_build_stream/Containerfile'"
    assert_failure
}

# =============================================================================
# 8. Supporting scripts are not world-writable
# =============================================================================

@test "omnia_core/entrypoint.sh is not world-writable" {
    local perms
    perms=$(stat -c '%a' "${CONTAINERS_DIR}/omnia_core/entrypoint.sh" 2>/dev/null || stat -f '%Lp' "${CONTAINERS_DIR}/omnia_core/entrypoint.sh" 2>/dev/null || echo "skip")
    if [ "$perms" = "skip" ]; then
        skip "stat not available"
    fi
    [[ ! "$perms" =~ [2367]$ ]]
}
