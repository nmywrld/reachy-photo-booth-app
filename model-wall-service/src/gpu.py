# SPDX-License-Identifier: Apache-2.0
"""Reads GPU and unified-memory statistics. Every field may be None."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pynvml

logger = logging.getLogger(__name__)


def parse_meminfo(text: str) -> dict[str, int | None]:
    values: dict[str, int] = {}
    for line in text.splitlines():
        parts = line.replace(":", " ").split()
        if len(parts) >= 2 and parts[1].isdigit():
            values[parts[0]] = int(parts[1]) * 1024
    total, available = values.get("MemTotal"), values.get("MemAvailable")
    used = total - available if total is not None and available is not None else None
    return {"total_bytes": total, "used_bytes": used}


def container_for_pid(pid: int, proc_root: Path = Path("/proc")) -> str | None:
    """Containers on the wall set `hostname` to their container name."""
    try:
        return (proc_root / str(pid) / "root/etc/hostname").read_text().strip() or None
    except OSError:
        return None


def memory_by_container(
    processes: list[Any], resolve: Callable[[int], str | None] = container_for_pid
) -> dict[str, int]:
    """Sum per-process GPU memory. A PID listed twice is only counted once."""
    by_pid: dict[int, int] = {}
    for process in processes:
        used = process.usedGpuMemory
        if used is None or used >= pynvml.NVML_VALUE_NOT_AVAILABLE_ulonglong.value:
            continue
        by_pid[process.pid] = max(by_pid.get(process.pid, 0), used)
    totals: dict[str, int] = {}
    for pid, used in by_pid.items():
        if (container := resolve(pid)) is not None:
            totals[container] = totals.get(container, 0) + used
    return totals


def _read(function: Callable[..., Any], *args: Any) -> Any:
    try:
        return function(*args)
    except pynvml.NVMLError:
        return None


class GpuSampler:
    def __init__(self) -> None:
        self._handle = None
        try:
            pynvml.nvmlInit()
            self._handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(self._handle)
            self.name = name.decode() if isinstance(name, bytes) else name
        except pynvml.NVMLError as error:
            self.name = None
            logger.warning("NVML is unavailable: %s", error)

    def sample(self) -> dict[str, Any]:
        try:
            memory = parse_meminfo(Path("/proc/meminfo").read_text())
        except OSError:
            memory = {"total_bytes": None, "used_bytes": None}

        result: dict[str, Any] = {
            "name": self.name,
            "available": self._handle is not None,
            "utilization_percent": None,
            "temperature_c": None,
            "power_watts": None,
            "memory": memory,
            "container_memory_bytes": {},
        }
        if self._handle is None:
            return result

        utilization = _read(pynvml.nvmlDeviceGetUtilizationRates, self._handle)
        if utilization is not None:
            result["utilization_percent"] = utilization.gpu
        result["temperature_c"] = _read(
            pynvml.nvmlDeviceGetTemperature, self._handle, pynvml.NVML_TEMPERATURE_GPU
        )
        milliwatts = _read(pynvml.nvmlDeviceGetPowerUsage, self._handle)
        if milliwatts is not None:
            result["power_watts"] = milliwatts / 1000
        processes = (
            _read(pynvml.nvmlDeviceGetComputeRunningProcesses, self._handle) or []
        ) + (_read(pynvml.nvmlDeviceGetGraphicsRunningProcesses, self._handle) or [])
        result["container_memory_bytes"] = memory_by_container(processes)
        return result
