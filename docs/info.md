## How it works

This project implements a **Finite State Machine (FSM) vending machine** in Verilog.  

- The machine accepts coins of **5, 10, and 20 credits** using inputs `ui[1:0]`.  
- The product price is **15 credits**.  
- When the total balance reaches or exceeds 15 credits, the machine dispenses a product (output `uo[0] = 1`) for one cycle, then resets the balance to zero.  
- The current balance is shown on the debug outputs `uo[7:1]`.  

### Coin encoding (`ui[1:0]`)
| Input (`ui[1:0]`) | Coin Value |
|-------------------|------------|
| `00`              | No coin    |
| `01`              | 5          |
| `10`              | 10         |
| `11`              | 20         |

### Output encoding (`uo[7:0]`)
- `uo[0]` = **Dispense signal** (goes high when product is dispensed)  
- `uo[7:1]` = **Balance (debug)**  

---

## Truth table (examples)

| Sequence of Coins | Balance Before | Balance After | Dispense (`uo[0]`) |
|-------------------|----------------|---------------|---------------------|
| None              | 0              | 0             | 0 |
| 5                 | 0              | 5             | 0 |
| 10                | 0              | 10            | 0 |
| 5 → 10            | 5              | 15            | 1 (dispense) |
| 10 → 5            | 10             | 15            | 1 (dispense) |
| 20                | 0              | 20 → reset    | 1 (dispense) |
| 5 → 5 → 5         | 10             | 15            | 1 (dispense) |

After each **dispense**, the balance resets to 0.  

---

## How to test

1. Apply a clock signal to `clk` (10 µs period in simulation = 100 kHz).  
2. Hold `rst_n = 0` for a few cycles to reset, then set `rst_n = 1`.  
3. Insert coins by driving `ui[1:0]` with the proper encoding (`01`, `10`, `11`).  
4. Observe outputs:  
   - `uo[0]` goes HIGH when product is dispensed.  
   - `uo[7:1]` shows current balance in credits.  

Example simulation (using cocotb testbench):  
- Insert 5 (`ui=01`), then 10 (`ui=10`) → dispense.  
- Insert 20 (`ui=11`) → immediate dispense.  

---

## External hardware

- No external hardware is required.  
- Optional: you can connect LEDs to `uo[7:0]` to see the **dispense signal** (`uo[0]`) and the **binary balance display** (`uo[7:1]`).  
