import cocotb
from cocotb.triggers import RisingEdge


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
    # Wait an extra cycle, since dispense appears after state transition
    await RisingEdge(dut.clk)
    dispense = int(dut.uo_out[0])
    balance  = int(dut.uo_out[7:1])
    dut._log.info(f"{msg}: balance={balance}, dispense={dispense}")
    return dispense, balance


@cocotb.test()
async def test_vending_machine(dut):
    """Test sequence for vending machine FSM"""

    # Reset
    await reset_dut(dut)

    # Insert 5
    await insert_coin(dut, 0b01)
    _, balance = await check_dispense(dut, "After 5")
    assert balance == 5, "Balance should be 5"

    # Insert 10
    await insert_coin(dut, 0b10)
    dispense, balance = await check_dispense(dut, "After 5+10")
    assert dispense == 1, "Should dispense after reaching 15"
    assert balance == 0, "Balance should reset after dispense"

    # Insert 20 directly
    await insert_coin(dut, 0b11)
    dispense, balance = await check_dispense(dut, "After 20")
    assert dispense == 1, "Should dispense with 20"
    assert balance == 0, "Balance should reset after dispense"
