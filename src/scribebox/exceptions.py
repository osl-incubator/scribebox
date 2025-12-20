"""Custom exceptions used by Scribebox."""

from __future__ import annotations


class ScribeboxError(Exception):
    """Base exception for the project."""


class DependencyMissingError(ScribeboxError):
    """Raised when an optional dependency is not installed."""


class ExternalToolError(ScribeboxError):
    """Raised when an external tool (e.g., ffmpeg) fails."""


class InvalidInputError(ScribeboxError):
    """Raised when input parameters are invalid."""
