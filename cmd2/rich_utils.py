# coding=utf-8
"""Provides common utilities to support Rich in cmd2 applications."""

from enum import Enum
from typing import (
    IO,
    Any,
    Optional,
)

from rich.console import Console
from rich.style import Style
from rich.theme import Theme
from rich_argparse import RichHelpFormatter

# Default styles for printing strings of various types.
# These can be altered to suit an application's needs and only need to be a
# function with the following structure: func(str) -> str
style_success = Style(color="green")
"""Rich style which colors text to signify success"""

style_warning = Style(color="bright_yellow")
"""Rich style which colors text to signify a warning"""

style_failure = Style(color="bright_red")
"""Rich style which colors text to signify a failure"""


class AllowStyle(Enum):
    """Values for ``cmd2.rich_utils.allow_style``"""

    ALWAYS = 'Always'  # Always output ANSI style sequences
    NEVER = 'Never'  # Remove ANSI style sequences from all output
    TERMINAL = 'Terminal'  # Remove ANSI style sequences if the output is not going to the terminal

    def __str__(self) -> str:
        """Return value instead of enum name for printing in cmd2's set command"""
        return str(self.value)

    def __repr__(self) -> str:
        """Return quoted value instead of enum description for printing in cmd2's set command"""
        return repr(self.value)


# Controls when ANSI style sequences are allowed in output
allow_style = AllowStyle.TERMINAL

# Rich theme used by Cmd2Console
THEME: Optional[Theme] = None

# Backup of default rich-argparse styles
DEFAULT_RICH_ARGPARSE_STYLES = RichHelpFormatter.styles.copy()


def set_theme(theme: Optional[Theme]) -> None:
    """
    Set the Rich theme used by Cmd2Console and rich-argparse.

    :param theme: new theme or None if you want to use Rich and rich-argparse defaults.
    """
    global THEME
    THEME = theme

    # Update rich-argparse styles
    if theme is None:
        RichHelpFormatter.styles = DEFAULT_RICH_ARGPARSE_STYLES.copy()
    else:
        for name, style in theme.styles.items():
            if name in RichHelpFormatter.styles:
                RichHelpFormatter.styles[name] = style


class Cmd2Console(Console):
    """Rich console with characteristics appropriate for cmd2 applications."""

    def __init__(self, file: IO[str]) -> None:
        """
        Cmd2Console initializer

        :param file: a file object where the console should write to
        """
        kwargs: dict[str, Any] = {}
        if allow_style == AllowStyle.ALWAYS:
            kwargs["force_terminal"] = True

            # Turn off interactive mode if dest is not actually a terminal which supports it
            tmp_console = Console(file=file)
            kwargs["force_interactive"] = tmp_console.is_interactive
        elif allow_style == AllowStyle.NEVER:
            kwargs["force_terminal"] = False

        # Turn off automatic markup, emoji, and highlight rendering at the console level.
        # You can still enable these in Console.print() calls.
        super().__init__(
            file=file,
            tab_size=4,
            markup=False,
            emoji=False,
            highlight=False,
            theme=THEME,
            **kwargs,
        )

    def on_broken_pipe(self) -> None:
        """Override which raises BrokenPipeError instead of SystemExit"""
        try:
            super().on_broken_pipe()
        except SystemExit:
            pass
        raise BrokenPipeError
