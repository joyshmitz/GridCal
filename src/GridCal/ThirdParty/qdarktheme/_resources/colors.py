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
"""Default color values."""

THEME_COLOR_VALUES = {
    "dark": '{"background": {"base": "#202124", "list": {}, "panel": {"darken": 0.3}, "popup": {"lighten": 0.3}, "table": {"darken": 0.5}, "textarea": {"darken": 0.13}, "title": {"darken": 0.3}}, "border": {"base": "#3f4042", "input": {"transparent": 0}}, "foreground": {"base": "#e4e7eb", "defaultButton.disabledBackground": {"transparent": 0.2}, "disabled": {"transparent": 0.4}, "disabledSelectionBackground": {"transparent": 0.2}, "icon": {"darken": 0.01}, "icon.unfocused": {"transparent": 0.6}, "input.placeholder": {"transparent": 0.6}, "progressBar.disabledBackground": {"transparent": 0.2}, "slider.disabledBackground": {"transparent": 0.2}, "sliderTrack.inactiveBackground": {"transparent": 0.1}}, "input.background": "#3f4042", "inputButton.hoverBackground": "#ffffff25", "linkVisited": "#c58af8", "list.alternateBackground": "#ffffff0c", "list.hoverBackground": "#ffffff13", "menubar.selectionBackground": "#ffffff25", "popupItem.checkbox.background": "#ffffff19", "popupItem.selectionBackground": "#ffffff22", "primary": {"base": "#8ab4f7", "button.activeBackground": {"darken": 0.14, "transparent": 0.23}, "button.hoverBackground": {"darken": 0.1, "transparent": 0.11}, "defaultButton.activeBackground": {"darken": 0.12}, "defaultButton.hoverBackground": {"darken": 0.06}, "list.inactiveSelectionBackground": {"lighten": 0.2, "transparent": 0.15}, "list.selectionBackground": {"darken": 0.2, "transparent": 0.4}, "progressBar.background": {"darken": 0.1}, "selection.background": {"darken": 0.2, "lighten": 0.1, "transparent": 0.4}, "sliderHandle.activeBackground": {"darken": 0.09}, "table.inactiveSelectionBackground": {"lighten": 0.2, "transparent": 0.18}, "table.selectionBackground": {"darken": 0.2, "transparent": 0.55}, "textarea.selectionBackground": {"darken": 0.2, "lighten": 0.1, "transparent": 0.4}}, "scrollbar.background": "#ffffff10", "scrollbarSlider.activeBackground": "#ffffff60", "scrollbarSlider.background": "#ffffff30", "scrollbarSlider.disabledBackground": "#ffffff15", "scrollbarSlider.hoverBackground": "#ffffff45", "statusBar.background": "#2a2b2e", "statusBarItem.activeBackground": "#ffffff34", "statusBarItem.hoverBackground": "#ffffff22", "tab.activeBackground": "#ffffff00", "tab.hoverBackground": "#ffffff18", "tabCloseButton.hoverBackground": "#ffffff25", "table.alternateBackground": "#ffffff15", "tableSectionHeader.background": "#3f4042", "textarea.inactiveSelectionBackground": "#ffffff20", "toolbar.activeBackground": "#ffffff34", "toolbar.background": "#333333", "toolbar.hoverBackground": "#ffffff22", "tree.inactiveIndentGuidesStroke": "#ffffff35", "tree.indentGuidesStroke": "#ffffff60", "treeSectionHeader.background": "#3f4042"}',  # noqa: E501
    "light": '{"background": {"base": "#f8f9fa", "list": {}, "panel": {"lighten": 0.5}, "popup": {"lighten": 0.2}, "table": {"lighten": 0.5}, "textarea": {"lighten": 0.25}, "title": {"darken": 0.04}}, "border": {"base": "#dadce0", "input": {}}, "foreground": {"base": "#4d5157", "defaultButton.disabledBackground": {"transparent": 0.25}, "disabled": {"transparent": 0.4}, "disabledSelectionBackground": {"transparent": 0.25}, "icon": {"darken": 0.05}, "icon.unfocused": {"transparent": 0.6}, "input.placeholder": {"transparent": 0.6}, "progressBar.disabledBackground": {"transparent": 0.25}, "slider.disabledBackground": {"transparent": 0.25}, "sliderTrack.inactiveBackground": {"transparent": 0.2}}, "input.background": "#f8f9fa", "inputButton.hoverBackground": "#00000018", "linkVisited": "#660098", "list.alternateBackground": "#00000009", "list.hoverBackground": "#00000013", "menubar.selectionBackground": "#00000020", "popupItem.checkbox.background": "#00000019", "popupItem.selectionBackground": "#00000022", "primary": {"base": "#1a73e8", "button.activeBackground": {"darken": 0.03, "transparent": 0.24}, "button.hoverBackground": {"darken": 0.03, "transparent": 0.1}, "defaultButton.activeBackground": {"lighten": 0.3}, "defaultButton.hoverBackground": {"lighten": 0.1}, "list.inactiveSelectionBackground": {"darken": 0.43, "transparent": 0.09}, "list.selectionBackground": {"lighten": 0.2, "transparent": 0.35}, "progressBar.background": {"lighten": 0.2}, "selection.background": {"lighten": 0.3, "transparent": 0.5}, "sliderHandle.activeBackground": {"lighten": 0.2}, "table.inactiveSelectionBackground": {"darken": 0.43, "transparent": 0.09}, "table.selectionBackground": {"lighten": 0.1, "transparent": 0.5}, "textarea.selectionBackground": {"lighten": 0.3, "transparent": 0.5}}, "scrollbar.background": "#00000010", "scrollbarSlider.activeBackground": "#00000060", "scrollbarSlider.background": "#00000040", "scrollbarSlider.disabledBackground": "#00000015", "scrollbarSlider.hoverBackground": "#00000050", "statusBar.background": "#dfe1e5", "statusBarItem.activeBackground": "#00000024", "statusBarItem.hoverBackground": "#00000015", "tab.activeBackground": "#00000000", "tab.hoverBackground": "#00000015", "tabCloseButton.hoverBackground": "#00000020", "table.alternateBackground": "#00000012", "tableSectionHeader.background": "#dadce0", "textarea.inactiveSelectionBackground": "#00000015", "toolbar.activeBackground": "#00000024", "toolbar.background": "#ebebeb", "toolbar.hoverBackground": "#00000015", "tree.inactiveIndentGuidesStroke": "#00000030", "tree.indentGuidesStroke": "#00000050", "treeSectionHeader.background": "#dadce0"}',  # noqa: E501
}
ACCENT_COLORS = {
    "dark": {
        "blue": "#8ab4f7",
        "graphite": "#898a8f",
        "green": "#4caf50",
        "orange": "#ff9800",
        "pink": "#c7457f",
        "purple": "#af52bf",
        "red": "#f6685e",
        "yellow": "#ffeb3b",
    },
    "light": {
        "blue": "#1a73e8",
        "graphite": "#898a8f",
        "green": "#4caf50",
        "orange": "#ff9800",
        "pink": "#c7457f",
        "purple": "#9c27b0",
        "red": "#f44336",
        "yellow": "#f4c65f",
    },
}
