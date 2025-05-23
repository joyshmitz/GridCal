# MIT License
#
# Copyright (c) 2021-2022 Yunosuke Ohsugi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module for handling template text."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from itertools import chain, zip_longest

from GridCal.ThirdParty.qdarktheme._util import multi_replace


@dataclass(unsafe_hash=True, frozen=True)
class _Placeholder:
    match_text: str
    value: str | int | float
    filters: tuple[str]


class Template:
    """Class that handles template text like jinja2."""

    _PLACEHOLDER_RE = re.compile(r"{{.*?}}")
    _STRING_RE = re.compile(r"""('([^'\\]*(?:\\.[^'\\]*)*)'|"([^"\\]*(?:\\.[^"\\]*)*)")""", re.S)

    def __init__(self, text: str, filters: dict):
        """Initialize Template class."""
        self._target_text = text
        self._filters = filters

    @staticmethod
    def _to_py_value(text: str):
        try:
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                return text

    @staticmethod
    def _parse_placeholders(text: str):
        placeholders: set[_Placeholder] = set()
        for match in re.finditer(Template._PLACEHOLDER_RE, text):
            match_text = match.group()
            contents, *filters = match_text.strip("{}").replace(" ", "").split("|")
            value = Template._to_py_value(contents)
            placeholders.add(_Placeholder(match_text, value, tuple(filters)))
        return placeholders

    def _run_filter(self, value: str | int | float, filter_text: str):
        contents = filter_text.split("(")
        if len(contents) == 1:
            return self._filters[contents[0]](value)

        filter_name, arg_text = contents
        py_strings = [match.group() for match in Template._STRING_RE.finditer(arg_text)]
        if len(py_strings) == 0:
            json_text = '{"' + arg_text.replace("=", '":').replace(",", ',"').replace(")", "}")
        else:
            py_strings_escaped = [re.escape(py_string) for py_string in py_strings]
            words = re.split("|".join(py_strings_escaped), arg_text)
            words = [word.replace("=", '":').replace(",", ',"').replace(")", "}") for word in words]
            json_text = '{"' + "".join(
                chain.from_iterable(zip_longest(words, py_strings, fillvalue=""))
            )
        arguments: dict = json.loads(json_text)
        return self._filters[filter_name](value, **arguments)

    def render(self, replacements: dict) -> str:
        """Render replacements."""
        placeholders = Template._parse_placeholders(self._target_text)
        new_replacements: dict[str, str] = {}
        for placeholder in placeholders:
            value = placeholder.value
            if type(value) is str and len(value) != 0:
                value = replacements.get(value)
            if value is None:
                raise AssertionError(
                    f"There is no replacements for: {placeholder.value} in {placeholder.match_text}"
                )
            for filter in placeholder.filters:
                value = self._run_filter(value, filter)
            new_replacements[placeholder.match_text] = str(value)
        return multi_replace(self._target_text, new_replacements)
