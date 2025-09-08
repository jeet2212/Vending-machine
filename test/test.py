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
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


async def check_dispense(dut, msg):
    """Check that dispense goes high exactly one cycle after enough coins."""
    await ClockCycles(dut.clk, 1)  # FSM transitions into DISP here
    uo_val = safe_int(dut.uo_out.value)
    balance = uo_val >> 1
    dispense = uo_val & 1
    dut._log.info(f"{msg}: balance={balance}, dispense={dispense}")
    assert dispense == 1, f"{msg} -> expected dispense=1"

    # One more cycle: dispense should clear
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

    # --- Insert 5 ---
    dut.ui_in.value = 0b01
    await ClockCycles(dut.clk, 1)

    # --- Insert 10 (total=15 → should dispense next cycle) ---
    dut.ui_in.value = 0b10
    await check_dispense(dut, "After 5+10")

    # --- Insert 20 directly (should dispense next cycle) ---
    dut.ui_in.value = 0b11
    await check_dispense(dut, "After 20")
