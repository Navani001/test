import time
import threading
import psutil


def measure_peak_memory(server_pid, inference_fn, interval=0.1):
    server = psutil.Process(server_pid)
    peak_ram = 0
    running = True

    def monitor():
        nonlocal peak_ram

        while running:
            try:
                processes = [server] + server.children(recursive=True)
                ram = sum(
                    p.memory_info().rss
                    for p in processes
                    if p.is_running()
                )
                peak_ram = max(peak_ram, ram)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            time.sleep(interval)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()

    start = time.perf_counter()
    try:
        result = inference_fn()
    finally:
        running = False
        thread.join()

    elapsed = time.perf_counter() - start

    return {
        "result": result,
        "peak_ram_gb": round(peak_ram / (1024**3), 3),
        "latency_seconds": round(elapsed, 3),
    }
