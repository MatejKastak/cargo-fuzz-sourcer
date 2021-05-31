import fileinput
import re
import subprocess
import textwrap
import typing

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import RustLexer

# Regex searching for the leak
LEAK = re.compile(r"\s+#(?P<num>\d+) .* \((?P<spec>.*)\)")

# Objdump can prefix the source code from debug info with the custom string
SOURCE_PREFIX = "ABCDcfs"

# Base for the objdump command
CMD_BASE = f"objdump -S --source-comment={SOURCE_PREFIX} -C -l -d --no-show-raw-insn -M intel".split(
    " "
)


def filter_stdin() -> None:
    """Filter the cargo-fuzz output on stdin."""
    for line in fileinput.input():
        process_line(line)


def process_line(line: str) -> None:
    """Process a single line of input."""

    # Print the line either way, we want to only add to the output
    print(line, end="")

    # Check if the line matches the leak
    match = LEAK.match(line)
    if match:
        process_leak(match.group("num"), match.group("spec"))


def process_leak(num: str, spec: str) -> None:
    """Process a single leak."""

    if int(num) > 5:
        return

    file_path, offset_str = spec.rsplit("+", maxsplit=1)

    cmd = construct_objdump_cmd(file_path, offset_str)
    res = subprocess.run(cmd, capture_output=True, text=True)

    print_objdump_result(res.stdout)


def print_objdump_result(output: str) -> None:
    source = extract_source_code(output)

    if source.strip():
        print(
            textwrap.indent(
                highlight(
                    source, RustLexer(), Terminal256Formatter(style="gruvbox-dark")
                ),
                "\t\t",
            ),
            end="",
        )


def extract_source_code(output: str) -> str:
    source: typing.List[str] = []
    for line in output.splitlines():
        if line.startswith(SOURCE_PREFIX):
            source.append(line[len(SOURCE_PREFIX) :])

    return "\n".join(source)


def construct_objdump_cmd(file_path: str, offset_str: str) -> typing.List[str]:
    """Construct `objdump` command."""

    # Calculate the start and end offset
    # For some reason the offset is one off
    start_addr = int(offset_str, base=16) - 8
    stop_addr = start_addr + 1

    cmd = CMD_BASE + [
        f"--start-address={hex(start_addr)}",
        f"--stop-address={hex(stop_addr)}",
        file_path,
    ]

    return cmd
