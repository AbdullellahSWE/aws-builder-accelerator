#!/usr/bin/env bash
set -euo pipefail

# The cdk-nag rule pack runs as part of synth, so an unacknowledged finding
# fails here. NOTE: inert until you uncomment the plugin in app.py.
echo "== cdk-nag =="
uv run cdk synth --quiet

# Advisories appear without any change from us, so a new CVE shouldn't block
# an unrelated deploy. Report it so it gets triaged, but keep going.
echo "== dependency scan =="
uv run pip-audit || echo "WARNING: pip-audit reported vulnerabilities, triage them"
(cd ui && npm audit --audit-level=high) || echo "WARNING: npm audit reported vulnerabilities, triage them"