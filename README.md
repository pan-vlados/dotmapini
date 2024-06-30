# dotmapini

<p align="center">
  <img src="https://img.shields.io/badge/Python3-Programming-green?style=plastic&labelColor=4584b6&color=ffde57"/>
  <img src="https://img.shields.io/badge/INI-config-file"/>
  <img src="https://img.shields.io/badge/dotmapini-config?style=for-the-badge&color=purple"/>
  <img src="https://img.shields.io/badge/dot-notation-ini?color=blue"/>
  <img src="https://img.shields.io/badge/LICENSE-MIT-white"/>
</p>

Package allow configuration and section's option values of .ini file to be called as attributes, where the section and option are separated by dot notation.

> The focus is to work with .ini configuration data using dot notation. Just call attributes and get their values in development flow while defining them in single place.
- No more configuration values in `config['section']['option']` style, just `config.section.option`;
- Can parse .ini files with dots between section names and convert them as several sections for corresponding values;
- Parse values and convert them to Python datatypes;
    ```python
    # Return parsed value datatypes:
    Union[Config, str, bool, int, float, bytes, tuple, list, dict, set, None]
    # Other types as well as Python types that aren't presented correctly in .ini
    # not implemented and will be parsed as string.
    ```
- Your config is instance of `collections.MutableMapping` (dict's like) and have the same features;
- Support all keyword arguments for `configparser.ConfigParser` in `Config.load(path, **kwargs)` method;
- Less keystroke;
- No dependencies, only stdlib.


## Installation:

```sh
pip install dotmapini
```


## Usage:

Imagine you have following .ini configuration file:
```ini
# example.ini
[APP]
debug = False

[server]
host = 127.0.0.1
port = 8080

[server.db]
host = localhost
database = test
user = username
password = password

[complex.Python.datatypes]  ; Your complex Python datatype as is
example = [{'key': ({'value', 'value2'}, [True, 1.2, 3])}]
```
Minimal reproducible example:
```python
from dotmapini import Config


config = Config.load(
    path='/your/path/to/example.ini',
    allow_no_value=True  # keyword for configparser.ConfigParser(...)
    )
print(config.APP.debug)  # => False type bool
print(config.server.host)  # => '127.0.0.1' type str
print(config.server.port)  # => 8080 type int
print(config.server.db.database)  # => 'test' type str
print(config.server.db.username)  # => 'username' type str
print(config.complex.Python.datatypes.example)  # => [{'key': ({'value', 'value2'}, [True, 1.2, 3])}] type list
```
Of course as always you can do this:
```python
print(config['server']['db']['host'])  # => 'localhost' type str
```
But for what...


## IMPORTANT:

- <details><summary>Uppercase strings for options will be parsed as lowercase.</summary>

    Example:
    ```ini
    [section]
    OPTION = ...
    ```
    Will be:
    ```python
    config = Config.load(...)
    config.section.option  # not self.section.OPTION
    ```
    </details>

- <details><summary>Only digits in section's name not allowed.</summary>

    Example:
    ```ini
    [section.1.subsection]  ; A digit between dots not allowed as well
    ...
    [2]
    ...
    [3.section]
    ...
    ```
    Will be:
    ```python
    config = Config.load(...)  # will raise DigitInSectionNameError
    ```
    </details>

- <details><summary>If you have DEFAULT section it will be added to all other sections thus it can override same named option values.</summary>

    Example:
    ```ini
    [DEFAULT]
    option = value

    [section]
    option = value2
    ```
    Will be:
    ```python
    config = Config.load(...)
    config.section.option = value  # not value2
    ```
    </details>

- Be aware not to [memory overflow](https://github.com/python/cpython/blob/99bc8589f09e66682a52df1f1a9598c7056d49dd/Lib/ast.py#L63) while represent complex Python datatypes in .ini file.

Most of this stuff is the default behavior of `configparser.ConfigParser`.


## Need to mention:

**Q**: Why not dotmap?\
**A**: I want to focus to work specifically with .ini/configparser. There is no need to me to create a lot of dict's like objects.\
**Q**: Why not types.SimpleNamesapce?\
**A**: It can instantiate attributes and nothing else, that is not the case here. Class `collections.MutableMapping` provide more control/isolation when create complex custom dict's like bjects, which is focus to work with .ini configuration files and modify receiving values.


## LICENSE
> MIT
