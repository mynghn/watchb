from dataclasses import dataclass, fields


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
