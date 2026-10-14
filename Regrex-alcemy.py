import psutil
import time
import threading


def measure_peak_ram(inference_fn, server_pid, interval=0.05):
    server = psutil.Process(server_pid)
    peak_ram = 0
    running = True

    def monitor():
        nonlocal peak_ram

        while running:
            try:
                processes = [server] + server.children(recursive=True)
                total_ram = sum(
                    p.memory_info().rss
                    for p in processes
                    if p.is_running()
                )
                peak_ram = max(peak_ram, total_ram)
            except psutil.Error:
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

    return result, peak_ram / (1024**3), elapsed
