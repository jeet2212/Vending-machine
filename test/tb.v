`default_nettype none
`timescale 1ns / 1ps

module tb ();

  // Dump the signals to a VCD file
  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0, tb);
    #1;
  end

  // Clock & reset
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  // Instantiate DUT
  tt_um_example dut (
`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif
      .ui_in  (ui_in),
      .uo_out (uo_out),
      .uio_in (uio_in),
      .uio_out(uio_out),
      .uio_oe (uio_oe),
      .ena    (ena),
      .clk    (clk),
      .rst_n  (rst_n)
  );

  // Clock generation: 10ns period
  always #5 clk = ~clk;

  // Task: insert a coin
  task insert_coin(input [1:0] coin);
    begin
      ui_in[1:0] = coin;
      @(posedge clk);
      ui_in[1:0] = 2'b00;  // return to no coin
      @(posedge clk);
    end
  endtask

  // Test sequence
  initial begin
    // Initialize
    clk   = 0;
    rst_n = 0;
    ena   = 1;
    ui_in = 0;
    uio_in= 0;

    // Apply reset
    #20;
    rst_n = 1;
    $display("Reset complete. Starting test...");

    // Insert 5
    insert_coin(2'b01);  // 5
    $display("Inserted 5, balance = %0d, dispense = %b", uo_out[7:1], uo_out[0]);

    // Insert 10 -> should dispense (total = 15)
    insert_coin(2'b10);  // 10
    $display("Inserted 10, balance = %0d, dispense = %b", uo_out[7:1], uo_out[0]);

    // Wait a bit
    #20;

    // Insert 20 -> should dispense immediately
    insert_coin(2'b11);  // 20
    $display("Inserted 20, balance = %0d, dispense = %b", uo_out[7:1], uo_out[0]);

    #50;
    $display("Test finished.");
    $finish;
  end

endmodule
