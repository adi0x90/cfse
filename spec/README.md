# CFSE Specification

**Version:** 1.0.0
**Status:** Stable

## Overview

This directory contains the normative specification for Concept Flow Scenarios Explorations (CFSE)—a formal methodology for security epistemology.

CFSE provides an artifact protocol and workflow for building a world model of a system, stating security properties as invariants, and validating hypotheses with evidence-linked explorations.

If you’re new, start with `../guides/foundations/introduction.md` and `foundations/artifact-system.md`.

## Structure

| Directory | Content | Purpose |
|-----------|---------|---------|
| foundations/ | Core framework rules | Artifact pipeline, conformance, extensions |
| grammar/ | Syntax rules | ID patterns, reference syntax, formal logic |
| artifacts/ | Artifact definitions | Schema + prose for each artifact type |
| semantics/ | Interpretation rules | States, verdicts, traceability |

## Normative Language

This specification uses RFC-style keywords (RFC 2119 + RFC 8174) when, and only when, they appear in all capitals:

| Term | Meaning |
|------|---------|
| MUST | Absolute requirement |
| MUST NOT | Absolute prohibition |
| SHOULD | Default unless good reason to deviate |
| SHOULD NOT | Discouraged unless good reason to deviate |
| MAY | Truly optional |

## Conformance

See [foundations/conformance.md](foundations/conformance.md) for conformance levels.

## Versioning

This spec follows [Semantic Versioning](https://semver.org/). See [changelog.md](changelog.md).

## Extensions (Optional)

CFSE supports opt-in extensions to add workflows and artifact types without bloating the core spec.

- Extension rules: `foundations/extensions.md`
- See `../extensions/README.md` for extension packaging notes.

## Proposals

Draft proposals (RFCs) live at the repository root in `rfcs/`. These documents are not yet normative; they exist to capture problems, analysis, and proposed spec changes before being incorporated into core sections.

- Start here: `../rfcs/PROPOSALS.md`
