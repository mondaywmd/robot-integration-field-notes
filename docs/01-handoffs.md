# Pain: each button works, but the complete task fails

## What happened

Observation, planning, driving, restoring the arm and grasping had separate status rules. The automatic path treated a result differently from the manual path. A browser-owned sequence also depended on page lifetime. Adding more retries would not repair those disagreements.

## Solution

Let one local owner call the existing operations. A browser submits intent and displays status. Each stage needs a completion receipt belonging to this run and stage. A stop request is not the same as a confirmed physical stop. A failure cancels downstream stages; service restart must not silently replay old actions.

`handoff.py` demonstrates five sequential operations, cancellation and receipt identity. `panel.py` demonstrates a web client disconnecting without cancelling the local worker. Neither implements a physical controller or durable task resume.

## Hardware adapter contract

- `perform(stage, run_id, cancel)` must bound its own I/O and respond to cancellation. Return a receipt only after the actual stage-specific completion condition.
- `drive`: actual arrival and stationary confirmation, not “command sent.”
- `restore`: measured pose suitable for the new capture, not the requested servo angle.
- `grasp`: separate command completion from object pickup confirmation.
- `stop()` returning true must represent the hardware acknowledgement you actually observed. On lost communication, report unknown—not stopped.
- Keep sensor freshness, driver timeouts, joint limits and obstacle stopping independent of browser polling.
- Do not copy C2's pose tolerances or observation exceptions as universal rules.

## Try / expected outcome

`python handoff.py --fail-at drive` exits 1. Events end at drive; restore and grasp do not run. `python handoff.py` succeeds entirely in simulation. Restarting the panel creates an idle demonstration, not resumed motion. A deployment requiring crash recovery needs persisted operation identity and hardware reconciliation beyond this sample.

## 中文要点

痛点是完成条件和任务所有权不一致，而不只是按钮少。统一手动与自动的同一接口；网页显示与机器人执行分开。关闭网页不停止模拟任务，不代表可以删除底层失联停止。失败后不自动重试动作，重新启动也不自动恢复旧任务。
