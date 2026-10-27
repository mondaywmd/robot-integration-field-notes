# Pain: a task needed a webpage to stay alive

`python panel.py` serves a small bilingual simulation panel at http://127.0.0.1:8788. The Python process owns the task. The browser only starts, stops, resets and reads status. Close the page during a run, wait, and reopen: the mock result remains until reset. There is no browser heartbeat.

The panel includes a deliberate drive-failure option so you can see failure recovery without a robot. Reset clears a finished result; it cannot clear a running task. Stop requests cooperative cancellation and the worker finishes its failure/stop record. Double starts are rejected while active. Restarting the server starts idle; no persistent auto-resume.

This is a **localhost-only mock UI**. It has no authentication, ROS, camera video, firmware flashing, motor commands or physical stop protection. Do not expose it on a network or attach real actuators as-is. Add authentication, durable ownership and verified device stopping appropriate to your system before hardware integration. Browser refresh is not a stop button and a browser stop button is not an emergency stop.

## 中文

控制面板也是可复用的成果：开始、停止、状态、结果和失败后重置，任务在本机进程中继续执行。中英文切换只影响显示。此版本完全是模拟设备，不是直接用于真机的控制服务；它演示的是任务归属和界面交接。
