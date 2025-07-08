import platform
import psutil

def get_memory_info():
    system = platform.system()

    if system == "Linux":
        with open('/proc/meminfo', 'r') as f:
            meminfo = {}
            for line in f:
                parts = line.split()
                key = parts[0].rstrip(':')
                value = int(parts[1])  # in kB
                meminfo[key] = value
        total_kb = meminfo.get('MemTotal', 0)
        available_kb = meminfo.get('MemAvailable', 0)
        total_gb = total_kb / 1024**2
        available_gb = available_kb / 1024**2
        return total_gb, available_gb

    else:
        mem = psutil.virtual_memory()
        total_gb = mem.total / 1024**3
        available_gb = mem.available / 1024**3
        return total_gb, available_gb

def format_memory_info(total_gb, available_gb, model_size=None):
    result = []
    result.append(f"Total Memory    : {total_gb:.2f} GB")
    result.append(f"Available Memory: {available_gb:.2f} GB")
    if model_size is not None and model_size > 0:
        result.append(f"Memory used by loading model: {model_size:.2f} GB")
    elif model_size is not None and model_size < 0:
        result.append(f"Memory gained by clearing model: {model_size:.2f} GB")
    return result

if __name__ == "__main__":
    total, start = get_memory_info()
    # Simulate model load here
    total, end = get_memory_info()
    used_mb = (start - end) * 1024  # convert GB diff to MB
    for line in format_memory_info(total, end, model_size=used_mb):
        print(line)
