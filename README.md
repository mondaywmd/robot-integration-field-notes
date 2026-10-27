# Robot Integration Field Notes

**Problems we hit while turning a stationary grasp into one local mobile task—and small examples you can run without a robot.**

[中文](README.zh-CN.md) · [Real-robot demo and devlog](https://mondaywmd.github.io/monday-robotics-universe/c2-one-click-red-cube.html) · [Video-making tools](https://github.com/mondaywmd/robot-demo-video-tools)

This is an educational extraction of lessons from a C2 project, **not the production robot stack**. Python 3.11+; standard library only. No firmware, ROS, serial connection, actuator command, or hardware calibration runs here.

| Pain point | Shareable solution |
|---|---|
| Five manual actions work; the combined task fails | [Task ownership and handoffs](docs/01-handoffs.md), runnable `handoff.py` |
| A webpage disconnect stops an onboard task | [Local demo control panel](docs/05-control-panel.md), `panel.py` |
| Fresh RGB-D frames are rejected as too old | [Clock and cache contract](docs/02-rgbd.md), `rgbd_cache.py` |
| Model looks correct, real robot misses | [Measured reference and error diagnosis](docs/03-errors.md), `analyze_errors.py` |
| Finding a flasher and knowing what to click is painful | [First firmware flash field guide](docs/04-flashing.md), read-only `firmware_preflight.py` |

## Try it

From the repository root:

```sh
python handoff.py
python handoff.py --fail-at drive  # expected exit 1; no grasp after failure
python panel.py                   # open http://127.0.0.1:8788
python analyze_errors.py imu examples/synthetic_imu.csv
python analyze_errors.py points examples/synthetic_points.csv
python -m unittest discover -s tests -v
```

`examples/` contains **synthetic** measurements with known errors. They are not hardware results. The mock panel never drives anything. Start and stop buttons demonstrate application semantics only.

## What transfers to your robot?

The ideas and small data contracts. Replace the demonstration adapter with your own hardware integration only after defining measured completion, cancellation, stop acknowledgement, timeout, coordinate frames, and sensor validity. Each hardware call must have its own bounded I/O; a Python cancellation event cannot interrupt an arbitrary blocked driver. Keep low-level communication and collision protections in the device controller. See [adapter contract](docs/01-handoffs.md).

The real project eventually demonstrated approach, grasp, lift and release; its sensor alignment and heading stability remain subject to further validation. Passing these offline checks does not validate a real robot.

## Reuse

MIT for original code and documentation in this repository. No vendor code, firmware binaries or private credentials are included. The layout photo is the author's previously published experiment image. Linked vendor tools have their own terms. We do not claim to have created ATK-XISP or STM32CubeProgrammer.
