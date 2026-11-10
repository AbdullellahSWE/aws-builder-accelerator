# ASH Security Scan Report

- **Report generated**: 2026-11-10T20:44:39+00:00
- **Time since scan**: 4 minutes

## Scan Metadata

- **Project**: ASH
- **Scan executed**: 2026-11-10T20:40:12+00:00
- **ASH version**: 3.7.0

## Summary

### Scanner Results

The table below shows findings by scanner, with status based on severity thresholds and dependencies:

- **Severity levels**:
  - **Suppressed (S)**: Findings that have been explicitly suppressed and don't affect scanner status
  - **Critical (C)**: Highest severity findings that require immediate attention
  - **High (H)**: Serious findings that should be addressed soon
  - **Medium (M)**: Moderate risk findings
  - **Low (L)**: Lower risk findings
  - **Info (I)**: Informational findings with minimal risk
- **Duration (Time)**: Time taken by the scanner to complete its execution
- **Actionable**: Number of findings at or above the threshold severity level that require attention
- **Result**:
  - **PASSED** = No findings at or above threshold
  - **FAILED** = Findings at or above threshold
  - **MISSING** = Required dependencies not available
  - **SKIPPED** = Scanner explicitly disabled
  - **ERROR** = Scanner execution error
- **Threshold**: The minimum severity level that will cause a scanner to fail
  - Thresholds: ALL, LOW, MEDIUM, HIGH, CRITICAL
  - Source: Values in parentheses indicate where the threshold is set:
    - `global` (global_settings section in the ASH_CONFIG used)
    - `config` (scanner config section in the ASH_CONFIG used)
    - `scanner` (default configuration in the plugin, if explicitly set)
- **Statistics calculation**:
  - All statistics are calculated from the final aggregated SARIF report
  - Suppressed findings are counted separately and do not contribute to actionable findings
  - Scanner status is determined by comparing actionable findings to the threshold

| Scanner | Suppressed | Critical | High | Medium | Low | Info | Actionable | Result | Threshold |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| bandit | 0 | 0 | 0 | 0 | 0 | 0 | 0 | PASSED | MEDIUM (global) |
| cdk-nag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | MISSING | MEDIUM (global) |
| cfn-nag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | MISSING | MEDIUM (global) |
| checkov | 0 | 0 | 0 | 0 | 0 | 0 | 0 | PASSED | MEDIUM (global) |
| detect-secrets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | PASSED | MEDIUM (global) |
| grype | 0 | 0 | 0 | 0 | 0 | 0 | 0 | MISSING | MEDIUM (global) |
| npm-audit | 0 | 0 | 0 | 9 | 0 | 0 | 9 | FAILED | MEDIUM (global) |
| opengrep | 0 | 0 | 0 | 0 | 0 | 0 | 0 | MISSING | MEDIUM (global) |
| semgrep | 0 | 0 | 0 | 0 | 0 | 0 | 0 | PASSED | MEDIUM (global) |
| syft | 0 | 0 | 0 | 0 | 0 | 0 | 0 | MISSING | MEDIUM (global) |

### Top 9 Hotspots

Files with the highest number of security findings:

| Finding Count | File Location |
| ---: | --- |
| 1 | node_modules/typescript-eslint/@typescript-eslint/eslint-plugin/package.json |
| 1 | node_modules/typescript-eslint/@typescript-eslint/parser/package.json |
| 1 | node_modules/typescript-eslint/@typescript-eslint/eslint-plugin/@typescript-eslint/type-utils/package.json |
| 1 | node_modules/typescript-eslint/@typescript-eslint/eslint-plugin/@typescript-eslint/type-utils/@typescript-eslint/typescript-estree/package.json |
| 1 | node_modules/typescript-eslint/@typescript-eslint/parser/@typescript-eslint/typescript-estree/package.json |
| 1 | node_modules/typescript-eslint/@typescript-eslint/utils/@typescript-eslint/typescript-estree/package.json |
| 1 | node_modules/typescript-eslint/@typescript-eslint/utils/package.json |
| 1 | node_modules/typescript-eslint/minimatch/package.json |
| 1 | node_modules/typescript-eslint/package.json |

<h2>Detailed Findings</h2>

<details>
<summary>Show 9 actionable findings</summary>

### Finding 1: npm-audit-transitive-@typescript-eslint/eslint-plugin

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-@typescript-eslint/eslint-plugin
- **Location**: node_modules/typescript-eslint/@typescript-eslint/eslint-plugin/package.json:1

**Description**:
Transitive vulnerability in @typescript-eslint/eslint-plugin (via @typescript-eslint/parser, @typescript-eslint/type-utils, @typescript-eslint/utils) 6.16.0 - 8.72.2

---

### Finding 2: npm-audit-transitive-@typescript-eslint/parser

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-@typescript-eslint/parser
- **Location**: node_modules/typescript-eslint/@typescript-eslint/parser/package.json:1

**Description**:
Transitive vulnerability in @typescript-eslint/parser (via @typescript-eslint/typescript-estree) 6.16.0 - 8.72.2

---

### Finding 3: npm-audit-transitive-@typescript-eslint/type-utils

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-@typescript-eslint/type-utils
- **Location**: node_modules/typescript-eslint/@typescript-eslint/eslint-plugin/@typescript-eslint/type-utils/package.json:1

**Description**:
Transitive vulnerability in @typescript-eslint/type-utils (via @typescript-eslint/typescript-estree, @typescript-eslint/utils) 6.16.0 - 8.72.2

---

### Finding 4: npm-audit-transitive-@typescript-eslint/typescript-estree

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-@typescript-eslint/typescript-estree
- **Location**: node_modules/typescript-eslint/@typescript-eslint/eslint-plugin/@typescript-eslint/type-utils/@typescript-eslint/typescript-estree/package.json:1

**Description**:
Transitive vulnerability in @typescript-eslint/typescript-estree (via minimatch) 6.16.0 - 8.72.2

---

### Finding 5: npm-audit-transitive-@typescript-eslint/typescript-estree

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-@typescript-eslint/typescript-estree
- **Location**: node_modules/typescript-eslint/@typescript-eslint/parser/@typescript-eslint/typescript-estree/package.json:1

**Description**:
Transitive vulnerability in @typescript-eslint/typescript-estree (via minimatch) 6.16.0 - 8.72.2

---

### Finding 6: npm-audit-transitive-@typescript-eslint/typescript-estree

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-@typescript-eslint/typescript-estree
- **Location**: node_modules/typescript-eslint/@typescript-eslint/utils/@typescript-eslint/typescript-estree/package.json:1

**Description**:
Transitive vulnerability in @typescript-eslint/typescript-estree (via minimatch) 6.16.0 - 8.72.2

---

### Finding 7: npm-audit-transitive-@typescript-eslint/utils

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-@typescript-eslint/utils
- **Location**: node_modules/typescript-eslint/@typescript-eslint/utils/package.json:1

**Description**:
Transitive vulnerability in @typescript-eslint/utils (via @typescript-eslint/typescript-estree) 6.16.0 - 8.72.2

---

### Finding 8: GHSA-g3hv-75wg-m249

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: GHSA-g3hv-75wg-m249
- **Location**: node_modules/typescript-eslint/minimatch/package.json:1

**Description**:
minimatch has potential denial of service via globparts amplification in minimatch 7.0.0 - 11.0.0. https://github.com/advisories/GHSA-g3hv-75wg-m249

---

### Finding 9: npm-audit-transitive-typescript-eslint

- **Severity**: MEDIUM
- **Scanner**: npm-audit
- **Rule ID**: npm-audit-transitive-typescript-eslint
- **Location**: node_modules/typescript-eslint/package.json:1

**Description**:
Transitive vulnerability in typescript-eslint (via @typescript-eslint/eslint-plugin, @typescript-eslint/parser, @typescript-eslint/utils) <=8.72.2

</details>

---

*Report generated by [Automated Security Helper (ASH)](https://github.com/awslabs/automated-security-helper) at 2026-11-10T20:44:39+00:00*