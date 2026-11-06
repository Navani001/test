import os
import sys
import time
import platform

print("Python:", sys.executable)
print("Working directory:", os.getcwd())
print("Script:", __file__)
print("Python paths:", sys.path)
print("CPU count:", os.cpu_count())
print("CPU affinity:", os.sched_getaffinity(0))
print("Platform:", platform.platform())

for key in [
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "LD_LIBRARY_PATH",
    "LD_PRELOAD"
]:
    print(key, os.environ.get(key))
