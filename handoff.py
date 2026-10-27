"""Offline task-handoff example. No robot, ROS, web or serial connection."""
import argparse
import json
import threading
import time
import uuid
from dataclasses import dataclass

STAGES = ("observe", "plan", "drive", "restore", "grasp")

@dataclass(frozen=True)
class Receipt:
    run_id: str
    stage: str
    ok: bool
    settled: bool = True

class Runner:
    """Single invocation only; reuse requires a new instance, never implicit resume."""
    def __init__(self, adapter):
        self.adapter = adapter
        self.cancel = threading.Event()
        self.started = False
        self.events = []

    def run(self):
        if self.started:
            raise RuntimeError("Create a new runner for an explicitly requested new task")
        self.started = True
        run_id = uuid.uuid4().hex
        try:
            for stage in STAGES:
                if self.cancel.is_set():
                    raise InterruptedError("Cancelled before next stage")
                self.events.append({"stage": stage, "state": "started"})
                # Adapters own bounded I/O and cooperative cancellation. This
                # example does NOT claim it can interrupt a blocking hardware call.
                reply = self.adapter.perform(stage, run_id, self.cancel)
                if self.cancel.is_set():
                    raise InterruptedError("Cancelled during stage")
                if not isinstance(reply, Receipt) or (reply.run_id, reply.stage) != (run_id, stage):
                    raise ValueError("Mismatched completion receipt")
                if not reply.ok or not reply.settled:
                    raise ValueError("Stage failed or did not settle")
                self.events.append({"stage": stage, "state": "completed"})
            return {"state": "completed", "mode": "simulation", "events": self.events}
        except Exception as exc:
            try:
                stopped = self.adapter.stop() is True
            except Exception:
                stopped = False
            return {"state": "cancelled" if isinstance(exc, InterruptedError) else "failed",
                    "mode": "simulation", "error": str(exc), "stop_acknowledged": stopped,
                    "events": self.events}

class DemoAdapter:
    def __init__(self, fail_at=None, delay=0.1):
        self.fail_at, self.delay = fail_at, delay
        self.calls = []

    def perform(self, stage, run_id, cancel):
        self.calls.append(stage)
        cancel.wait(self.delay)
        return Receipt(run_id, stage, stage != self.fail_at)

    def stop(self):
        return True  # A mock acknowledgement, never physical stop evidence.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fail-at", choices=STAGES)
    args = parser.parse_args()
    result = Runner(DemoAdapter(args.fail_at)).run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["state"] == "completed" else 1)
