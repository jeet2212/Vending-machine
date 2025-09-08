`default_nettype none
`timescale 1ns / 1ps

`timescale 1ns/1ps

module tb;
    reg clk;
    reg rst_n;
    reg ena;
    reg [7:0] ui_in;
    reg [7:0] uio_in;
    wire [7:0] uo_out;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;

    // Instantiate DUT
    tt_um_vending_machine dut (
        .clk(clk),
        .rst_n(rst_n),
        .ena(ena),
        .ui_in(ui_in),
        .uio_in(uio_in),
        .uo_out(uo_out),
        .uio_out(uio_out),
        .uio_oe(uio_oe)
    );

    // Clock generator
    initial clk = 0;
    always #5 clk = ~clk;

    // Don’t add stimulus or $finish here — cocotb controls everything
endmodule

