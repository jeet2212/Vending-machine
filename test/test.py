# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock


async def reset_dut(dut):
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def insert_coin(dut, coin):
    dut.ui_in.value = coin
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)


@cocotb.test()
async def test_vending_machine(dut):
    """Vending machine FSM test"""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut._log.info("Start Vending Machine Test")

    await reset_dut(dut)
    dut._log.info("Reset complete")

    # Insert 10 credits
    await insert_coin(dut, 0b10)
    dut._log.info(f"After 10: balance={int(dut.uo_out.value) >> 1}, dispense={dut.uo_out.value & 1}")
    assert (dut.uo_out.value & 1) == 0, "Should not dispense yet at 10 credits"

    # Insert 5 credits → should dispense
    await insert_coin(dut, 0b01)
    dut._log.info(f"After 5: balance={int(dut.uo_out.value) >> 1}, dispense={dut.uo_out.value & 1}")
    assert (dut.uo_out.value & 1) == 1, "Should dispense product at 15 credits"

    # Wait one cycle → dispense should clear
    await ClockCycles(dut.clk, 1)
    dut._log.info(f"Dispense cleared: balance={int(dut.uo_out.value) >> 1}, dispense={dut.uo_out.value & 1}")
    assert (dut.uo_out.value & 1) == 0, "Dispense signal should clear after one cycle"

    # Insert 20 directly → should dispense immediately
    await insert_coin(dut, 0b11)


    assert dut.uo_out.value & 1 == 1, "Should dispense product at 20 credits"

    # Extra wait cycles
    await ClockCycles(dut.clk, 5)
    dut._log.info("Vending Machine Test Complete")
