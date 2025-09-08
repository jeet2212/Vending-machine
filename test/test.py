import cocotb
from cocotb.triggers import RisingEdge, Timer


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def insert_coin(dut, value):
    """Insert a coin: 01=5, 10=10, 11=20"""
    dut.ui_in.value = value
    await RisingEdge(dut.clk)
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)


async def check_dispense(dut, msg=""):
    """
    Check if dispense pulses.
    In gate-level sim dispense may be very short, so poll with fine granularity.
    """
    found = False
    balance = 0
    dispense = 0

    for i in range(10):  # check over 10ns
        await Timer(1, units="ns")
        uo_val = int(dut.uo_out.value)
        balance = uo_val >> 1
        dispense = uo_val & 1
        dut._log.info(f"{msg} (step {i}): balance={balance}, dispense={dispense}")
        if dispense == 1:
            found = True
            break

    assert found, f"{msg} -> expected dispense=1 within time window"
    return dispense, balance


@cocotb.test()
async def test_vending_machine(dut):
    """Test sequence for vending machine FSM"""

    # Reset
    await reset_dut(dut)

    # Insert 5
    await insert_coin(dut, 0b01)
    dispense, balance = await check_dispense(dut, "After 5")
    assert balance == 5, "Balance should be 5"
    assert dispense == 0, "No dispense after only 5"

    # Insert 10 (total 15)
    await insert_coin(dut, 0b10)
    dispense, balance = await check_dispense(dut, "After 5+10")
    assert dispense == 1, "Should dispense after reaching 15"
    assert balance == 0, "Balance should reset after dispense"

    # Insert 20 directly
    await insert_coin(dut, 0b11)
    dispense, balance = await check_dispense(dut, "After 20")
    assert dispense == 1, "Should dispense with 20"
    assert balance == 0, "Balance should reset after dispense"
