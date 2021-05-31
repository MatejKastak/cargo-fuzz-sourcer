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
SOURCE_PREFIX_LEN = len(SOURCE_PREFIX)

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

    if int(num) > 7:
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
    """Extract the code snippet from the objdump output."""
    res: str = ""
    lines_to_include = 3
    lines = list(output.splitlines())

    # Find the first line that starts with the chosen prefix
    for idx, line in enumerate(lines):
        if line.startswith(SOURCE_PREFIX):
            break
    else:
        # If we don't find any source code, return empty string
        return ""

    # Normalize the index
    idx -= 1

    # Line at idx should contain the file path and file number
    file_path = lines[idx]
    if "rustlib" in file_path:
        return ""

    # Add it as a comment first
    res += f"// {lines[idx]}\n"

    # Collect the first code snippet in the output, ingore any other code
    source_code = []
    for i, line in enumerate(lines[idx + 1 :]):
        if not line.startswith(SOURCE_PREFIX):
            break
        source_code.append(line[SOURCE_PREFIX_LEN:])
    else:
        return ""

    # Join the last `lines_to_include` source code lines
    # It looks like the last line in this list is the "leaking" line of code
    # This way we can add a litle bit more context to the output
    res += "\n".join(source_code[-lines_to_include:])

    return res


def construct_objdump_cmd(file_path: str, offset_str: str) -> typing.List[str]:
    """Construct `objdump` command."""

    # Calculate the start and end offset
    # For some reason the offset is one off
    start_addr = int(offset_str, base=16) - 0x10
    stop_addr = start_addr + 0x14

    cmd = CMD_BASE + [
        f"--start-address={hex(start_addr)}",
        f"--stop-address={hex(stop_addr)}",
        file_path,
    ]

    return cmd
