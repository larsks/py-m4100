import logging
import re

LOG = logging.getLogger(__name__)

RE_DOTTED_LINE = re.compile(r"(?P<name>[^.]+)\.\.\.\.*( (?P<value>.*))?")


def parse_dotted_table(lines):
    table = {}
    for line in lines:
        if mo := RE_DOTTED_LINE.match(line):
            field, value = mo.group("name"), mo.group("value")
            table[field] = value

    return table


def parse_fixed_width_table(lines):
    """Parse a table of fixed with columns.

    Dynamically discovers column labels and column widths."""

    rows = []
    mark = 0

    # Find header/data split
    for i, line in enumerate(lines):
        if line.startswith("-"):
            mark = i
            break
    else:
        return []

    colspec = []
    for col in re.finditer("-+", lines[mark]):
        colspec.append(slice(*col.span()))

    headers = [[] for _ in range(len(colspec))]
    for line in reversed(lines[0:mark]):
        if not line.strip():
            break
        for i, spec in enumerate(colspec):
            headers[i].append(line[spec].strip())

    headers = [" ".join(reversed(header)).strip().lower() for header in headers]

    for line in lines[mark + 1 :]:
        row = [line[spec].strip() for spec in colspec]
        rows.append(dict(zip(headers, row)))

    return rows
