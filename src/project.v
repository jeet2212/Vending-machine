/*
 * Copyright (c) 2024
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // FSM states
  typedef enum logic [1:0] {
    IDLE   = 2'b00,
    S5     = 2'b01,
    S10    = 2'b10,
    DISP   = 2'b11
  } state_t;

  state_t state, next_state;
  reg [7:0] balance;

  // Coin input (ui_in[1:0])
  wire [1:0] coin = ui_in[1:0];
  wire [7:0] coin_value =
        (coin == 2'b01) ? 8'd5  :
        (coin == 2'b10) ? 8'd10 :
        (coin == 2'b11) ? 8'd20 : 8'd0;

  // Sequential state update
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state   <= IDLE;
      balance <= 0;
    end else begin
      state   <= next_state;
      if (coin_value != 0 && state != DISP)
        balance <= balance + coin_value;
      else if (state == DISP)
        balance <= 0;  // reset after dispensing
    end
  end

  // Next state logic
  always @(*) begin
    case (state)
      IDLE:   next_state = (balance >= 15) ? DISP :
                           (balance == 5)  ? S5   :
                           (balance == 10) ? S10  : IDLE;
      S5:     next_state = (balance >= 15) ? DISP :
                           (balance == 10) ? S10  : S5;
      S10:    next_state = (balance >= 15) ? DISP :
                           (balance == 5)  ? S5   : S10;
      DISP:   next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end

  // Output: product dispense on uo_out[0], balance debug on uo_out[7:1]
  assign uo_out[0]   = (state == DISP);
  assign uo_out[7:1] = balance[6:0];

  // Unused IOs
  assign uio_out = 0;
  assign uio_oe  = 0;

  // Prevent warnings
  wire _unused = &{ena, uio_in, 1'b0};

endmodule
