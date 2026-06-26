#!/usr/bin/env bats
# =============================================================================
# test_omnia_sh_sanity.bats — Tier 4: E2E sanity for omnia.sh
# =============================================================================
# Validates omnia.sh structure, CLI options, function definitions,
# version configuration, and monorepo path correctness.
#
# Usage:  bats test/e2e-sanity/bats/test_omnia_sh_sanity.bats
# =============================================================================

load '../../test_helper/bats-support/load'
load '../../test_helper/bats-assert/load'

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    OMNIA_SH="${REPO_ROOT}/src/main/omnia.sh"
}

# =============================================================================
# 1. File properties
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

@test "omnia.sh is NOT at repo root (moved to src/main/)" {
    [ ! -f "$REPO_ROOT/omnia.sh" ]
}

# =============================================================================
# 2. CLI options
# =============================================================================

@test "help text includes --build option" {
    run grep -- '--build' "$OMNIA_SH"
    assert_success
}

@test "help text includes --install option" {
    run grep -- '--install' "$OMNIA_SH"
    assert_success
}

@test "help text includes --upgrade option" {
    run grep -- '--upgrade' "$OMNIA_SH"
    assert_success
}

@test "help text includes --uninstall option" {
    run grep -- '--uninstall' "$OMNIA_SH"
    assert_success
}

@test "--build|-b case handler exists" {
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

@test "setup_omnia_core() is defined" {
    run grep 'setup_omnia_core()' "$OMNIA_SH"
    assert_success
}

@test "cleanup_omnia_core() is defined" {
    run grep 'cleanup_omnia_core()' "$OMNIA_SH"
    assert_success
}

@test "get_version_from_git_tag() is defined" {
    run grep 'get_version_from_git_tag()' "$OMNIA_SH"
    assert_success
}

@test "validate_version_string() is defined" {
    run grep 'validate_version_string()' "$OMNIA_SH"
    assert_success
}

@test "get_current_omnia_version() is defined" {
    run grep 'get_current_omnia_version()' "$OMNIA_SH"
    assert_success
}

@test "get_container_tag_from_version() is defined" {
    run grep 'get_container_tag_from_version()' "$OMNIA_SH"
    assert_success
}

# =============================================================================
# 4. Version configuration
# =============================================================================

@test "omnia_release is set" {
    run grep 'omnia_release=' "$OMNIA_SH"
    assert_success
}

@test "OMNIA_CORE_CONTAINER_TAG is set" {
    run grep 'OMNIA_CORE_CONTAINER_TAG=' "$OMNIA_SH"
    assert_success
}

@test "ALL_OMNIA_VERSIONS array is defined" {
    run grep 'ALL_OMNIA_VERSIONS=' "$OMNIA_SH"
    assert_success
}

# =============================================================================
# 5. Monorepo path references
# =============================================================================

@test "prepare_upgrade.yml uses /omnia/src/playbooks/upgrade/" {
    run grep '/omnia/src/playbooks/upgrade/prepare_upgrade.yml' "$OMNIA_SH"
    assert_success
}

@test "upgrade.yml uses /omnia/src/playbooks/upgrade/" {
    run grep '/omnia/src/playbooks/upgrade/upgrade.yml' "$OMNIA_SH"
    assert_success
}

@test "oim_cleanup.yml uses /omnia/src/playbooks/utils/" {
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
# 6. No stale pre-monorepo references
# =============================================================================

@test "no omnia-artifactory references" {
    run grep 'omnia-artifactory' "$OMNIA_SH"
    assert_failure
}

@test "no stale /omnia/upgrade/ paths (without src/)" {
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

# =============================================================================
# 7. Upgrade / rollback framework
# =============================================================================

@test "get_available_upgrade_versions() is defined" {
    run grep 'get_available_upgrade_versions()' "$OMNIA_SH"
    assert_success
}

@test "get_available_rollback_versions() is defined" {
    run grep 'get_available_rollback_versions()' "$OMNIA_SH"
    assert_success
}

@test "rollback_same_tag() is defined" {
    run grep 'rollback_same_tag()' "$OMNIA_SH"
    assert_success
}

@test "show_post_upgrade_instructions() is defined" {
    run grep 'show_post_upgrade_instructions()' "$OMNIA_SH"
    assert_success
}
