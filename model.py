import re


# ============================================================
# REGEX PATTERNS
# Compile once instead of compiling/searching the pattern
# repeatedly for every line.
# ============================================================

RUN_ID_RE = re.compile(
    r"Inserted Tracker db.*?(\d+)"
)

OPINION_INFERENCE_RE = re.compile(
    r"Completed opinion inference: (\d+)/(\d+) successful"
)

FAILURE_RE = re.compile(
    r"LLM inference failure.*?"
    r"request_id=(.*?),\s*"
    r"output_type=(.*?),\s*"
    r"task_type=(.*?),\s*"
    r"failure_type=(.*?),\s*"
    r"attempt=(\d+)/(\d+):\s*(.*)"
)

STATS_RE = re.compile(
    r"\[Attempt\s+(\d+)\]\s+Failure stats\s*=>\s*"
    r"max_token=(\d+),\s*"
    r"decode=(\d+),\s*"
    r"parse=(\d+),\s*"
    r"schema_validation=(\d+)\s*"
    r"malformed_table=(\d+)\s*"
    r"\((\d+)/(\d+)\s+failed\)"
)

# Keep these patterns aligned with the actual log messages.
# They are compiled once.
LLM_THROUGHPUT_RE = re.compile(
    r"LLM condition throughput.*?"
    r"request_id=(.*?),\s*"
    r"output_type=(.*?),\s*"
    r"task_type=(.*?),\s*"
    r"throughput=(.*)"
)

CONDITION_THROUGHPUT_RE = re.compile(
    r"Condition throughput.*?"
    r"condition=(.*?),\s*"
    r"throughput=(.*)"
)


# ============================================================
# RESULT CREATION
# ============================================================

def create_result(include_inference=True):

    result = {
        "failures": [],
        "failure_stats": [],
        "llm_throughput": [],
        "condition_throughput": [],
    }

    if include_inference:
        result = {
            "total_inference": 0,
            "success_inference": 0,
            "failures": [],
            "failure_stats": [],
            "llm_throughput": [],
            "condition_throughput": [],
        }

    return result


# ============================================================
# PARSER
# ============================================================

def parse_log(log_text):

    key = "base"

    result = create_result()

    final_result = {}

    # splitlines() is done only once
    lines = log_text.splitlines()

    for line in lines:

        # ====================================================
        # RUN ID
        # ====================================================

        if "Inserted Tracker db" in line:

            date_time = extract_datetime(line)

            match_run_id = RUN_ID_RE.search(line)

            if match_run_id:

                run_id = match_run_id.group(1)

                final_result["run_id"] = run_id
                final_result["created_at"] = date_time

            continue


        # ====================================================
        # OPINION INFERENCE
        # ====================================================

        if "Completed opinion inference" in line:

            date_time = extract_datetime(line)

            opinion_inference_match = (
                OPINION_INFERENCE_RE.search(line)
            )

            if opinion_inference_match:

                # Keep the values as strings if your original
                # response contains strings.
                result["total_inference"] = (
                    opinion_inference_match.group(2)
                )

                result["success_inference"] = (
                    opinion_inference_match.group(1)
                )

            continue


        # ====================================================
        # GENERATING AGGREGATE
        # ====================================================

        if "Generating aggregate" in line:

            final_result[key] = result

            result = create_result(
                include_inference=False
            )

            key = "agg"

            continue


        # ====================================================
        # LLM FAILURE
        # ====================================================

        if "LLM inference failure" in line:

            date_time = extract_datetime(line)

            failure_match = FAILURE_RE.search(line)

            if not failure_match:
                continue

            request_info = failure_match.group(1)

            request_info_list = request_info.split(
                "::",
                2
            )

            # Prevent malformed log lines from crashing parser
            if len(request_info_list) < 3:
                continue


            # ------------------------------------------------
            # AGGREGATE FAILURE
            # ------------------------------------------------

            if request_info_list[0] == "agg":

                current_failure = {
                    "request_id_raw": request_info,
                    "audit_id": request_info_list[0],
                    "condition": request_info_list[1],
                    "indicator": request_info_list[2],

                    "is_agg": True,

                    "output_type": failure_match.group(2),
                    "task_type": failure_match.group(3).strip(),
                    "failure_type": failure_match.group(4).strip(),

                    "attempt": int(
                        failure_match.group(5)
                    ),

                    "max_attempts": int(
                        failure_match.group(6)
                    ),

                    "error_message": failure_match.group(7).strip(),

                    "created_at": date_time,
                }

                result["failures"].append(
                    current_failure
                )

            else:

                # ------------------------------------------------
                # NORMAL FAILURE
                # ------------------------------------------------

                current_failure = {
                    "request_id_raw": request_info,
                    "audit_id": request_info_list[0],
                    "condition": request_info_list[1],
                    "indicator": request_info_list[2],

                    "is_agg": False,

                    "output_type": failure_match.group(2),
                    "task_type": failure_match.group(3).strip(),
                    "failure_type": failure_match.group(4).strip(),

                    "attempt": int(
                        failure_match.group(5)
                    ),

                    "max_attempts": int(
                        failure_match.group(6)
                    ),

                    "error_message": failure_match.group(7).strip(),

                    "created_at": date_time,
                }

                result["failures"].append(
                    current_failure
                )

            continue


        # ====================================================
        # FAILURE STATS
        # ====================================================

        if "Failure stats" in line:

            date_time = extract_datetime(line)

            stats_match = STATS_RE.search(line)

            if stats_match:

                result["failure_stats"].append({

                    "attempt": int(
                        stats_match.group(1)
                    ),

                    "max_token": int(
                        stats_match.group(2)
                    ),

                    "decode": int(
                        stats_match.group(3)
                    ),

                    "parse": int(
                        stats_match.group(4)
                    ),

                    "schema_validation": int(
                        stats_match.group(5)
                    ),

                    "malformed_table": int(
                        stats_match.group(6)
                    ),

                    "failed": int(
                        stats_match.group(7)
                    ),

                    "total": int(
                        stats_match.group(8)
                    ),

                    "created_at": date_time,
                })

            continue


        # ====================================================
        # LLM THROUGHPUT
        # ====================================================

        if "LLM condition throughput" in line:

            date_time = extract_datetime(line)

            llm_match = LLM_THROUGHPUT_RE.search(line)

            if llm_match:

                # Adjust only the extraction fields if your
                # actual log format differs.

                llm_throughput = {
                    "request_id": llm_match.group(1),
                    "output_type": llm_match.group(2).strip(),
                    "task_type": llm_match.group(3).strip(),
                    "throughput": llm_match.group(4).strip(),
                    "created_at": date_time,
                }

                result["llm_throughput"].append(
                    llm_throughput
                )

            continue


        # ====================================================
        # CONDITION THROUGHPUT
        # ====================================================

        if "condition throughput" in line:

            date_time = extract_datetime(line)

            condition_match = (
                CONDITION_THROUGHPUT_RE.search(line)
            )

            if condition_match:

                conditions = {
                    "condition": condition_match.group(1).strip(),
                    "throughput": condition_match.group(2).strip(),
                    "created_at": date_time,
                }

                result["condition_throughput"].append(
                    conditions
                )

            continue


    # ========================================================
    # SAVE LAST RESULT
    # ========================================================

    final_result[key] = result

    return final_result
