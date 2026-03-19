def __getattr__(name: str):
    if name in {"app", "main"}:
        from .main import app, main

        return {"app": app, "main": main}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["app", "main"]
