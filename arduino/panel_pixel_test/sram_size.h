/**
 * Determines the SRAM available to the arduino from preprocessor defines.
 */

// Arduino AVR Boards
#if defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
#define SRAM_SIZE 8192
#elif defined(__AVR_ATmega32U4__)
#define SRAM_SIZE 2560
#elif defined(__AVR_ATmega328__) || defined(__AVR_ATmega328P__)
#define SRAM_SIZE 2048
#elif defined(__AVR_ATmega16U4__)
#define SRAM_SIZE 1280
#elif defined(__AVR_ATmega168__) || defined(__AVR_ATmega168V__)
#define SRAM_SIZE 1024
#elif defined(__AVR_ATtiny85__)
#define SRAM_SIZE 512
// TeensyDuino
#elif defined(__AVR_AT90USB1286__)  /* Teensy++ 2.0 */
#define SRAM_SIZE 8192
#elif defined(__MKL26Z64__) /* Teensy LC (Cortex-M0+)*/
#define SRAM_SIZE 8192
#elif defined(__MK20DX128__) /* Teensy 3.0 -> 3.2 (Cortex-M4) */
#define SRAM_SIZE 65536
#elif defined(__MK64FX512__) /* Teensy 3.5 (Cortex-M4F) */
#define SRAM_SIZE 196608
#elif defined(__MK66FX1M0__) /* Teensy 3.6 (Cortex-M4F) */
#define SRAM_SIZE 262144
#else
// Assume we're on an Arduino Uno
#define SRAM_SIZE 2048
#endif
