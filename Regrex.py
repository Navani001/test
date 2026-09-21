import json
import difflib

from parser_old import parse_log as old_parse_log
from parser_new import parse_log as new_parse_log


def compare_outputs(old_output, new_output):
    """
    Compare the complete output of the old and new parsers.

    Returns a useful diff if they are different.
    """

    if old_output == new_output:
        return None

    old_json = json.dumps(
        old_output,
        indent=2,
        sort_keys=True,
        default=str,
    ).splitlines()

    new_json = json.dumps(
        new_output,
        indent=2,
        sort_keys=True,
        default=str,
    ).splitlines()

    diff = difflib.unified_diff(
        old_json,
        new_json,
        fromfile="OLD PARSER",
        tofile="NEW PARSER",
        lineterm="",
    )

    return "\n".join(diff)


def test_old_and_new_parser_have_same_output():

    # --------------------------------------------------------
    # Read the same log for both parsers
    # --------------------------------------------------------

    with open(
        "test_logs/sample.log",
        "r",
        encoding="utf-8",
    ) as file:

        log_text = file.read()


    # --------------------------------------------------------
    # Run OLD parser
    # --------------------------------------------------------

    old_output = old_parse_log(log_text)


    # --------------------------------------------------------
    # Run NEW parser
    # --------------------------------------------------------

    new_output = new_parse_log(log_text)


    # --------------------------------------------------------
    # Compare complete output
    # --------------------------------------------------------

    diff = compare_outputs(
        old_output,
        new_output,
    )


    # --------------------------------------------------------
    # Fail test if ANY difference exists
    # --------------------------------------------------------

    assert diff is None, (
        "\n\n"
        "OLD PARSER AND NEW PARSER PRODUCED DIFFERENT OUTPUT!\n\n"
        f"{diff}"
    )
