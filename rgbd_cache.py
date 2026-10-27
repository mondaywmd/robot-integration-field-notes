"""Small received-time cache, not camera synchronization or depth registration."""
import math
import threading
from dataclasses import dataclass

@dataclass(frozen=True)
class Pair:
    rgb_received: float
    depth_received: float
    clock: str
    rgb: bytes
    depth: bytes

class LatestPair:
    def __init__(self):
        self.lock = threading.Lock()
        self.pair = None

    def publish(self, pair):
        if not all(math.isfinite(v) for v in (pair.rgb_received, pair.depth_received)):
            raise ValueError("Non-finite receive time")
        with self.lock:
            self.pair = pair

    def get(self, now, clock, max_age=0.8, max_skew=0.04, not_before=None):
        if not all(math.isfinite(v) for v in (now, max_age, max_skew)) or min(max_age,max_skew)<0:
            raise ValueError("Invalid timing budget")
        with self.lock:
            pair = self.pair
        if pair is None:
            raise ValueError("No pair")
        if pair.clock != clock:
            raise ValueError("Clock/boot domain changed")
        ages = [now-pair.rgb_received, now-pair.depth_received]
        if min(ages)<0 or max(ages)>max_age:
            raise ValueError("Future or stale pair")
        if abs(pair.rgb_received-pair.depth_received)>max_skew:
            raise ValueError("Receive-time skew exceeded")
        if not_before is not None:
            if not math.isfinite(not_before) or min(pair.rgb_received,pair.depth_received)<not_before:
                raise ValueError("Pair precedes explicit acquisition boundary")
        return pair
