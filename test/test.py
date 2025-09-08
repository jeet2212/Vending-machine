import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock


def safe_int(value):
    """Convert cocotb BinaryValue to int, resolving X/Z to 0."""
    binstr = value.binstr
    if "x" in binstr or "z" in binstr:
        return 0
    return int(binstr, 2)


async def reset_dut(dut):
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


async def check_dispense(dut, msg):
    """Wait 1 cycle and check that dispense is asserted for exactly 1 cycle."""
    await ClockCycles(dut.clk, 1)
    uo_val = safe_int(dut.uo_out.value)
    balance = uo_val >> 1
    dispense = uo_val & 1
    dut._log.info(f"{msg}: balance={balance}, dispense={dispense}")
    assert dispense == 1, f"{msg} -> expected dispense=1"

    # Next cycle dispense should return to 0
    await ClockCycles(dut.clk, 1)
    uo_val = safe_int(dut.uo_out.value)
    dispense = uo_val & 1
    assert dispense == 0, f"{msg} -> dispense should clear after 1 cycle"


@cocotb.test()
async def test_vending_machine(dut):
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset DUT
    await reset_dut(dut)

    # --- Test 5 + 10 = 15 -> dispense ---
    dut.ui_in.value = 0b01  # coin = 5
    await ClockCycles(dut.clk, 1)

    dut.ui_in.value = 0b10  # coin = 10
    await check_dispense(dut, "After 5+10")

    # --- Test 20 directly -> dispense ---
    dut.ui_in.value = 0b11  # coin = 20
    await check_dispense(dut, "After 20")
