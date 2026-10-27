# Pain: a fresh RGB-D pair was rejected as “before this request”

## Diagnosis

A resident sampler returns its latest pair. A consumer requiring its timestamp to be later than the request contradicts that contract: a pair acquired a few milliseconds earlier can still be perfectly fresh. Repeatedly restarting a camera or requesting three pairs can add latency without fixing the contract.

## Small solution

`LatestPair` stores one immutable pair under a lock. A consumer checks receive-time freshness, skew and clock/boot identity. It does **not** require timestamps later than the request. An optional explicit `not_before` boundary demonstrates a different requirement: data must follow a meaningful event, such as a settled pose.

Timing budgets in the example (0.8 s / 0.04 s) are illustrative, not sensor specifications. Receive timestamps are measured in the same local monotonic clock. They cannot be compared directly with camera hardware time, ROS simulated time or another machine's monotonic time.

## What it does not solve

This example has no image synchronization, camera intrinsics, RGB/depth alignment or network buffers. Receive-time freshness alone cannot prove the exposure happened after an arm movement; a hardware integration needs sensor timestamps, queue handling and a documented mapping into the same clock domain. Restoring the arm changes the camera transform: reacquire the scene and bind it to the current measured pose.

Zero depth means no valid range for those pixels, not zero physical distance. Do not fill it with a guessed distance just to continue. Check RGB mask, depth registration, invalid codes, reflective surfaces, range, occlusion and filtering separately. One paired frame can be enough for a stationary task; three frames should have an explicit purpose, such as estimating consistency—not be an unexplained requirement.

## 中文要点

“最新一帧”可以早于请求几毫秒；不要把缓存接口写成“必须是请求之后采样”。但是新鲜、RGB/Depth配对、时钟域和姿态关系仍然要清楚。深度为零不是目标在相机前0米，也不能直接拿邻近背景代替方块深度。
