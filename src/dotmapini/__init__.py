from __future__ import annotations
import ast
from collections import deque
from collections.abc import MutableMapping
from configparser import ConfigParser, SectionProxy
from typing import (
    TYPE_CHECKING,
    Any,
    Deque,
    Dict,
    ItemsView,
    Iterator,
    KeysView,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    ValuesView,
)

from .exceptions import DigitInSectionNameError


if TYPE_CHECKING:
    from pathlib import Path


__all__ = ('Config', 'DigitInSectionNameError')


VT = TypeVar('VT', str, bool, int, float, bytes, Tuple, List, Dict, Set, None)
_VT = TypeVar('_VT')
VTConfig = Union[VT, 'Config']


class Config(MutableMapping[str, VTConfig]):
    def __init__(
        self,
        dict_: Union[ConfigParser, SectionProxy, Dict[str, SectionProxy], Dict[str, VTConfig]],
        ) -> None:
        for key, value in dict_.items():
            remaining_attributes: Deque[str] = deque(key.split(sep='.'))  # split section by dot
            attribute: str = remaining_attributes.popleft()  # get first attribute name in section
            # Below <instance> is a self.__dict__ object, that we define to
            # manipulate with and not to overwrite existing Config attributes.
            instance, attribute = self._define_instance_and_attribute(
                attribute=attribute,
                remaining_attributes=remaining_attributes,
                )
            if attribute.isdigit():
                raise DigitInSectionNameError(f"Wrong attribute name <{attribute}> in {value!r}.\nInstance attribute should be string without digit. Only digits in section's names doesn't allowed.")
            instance[attribute] = self._parse_value(
                remaining_attributes=remaining_attributes,
                key=key,
                value=value,
                dict_=dict_,
                )

    @classmethod
    def _parse_value(
            cls,
            /,
            *,
            remaining_attributes: Deque[str],
            key: str,
            value: Union[SectionProxy, VTConfig],
            dict_: Union[ConfigParser, SectionProxy, Dict[str, SectionProxy], Dict[str, VTConfig]],
            ) -> VTConfig:
        """Allow to convert datatypes on our own, as mentioned in configparser source docs:
            Config parsers do not guess datatypes of values in configuration files,
            always storing them internally as strings. This means that if you need
            other datatypes, you should convert on your own.
            See: https://docs.python.org/3/library/configparser.html#supported-datatypes
        Additionally converts Python values properly presented in .ini options as corresponding
        Python datatypes using ast.literal_eval. Keeps value as string if values NOT properly
        presented in .ini.

        Return parsed value datatypes:
            VTConfig = Union[Config, str, bool, int, float, bytes, tuple, list, dict, set, None]

        IMPORTANT! Be aware of: https://github.com/python/cpython/blob/99bc8589f09e66682a52df1f1a9598c7056d49dd/Lib/ast.py#L63
        """
        if remaining_attributes:  # -> Config
            return cls(
                    dict_={'.'.join(remaining_attributes): value},
                    )  # performing dot separation for sections
        elif isinstance(value, SectionProxy):  # -> Config
            return cls(dict_=value)
        elif isinstance(value, str):
            if isinstance(dict_, (ConfigParser, SectionProxy)):
                if value.isdigit():  # -> int
                    return dict_.getint(key, value)
                elif value.lower() in ('true', 'false'):  # -> bool
                    return dict_.getboolean(key, value)
            try:
                return ast.literal_eval(value)  # -> see: https://github.com/python/cpython/blob/99bc8589f09e66682a52df1f1a9598c7056d49dd/Lib/ast.py#L56
            except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                # Suppress ast.literal_eval errors to maintain code runtime.
                pass
        return value  # -> Union[str, None, bool, Config]

    def _define_instance_and_attribute(
            self,
            /,
            *,
            attribute: str,
            remaining_attributes: Deque[str],
            ) -> Tuple[Dict[str, VTConfig], str]:
        """Define instance and attribute if both of them, splitted
        by dots, presented (except the last one) in class.
        Pop attributes from remaining_attributes.
        """
        if attribute in self.__dict__:
            instance = getattr(self, attribute)
            if not isinstance(instance, Config):
                raise TypeError(
                    f'Instance should be type of {self.__class__.__name__}, recieved {type(instance)}.',
                    )
            attribute = remaining_attributes.popleft()
            return instance._define_instance_and_attribute(
                attribute=attribute,
                remaining_attributes=remaining_attributes,
                )
        return self.__dict__, attribute

    @classmethod
    def load(
        cls, path: Union[Path, str],
        **kwargs: Any,
        ) -> Config:
        """Load nested configuration in .ini file and parse it as MutableMapping.
        kwargs - any keyword arguments for configparser.ConfigParser.
        """
        config = ConfigParser(**kwargs)
        config.read(path)
        return cls(dict_=config)

    # Here is some magic with __getattr__, __setattr__ and __delattr__
    # which helps us to work with Config attributes using dot notation.
    def __getattr__(self, key: str) -> VTConfig:
        return self.__getitem__(key)

    def __setattr__(self, key: str, value: VTConfig) -> None:
        self.__setitem__(key, value)

    def __delattr__(self, key: str) -> None:
        self.__delitem__(key)

    # Other methods implemented for consistency with MutableMapping.
    def __delitem__(self, key: str) -> None:
        return self.__dict__.__delitem__(key)

    def __getitem__(self, key: str) -> VTConfig:
        return self.__dict__.__getitem__(key)

    def __iter__(self) -> Iterator[str]:
        return self.__dict__.__iter__()

    def __len__(self) -> int:
        return self.__dict__.__len__()

    def __setitem__(self, key: str, value: VTConfig) -> None:
        return self.__dict__.__setitem__(key, value)

    def items(self) -> ItemsView[str, VTConfig]:
        return self.__dict__.items()

    def keys(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[VTConfig]:
        return self.__dict__.values()

    def get(self, key: str, default: Optional[_VT] = None) -> Optional[Union[VTConfig, _VT]]:
        return self.__dict__.get(key, default)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__dict__.__repr__()})'
