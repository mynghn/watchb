from dataclasses import dataclass, fields
from typing import Callable


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


def lazy_load_property(method):
    inst_var = f"_{method.__name__}"

    def cached(instance, *args, **kwargs):
        if not getattr(instance, inst_var, False):
            val = method(instance, *args, **kwargs)
            setattr(instance, inst_var, val)
        return getattr(instance, inst_var)

    return property(cached)


def validate_fields(fields: list[str], validator: Callable):
    def decorator(cls):
        for fname in fields:
            method_name = f"validate_{fname}"
            if defined := getattr(cls, method_name, False):
                setattr(cls, method_name, lambda inst, v: validator(defined(inst, v)))
            else:
                setattr(cls, method_name, lambda inst, v: validator(v))
        return cls

    return decorator
