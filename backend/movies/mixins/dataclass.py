import re
from dataclasses import Field, fields, is_dataclass
from importlib import import_module
from typing import Literal, NewType, Type, Union, get_args, get_origin, get_type_hints

from ..decorators import lazy_load_property


class TypeHintsMixin:
    @lazy_load_property
    def type_hints(self) -> dict[str, Type]:
        try:
            return get_type_hints(self)
        except NameError as e:
            return self._error_handling(e)

    def _error_handling(self, e: NameError) -> dict[str, Type]:
        name = re.search(
            r"(?<=name ')[a-zA-Z_][a-zA-Z0-9_]*(?=' is not defined)", e.args[0]
        ).group(0)
        _g = globals()
        _g[name] = getattr(import_module("movies.custom_types"), name)
        return self._with_args_kwargs(globalns=_g)

    def _with_args_kwargs(self, *args, **kwargs) -> dict[str, Type]:
        try:
            return get_type_hints(self, *args, **kwargs)
        except NameError as e:
            return self._error_handling(e)


class EmptyStringToNoneMixin(TypeHintsMixin):
    def is_optional_string_field(self, field: Field) -> bool:
        ftype = self.type_hints.get(field.name)
        origin_check = get_origin(ftype) is Union
        args_check = get_args(ftype) == (str, type(None))
        return origin_check and args_check

    def get_optional_string_fields(self) -> list[Field]:
        return [f for f in fields(self) if self.is_optional_string_field(f)]

    def __post_init__(self):
        if hasattr(super(), "__post_init__"):
            super().__post_init__()

        for f in self.get_optional_string_fields():
            if getattr(self, f.name) == "":
                setattr(self, f.name, None)


DataClass = NewType("DataClass", object)
ArrayLike = list | tuple | set | frozenset
DataClassArray = (
    list[DataClass] | tuple[DataClass, ...] | set[DataClass] | frozenset[DataClass]
)


class NestedInitMixin(TypeHintsMixin):
    def is_nested_field(self, field: Field) -> Literal[0, 1, 2]:
        """
        return type:
          - 0: not a dataclass nested field or complex typed array
          - 1: dataclass nested in array like field
          - 2: bare dataclass field
        """
        ftype = self.get_field_type(field)
        if is_dataclass(ftype):
            return 2
        else:

            origin_check = (origin_type := get_origin(ftype)) in get_args(ArrayLike)
            args_check = (
                len(arg_types := get_args(ftype)) == 1
                or (
                    isinstance(origin_type, tuple)
                    and len(arg_types) == 2
                    and arg_types[1] == Ellipsis
                )
            ) and is_dataclass(arg_types[0])
            return int(origin_check and args_check)

    def get_nested_fields(self) -> list[tuple[Field, int]]:
        return [(f, case) for f in fields(self) if (case := self.is_nested_field(f))]

    def get_field_type(self, field: Field) -> Type:
        return self.type_hints[field.name]

    def to_dataclass_array(
        self, curr: ArrayLike, dataclass: DataClass
    ) -> DataClassArray:
        new = []
        for inner in curr:
            if is_dataclass(inner):
                new.append(inner)
            else:
                converted = self.to_dataclass(curr=inner, dataclass=dataclass)
                new.append(converted)

        return type(curr)(new)

    def to_dataclass(self, curr: dict | ArrayLike, dataclass: DataClass) -> DataClass:
        if is_dataclass(curr):
            return curr
        else:
            if isinstance(curr, dict):
                return dataclass(**curr)
            elif isinstance(curr, ArrayLike):
                return dataclass(*curr)
            else:
                raise TypeError(
                    f"Dataclass({dataclass.__name__}) incompatible type encountered: {curr}"
                )

    def __post_init__(self):
        if hasattr(super(), "__post_init__"):
            super().__post_init__()
        for f, case in self.get_nested_fields():
            curr = getattr(self, f.name)
            ftype = self.get_field_type(f)
            if case == 1:
                if any([not is_dataclass(inner) for inner in curr]):
                    setattr(
                        self,
                        f.name,
                        self.to_dataclass_array(curr, dataclass=get_args(ftype)[0]),
                    )
            elif case == 2:
                if not is_dataclass(curr):
                    setattr(
                        self,
                        f.name,
                        self.to_dataclass(curr, dataclass=ftype),
                    )
            else:
                raise ValueError(f"Unexpected nested field case encoutnered: {case}")
