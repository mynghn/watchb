from dataclasses import dataclass, fields
from typing import Optional


def flexible_dataclass(cls=None, /, **kwargs):
    def decorator(cls):
        cls = dataclass(cls, **kwargs)
        cls.__init__.__qualname__ = f"{cls.__qualname__}.__default_init__"
        setattr(cls, "__default_init__", cls.__init__)

        def __flexible_init__(self, *args, **kwargs):
            filtered_kwargs = {
                f.name: kwargs[f.name] for f in fields(cls) if f.name in kwargs.keys()
            }
            self.__default_init__(*args, **filtered_kwargs)

        __flexible_init__.__qualname__ = f"{cls.__qualname__}.__init__"
        setattr(cls, "__init__", __flexible_init__)

        return cls

    if cls is None:
        return decorator

    return decorator(cls)


def lazy_load(
    method=None,
    /,
    variable_name: Optional[str] = None,
):
    def decorator(method):
        inst_var = variable_name or f"_{method.__name__}"

        def cached(instance, *args, **kwargs):
            if not getattr(instance, inst_var, False):
                val = method(instance, *args, **kwargs)
                setattr(instance, inst_var, val)
            return getattr(instance, inst_var)

        return cached

    if method is None:
        return decorator
    else:
        return decorator(method)
