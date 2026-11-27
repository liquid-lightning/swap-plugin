"""Makes tests/'s pyln-testing fixtures (node_factory, bitcoind, ...) and
helper modules (fixtures, utils, test_liquid_asset_poc) importable from
this directory, the same way tests/pytest.ini's `pythonpath = .` does for
the top-level tests/ dir -- this directory has no such ini of its own
(and doesn't want tests/pytest.ini's, which is scoped to its own dir), so
the path has to be added explicitly here, before any test_*.py in this
directory imports from those modules.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def cln_tests_dir():
    """CLN's tests/ directory: $CLN_TESTS_DIR, $LIGHTNING_SRC/tests, the tree
    this repository was copied into (plugins/assetswap-plugin of a CLN
    checkout, as devedition's build does), or a sibling checkout
    (../../lightning next to this repository)."""
    candidates = [os.environ.get('CLN_TESTS_DIR'),
                  os.path.join(os.environ['LIGHTNING_SRC'], 'tests') if os.environ.get('LIGHTNING_SRC') else None,
                  os.path.join(HERE, '..', '..', '..', 'tests'),
                  os.path.join(HERE, '..', '..', '..', 'lightning', 'tests')]
    for c in candidates:
        if c and os.path.isfile(os.path.join(c, 'fixtures.py')):
            return os.path.normpath(c)
    raise RuntimeError("CLN's tests/ directory not found: set CLN_TESTS_DIR or LIGHTNING_SRC")


TESTS_DIR = cln_tests_dir()
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)
