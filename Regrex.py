import re
from collections import defaultdict


def parse_log(log_text):

    result = {
        "failures": [],
        "failure_stats": [],
        "llm_throughput": [],
        "condition_throughput": []
    }

    lines = log_text.splitlines()

    current_failure = None

    for line in lines:

        # --------------------------------------------------
        # 1. LLM FAILURE
        # --------------------------------------------------

        failure_match = re.search(
            r"LLM inference failure.*?->\s*"
            r"request_id=(.*?),\s*"
            r"output_type=([^,]+),\s*"
            r"task_type=([^,]+),\s*"
            r"failure_type=([^,]+),\s*"
            r"attempt=(\d+)/(\d+):\s*(.*)",
            line
        )

        if failure_match:

            request_info = failure_match.group(1)

            current_failure = {
                "request_id_raw": request_info,
                "output_type": failure_match.group(2).strip(),
                "task_type": failure_match.group(3).strip(),
                "failure_type": failure_match.group(4).strip(),
                "attempt": int(failure_match.group(5)),
                "max_attempts": int(failure_match.group(6)),
                "error_message": failure_match.group(7).strip()
            }

            result["failures"].append(current_failure)

            continue


        # --------------------------------------------------
        # 2. FAILURE STATS
        # --------------------------------------------------

        stats_match = re.search(
            r"\[Attempt\s+(\d+)\]\s+Failure stats\s*->\s*"
            r"max_token=(\d+),\s*"
            r"decode=(\d+),\s*"
            r"parse=(\d+),\s*"
            r"schema_validation=(\d+)\s*"
            r"malformed_table=(\d+)\s*"
            r"\((\d+)/(\d+)\s+failed\)",
            line
        )

        if stats_match:

            result["failure_stats"].append({
                "attempt": int(stats_match.group(1)),
                "max_token": int(stats_match.group(2)),
                "decode": int(stats_match.group(3)),
                "parse": int(stats_match.group(4)),
                "schema_validation": int(stats_match.group(5)),
                "malformed_table": int(stats_match.group(6)),
                "failed": int(stats_match.group(7)),
                "total": int(stats_match.group(8))
            })

            continue


        # --------------------------------------------------
        # 3. OVERALL LLM THROUGHPUT
        # --------------------------------------------------

        throughput_match = re.search(
            r"LLM throughput\s*->\s*"
            r"overall=([\d.]+)\s*tok/s,\s*"
            r"tokens=(\d+),\s*"
            r"elapsed=([\d.]+)s",
            line
        )

        if throughput_match:

            result["llm_throughput"].append({
                "overall_tok_per_sec": float(throughput_match.group(1)),
                "tokens": int(throughput_match.group(2)),
                "elapsed_seconds": float(throughput_match.group(3))
            })

            continue


        # --------------------------------------------------
        # 4. CONDITION THROUGHPUT
        # --------------------------------------------------

        condition_match = re.search(
            r"LLM condition throughput\s*->\s*(.*)",
            line
        )

        if condition_match:

            conditions_text = condition_match.group(1)

            conditions = {}

            pattern = re.compile(
                r"([a-zA-Z0-9_]+)"
                r"=([\d.]+)\s*tok/s"
                r"\s*\((\d+)\s*tokens\)"
            )

            for match in pattern.finditer(conditions_text):

                condition = match.group(1)

                conditions[condition] = {
                    "tok_per_sec": float(match.group(2)),
                    "tokens": int(match.group(3))
                }

            result["condition_throughput"].append(conditions)

    return result
