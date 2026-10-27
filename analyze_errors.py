"""Offline CSV diagnostics; estimates only, never applies compensation."""
import argparse
import csv
import json
import math
import statistics
from pathlib import Path

def summarize(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows)<2:
        raise ValueError("Need at least two samples")
    cols = {k:[float(r[k]) for r in rows] for k in ("time_s","gyro_z_rad_s","yaw_rad")}
    if not all(math.isfinite(x) for v in cols.values() for x in v):
        raise ValueError("NaN/Inf in telemetry; diagnose input before compensation")
    t,gyro,yaw = (cols[k] for k in ("time_s","gyro_z_rad_s","yaw_rad"))
    if any(b<=a for a,b in zip(t,t[1:])):
        raise ValueError("Times must strictly increase within one clock/boot")
    unwrapped=[yaw[0]]
    for a,b in zip(yaw,yaw[1:]):
        unwrapped.append(unwrapped[-1]+math.atan2(math.sin(b-a),math.cos(b-a)))
    duration=t[-1]-t[0]
    return {"samples":len(t),"duration_s":duration,
            "gyro_z_mean_rad_s":statistics.mean(gyro),
            "gyro_z_std_rad_s":statistics.pstdev(gyro),
            "yaw_change_deg":math.degrees(unwrapped[-1]-unwrapped[0]),
            "yaw_drift_deg_per_min":math.degrees(unwrapped[-1]-unwrapped[0])*60/duration,
            "interpretation":"Only interpret as bias/drift if independently known stationary; no correction applied"}

def point_errors(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if not rows:raise ValueError("Empty points")
    delta=[]
    for r in rows:
        v=[float(r[k]) for k in ("expected_x_m","expected_y_m","expected_z_m","measured_x_m","measured_y_m","measured_z_m")]
        if not all(math.isfinite(x) for x in v):raise ValueError("Invalid point")
        delta.append([v[i+3]-v[i] for i in range(3)])
    return {"samples":len(delta),"mean_measured_minus_expected_m":[statistics.mean(d[i] for d in delta) for i in range(3)],"rms_3d_error_m":math.sqrt(statistics.mean(sum(x*x for x in d) for d in delta)),"note":"Same coordinate frame and independent reference required. Not an extrinsic calibration solver."}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("kind",choices=["imu","points"]);p.add_argument("csv");a=p.parse_args()
    print(json.dumps((summarize if a.kind=="imu" else point_errors)(a.csv),indent=2))
