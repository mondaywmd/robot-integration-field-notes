# Pain: finding the right flashing tool was harder than expected

This is a **board-specific field guide**, not a universal flashing recipe or an automatic flasher. The demonstrated robot used an OpenRF4 / STM32F407 controller, a USB-serial download connection and ATK-XISP. Other boards need their own schematic and boot-mode documentation.

## Find the tools without random executable mirrors

- [ALIENTEK / 正点原子 official download center](https://www.openedv.com/docs/build/html/index.html): look for **ATK-XISP**. ATK-XCOM is a serial terminal, not the same tool. The download center was indexed with ATK-XISP when this guide was prepared; availability and exact version can change.
- [STMicroelectronics STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html): official alternative for supported STM32 programming interfaces. We did not validate it as a drop-in replacement for this board's ATK-XISP setup.
- [ST UART connection documentation](https://dev.st.com/stm32cube-docs/prog/2.23.0/en/docs/markup/Uart_Connection_page.html) and [AN2606 boot-mode documentation](https://www.st.com/resource/en/application_note/an2606-stm32microcontroller-system-memory-boot-mode-stmicroelectronics.pdf): identify the exact MCU, supported boot interfaces and boot conditions.

Vendor software and firmware are not redistributed or covered by this repository's MIT license.

## The sequence that mattered

1. Identify the board revision, MCU, firmware purpose and matching host driver. Save the known-working image and a rollback procedure before writing anything.
2. Follow the board's documented power/download arrangement. Wi-Fi access to the robot's computer does not replace a required USB download cable to the controller. USB may power some rails and not others; main power off does not prove every component is unpowered.
3. Identify the actual USB serial port. Our recorded port was COM5/CH340 and baud was 115200; these are observations, not universal settings. Likewise, DTR/RTS reset/boot behavior is board wiring specific. Do not copy polarity from another board.
4. Select the exact HEX or BIN. HEX carries address records; a BIN needs the correct base address from the board's build. Check the file hash against your intended build manifest.
5. Inspect the programming options. In our maintenance workflow verification was enabled and **run after programming was disabled**. Erase options can destroy calibration/configuration regions; do not adopt full-chip erase as a general default.
6. Preserve the programming/verification log. Hashing the input file is not flash readback verification.
7. Treat reset, USB reconnection and the next power-on as a separate startup operation. **Unchecking “run after programming” does not disable boot-time homing.** Our full runtime retained startup motion; a stationary diagnostic image had a different entry point. Never confuse those images.
8. For rollback, restore the matching known-working firmware and driver pair using the documented board method. This repository provides no image and does not toggle reset, boot pins or serial lines.

## Read-only preflight utility

```sh
python firmware_preflight.py your-firmware.hex --sha256 YOUR_64_CHARACTER_BUILD_HASH
```

It reads a file only. A match proves equality to the supplied digest—not board compatibility, safe startup behavior, correct calibration or successful programming.

## What to record for another person

Board/MCU/revision; official tool source and version; firmware filename and hash; download/power wiring; port and boot-mode settings; verification log; startup behavior; matching host driver; exact rollback image. Share screenshots only after removing personal paths, serial numbers or credentials you do not intend to publish.

## 中文要点

找软件时分清 ATK-XISP（烧录）和 ATK-XCOM（串口终端），优先官方资料入口。下载完成、校验通过、程序已运行、机器人已安全停稳是四件不同的事。“编程后运行”不勾选，只影响当前烧录操作，不能阻止下一次上电时完整固件自动归位。不要照搬别人的COM端口、复位极性、擦除方式和固件。
