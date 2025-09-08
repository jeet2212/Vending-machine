# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


async def insert_coin(dut, coin):
    """Helper: insert a coin (2-bit encoding: 01=5, 10=10, 11=20)"""
    dut.ui_in.value = coin
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)


@cocotb.test()
async def test_vending_machine(dut):
    dut._log.info("Start Vending Machine Test")

    # Create a clock: 10us period (100kHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    dut._log.info("Reset complete")

    # Case 1: Insert 5 + 10 = 15 → dispense
    await insert_coin(dut, 0b01)  # 5
    dut._log.info(f"After 5: balance={int(dut.uo_out.value) >> 1}, dispense={dut.uo_out.value & 1}")

    await insert_coin(dut, 0b10)  # 10
    dut._log.info(f"After 10: balance={int(dut.uo_out.value) >> 1}, dispense={dut.uo_out.value & 1}")

    assert dut.uo_out.value & 1 == 1, "Should dispense product at 15 credits"

    # Case 2: Insert 20 directly → dispense
    await insert_coin(dut, 0b11)  # 20
    dut._log.info(f"After 20: balance={int(dut.uo_out.value) >> 1}, dispense={dut.uo_out.value & 1}")

    assert dut.uo_out.value & 1 == 1, "Should dispense product at 20 credits"

    # Extra wait cycles
    await ClockCycles(dut.clk, 5)
    dut._log.info("Vending Machine Test Complete")
