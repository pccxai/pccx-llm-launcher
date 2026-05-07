"""PCCX launcher support package."""

__all__ = [
    "AxiError",
    "GemmaError",
    "KV260Error",
    "PCCXLauncherError",
    "TraceError",
]


def __getattr__(name: str) -> object:
    if name in __all__:
        from . import errors

        return getattr(errors, name)
    raise AttributeError(name)
