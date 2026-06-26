#!/bin/bash
# =============================================================================
# Install BATS helper libraries into test/test_helper/
# =============================================================================
# Usage:  bash test/test_helper/install.sh
# Run once. Libraries are vendored locally (no git submodules).
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_helper() {
    local name="$1"
    local repo="$2"
    local dest="$SCRIPT_DIR/$name"

    if [ -d "$dest" ] && [ -f "$dest/load.bash" ]; then
        echo "✓ $name already installed at $dest"
        return 0
    fi

    echo "Installing $name..."
    rm -rf "$dest"
    git clone --depth 1 "$repo" "$dest"
    rm -rf "$dest/.git"
    echo "✓ $name installed (vendored, no .git)"
}

install_helper "bats-support" "https://github.com/bats-core/bats-support.git"
install_helper "bats-assert"  "https://github.com/bats-core/bats-assert.git"

echo ""
echo "Done. Run tests with:"
echo "  bats test/system/main/bats/test_omnia_sh.bats"
