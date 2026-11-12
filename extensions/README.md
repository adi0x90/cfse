# CFSE Extensions

This directory contains optional extensions to the CFSE core specification.

Extensions are opt-in and MUST be declared by a corpus. See `spec/foundations/extensions.md` for the normative rules.

This public repository may include zero or more extension packages over time. Extensions can also be published separately.

## Optional execution tooling

[Finite-trace profile](finite-trace/README.md) supplies a bounded, opt-in reference
evaluator and synthetic fixtures. It adds no core artifact fields or extension
namespace and does not claim full core semantic conformance.
