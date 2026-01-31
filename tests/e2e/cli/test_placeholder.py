"""
Placeholder E2E test.

This file exists to prevent pytest from failing when the e2e directory is empty.
Real E2E tests should be added here that test the full CLI workflow with actual
API calls (requires credentials).
"""

import pytest


@pytest.mark.e2e
def test_e2e_placeholder():
    """Placeholder test to prevent empty test directory errors."""
    # This test always passes
    # TODO: Add real E2E tests that test the full CLI workflow
    assert True, "E2E tests directory exists but no real tests implemented yet"
