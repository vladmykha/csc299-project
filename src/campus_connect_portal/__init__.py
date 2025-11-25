"""Campus Connect Grading Portal Interface package."""

from importlib import metadata

try:
    __version__ = metadata.version("campus-connect-grading-portal-interface")
except metadata.PackageNotFoundError:  # pragma: no cover - local dev
    __version__ = "0.0.0"

__all__ = ["__version__"]
