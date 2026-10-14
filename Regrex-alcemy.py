import os
import time
import threading
import psutil


def measure_peak_ram(inference_fn, interval=0.05):
    process = psutil.Process(os.getpid())
    peak_ram = 0
    running = True

    def monitor():
        nonlocal peak_ram

        while running:
            try:
                ram = process.memory_info().rss
                peak_ram = max(peak_ram, ram)
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

    return result, peak_ram / (1024 ** 3), elapsed
