/*
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

  // FSM state encoding (plain Verilog)
  parameter IDLE = 2'b00;
  parameter S5   = 2'b01;
  parameter S10  = 2'b10;
  parameter DISP = 2'b11;

  reg [1:0] state, next_state;
  reg [7:0] balance;

  // Coin input (ui_in[1:0])
  wire [1:0] coin = ui_in[1:0];
  wire [7:0] coin_value;
  assign coin_value = (coin == 2'b01) ? 8'd5  :
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

  // Next state logic (lookahead balance)
  always @(*) begin
    case (state)
      IDLE: begin
        if (balance + coin_value >= 15)
          next_state = DISP;
        else if (balance + coin_value == 5)
          next_state = S5;
        else if (balance + coin_value == 10)
          next_state = S10;
        else
          next_state = IDLE;
      end
      S5: begin
        if (balance + coin_value >= 15)
          next_state = DISP;
        else if (balance + coin_value == 10)
          next_state = S10;
        else
          next_state = S5;
      end
      S10: begin
        if (balance + coin_value >= 15)
          next_state = DISP;
        else if (balance + coin_value == 5)
          next_state = S5;
        else
          next_state = S10;
      end
      DISP: next_state = IDLE;
      default: next_state = IDLE;
    endcase
  end


  // Outputs
  assign uo_out[0]   = (state == DISP);
  assign uo_out[7:1] = balance[6:0];

  // Unused IOs
  assign uio_out = 0;
  assign uio_oe  = 0;

  // Prevent warnings
  wire _unused = &{ena, uio_in, 1'b0};

endmodule
