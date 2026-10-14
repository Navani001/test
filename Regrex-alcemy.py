import time
import threading
import psutil
import subprocess


def measure_peak_memory(inference_fn, server_pid, interval=0.1):
    server = psutil.Process(server_pid)

    peak_ram = 0
    peak_vram = 0
    running = True

    def monitor():
        nonlocal peak_ram, peak_vram

        while running:
            try:
                processes = [server] + server.children(recursive=True)

                total_ram = sum(
                    p.memory_info().rss
                    for p in processes
                    if p.is_running()
                )
                peak_ram = max(peak_ram, total_ram)

                output = subprocess.check_output(
                    [
                        "nvidia-smi",
                        "--query-gpu=memory.used",
                        "--format=csv,noheader,nounits",
                    ],
                    text=True,
                    timeout=2,
                )

                gpu_memory = [
                    int(value.strip())
                    for value in output.splitlines()
                    if value.strip()
                ]

                if gpu_memory:
                    peak_vram = max(peak_vram, max(gpu_memory))

            except (
                psutil.Error,
                subprocess.SubprocessError,
                ValueError,
            ):
                pass

            time.sleep(interval)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()

    start = time.perf_counter()

    try:
        result = inference_fn()
    finally:
        elapsed = time.perf_counter() - start
        running = False
        thread.join()

    memory_usage = {
        "peak_ram_gb": round(peak_ram / (1024 ** 3), 3),
        "peak_vram_gb": round(peak_vram / 1024, 3),
    }

    return result, memory_usage, round(elapsed, 3)
