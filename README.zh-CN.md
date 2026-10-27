# 机器人集成与排错笔记

**先写痛点，再分享方案和可运行的最小示例。** 从静止抓红方块，到观察、定位、规划、停靠、恢复姿态、重新抓取，真正花时间的往往是环节之间的交接。

这不是 C2 生产控制代码。Python 3.11+，标准库即可运行；默认没有真机、ROS、串口或烧录动作。

- [五个按钮怎么串成一个本机任务](docs/01-handoffs.md)
- [网页关闭后任务继续：模拟控制面板](docs/05-control-panel.md)
- [最新 RGB-D 为什么还会超时](docs/02-rgbd.md)
- [实测布局、相机/关节误差与 IMU 零偏](docs/03-errors.md)
- [第一次烧录控制板：工具、验证、回滚与启动行为](docs/04-flashing.md)

运行 `python panel.py`，打开 `http://127.0.0.1:8788` 即可体验模拟任务；点击 English / 中文切换语言。运行 `python -m unittest discover -s tests -v` 做离线检查。

`python analyze_errors.py imu examples/synthetic_imu.csv` 分析人工生成的 IMU 样本；`python analyze_errors.py points examples/synthetic_points.csv` 计算已知点误差。**只输出报告，不自动矫正或写入硬件。** 样本、补偿值与实际机器人验证分开记录。

[成功真机展示与中文日志](https://mondaywmd.github.io/monday-robotics-universe/zh/c2-one-click-red-cube.html) · [English README](README.md)
