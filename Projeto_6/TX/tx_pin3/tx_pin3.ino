#include "sw_uart.h"

// COM 5
due_sw_uart uart;

// int pino_tx = 3;
// char a; 
// int carac = 0b01100001;

void setup() {
  Serial.begin(9600);
  sw_uart_setup(&uart, 3, 1, 8, SW_UART_EVEN_PARITY);
  //pinMode(3, OUTPUT); 
}

void loop() {
 transmit_byte();
 delay(500);
}


void transmit_byte() {
  sw_uart_write_byte(&uart, 'a');
}
