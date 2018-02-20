#include <Arduino.h>
#include <FastLED.h>

#include "panel_config.h"
#include "board_properties.h"

// Macro function to determine if pin is valid.
// TODO: define MAX_PIN in board_properties.h
#define VALID_PIN( pin ) ((pin) > 0)

// Assuming we can fill half of SRAM with CRGB pixels
#define MAX_PIXELS (SRAM_SIZE / (2 * sizeof(CRGB)))

// Length of output buffer
#define BUFFLEN 256

// Serial Baud rate
#define SERIAL_BAUD 9600

// The number of panels, determined by defines, calculated in setup()
int panel_count;

// The length of each panel
int panel_info[MAX_PANELS];

// the total number of pixels used by panels, determined by defines
int pixel_count;

// An array of arrays of pixels, populated in setup()
CRGB **panels = 0;

// temporarily store the p_size calculated
int p_size = 0;

// Serial out Buffer
char buffer[BUFFLEN];

// Current error code
int error_code = 0;

// This is kind of bullshit but you have to define the pins like this
// because FastLED.addLeds needs to know the pin numbers at compile time.
// Panels must be contiguous. The firmware stops defining panels after the first 
// undefined panel.

#define INIT_PANEL( data_pin, clk_pin, len) \
    if(!VALID_PIN((data_pin)) || (len) <= 0){\
        snprintf(buffer, BUFFLEN, "; PANEL_%02d not configured", panel_count);\
        Serial.println(buffer);\
        return 0;\
    }\
    snprintf(buffer, BUFFLEN, "; initializing PANEL_%02d, data_pin: %d, clk_pin: %d, len: %d", panel_count, (data_pin), (clk_pin), (len));\
    Serial.println(buffer);\
    pixel_count += (len);\
    if(pixel_count > MAX_PIXELS){\
        snprintf(buffer, BUFFLEN, "pixel count %d exceeds MAX_PIXELS %d in PANEL_%02d", pixel_count, MAX_PIXELS, panel_count);\
        return 10;\
    }\
    panels[panel_count] = (CRGB*) malloc( (len) * sizeof(CRGB));\
    if(!panels[panel_count]) {\
        snprintf(buffer, BUFFLEN, "malloc failed for PANEL_%02d", panel_count);\
        return 11;\
    }\
    panel_info[panel_count] = (len);\

void stop() {
    while(1);
}

int init_panels() {
    panels = (CRGB**) malloc( MAX_PANELS * sizeof(CRGB*));
    panel_count = 0;
    pixel_count = 0;
    
    // This is such bullshit but you gotta do it like this because addLeds needs to know pins at compile time
    INIT_PANEL(PANEL_00_DATA_PIN, PANEL_00_CLK_PIN, PANEL_00_LEN);
    #if NEEDS_CLK
        FastLED.addLeds<PANEL_TYPE, PANEL_00_DATA_PIN, PANEL_00_CLK_PIN>(panels[panel_count], PANEL_00_LEN);
    #else
        FastLED.addLeds<PANEL_TYPE, PANEL_00_DATA_PIN>(panels[panel_count], PANEL_00_LEN);
    #endif
    panel_count++;
    INIT_PANEL(PANEL_01_DATA_PIN, PANEL_01_CLK_PIN, PANEL_01_LEN);
    #if NEEDS_CLK
        FastLED.addLeds<PANEL_TYPE, PANEL_01_DATA_PIN, PANEL_01_CLK_PIN>(panels[panel_count], PANEL_01_LEN);
    #else
        FastLED.addLeds<PANEL_TYPE, PANEL_01_DATA_PIN>(panels[panel_count], PANEL_01_LEN);
    #endif
    panel_count++;
    INIT_PANEL(PANEL_02_DATA_PIN, PANEL_02_CLK_PIN, PANEL_02_LEN);
    #if NEEDS_CLK
        FastLED.addLeds<PANEL_TYPE, PANEL_02_DATA_PIN, PANEL_02_CLK_PIN>(panels[panel_count], PANEL_02_LEN);
    #else
        FastLED.addLeds<PANEL_TYPE, PANEL_02_DATA_PIN>(panels[panel_count], PANEL_02_LEN);
    #endif
    panel_count++;
    INIT_PANEL(PANEL_03_DATA_PIN, PANEL_03_CLK_PIN, PANEL_03_LEN);
    #if NEEDS_CLK
        FastLED.addLeds<PANEL_TYPE, PANEL_03_DATA_PIN, PANEL_03_CLK_PIN>(panels[panel_count], PANEL_03_LEN);
    #else
        FastLED.addLeds<PANEL_TYPE, PANEL_03_DATA_PIN>(panels[panel_count], PANEL_03_LEN);
    #endif
    panel_count++;
}

void setup() {
    // initialize serial
    Serial.begin(SERIAL_BAUD);
    while (!Serial) {
        ; // wait for serial port to connect. Needed for native USB port only
    }

    snprintf(buffer, BUFFLEN, "; detected board: %s", DETECTED_BOARD);
    Serial.println(buffer);    
    snprintf(buffer, BUFFLEN, "; sram size: %d", SRAM_SIZE);
    Serial.println(buffer);

    // Clear out buffer
    buffer[0] = '\0';

    error_code = init_panels();

    // Check that there are not too many panels or pixels for the board
    if(!error_code){
        if(pixel_count <= 0){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "pixel_count is %d. No pixels defined. Exiting", pixel_count);        
        } else if(pixel_count > MAX_PIXELS) {
            error_code = 10;
            snprintf(buffer, BUFFLEN, "MAX_PIXELS is %d but pixel_count is %d. Not enough memory. Exiting", MAX_PIXELS, pixel_count);        
        } 
    }
    if(error_code){
        // If there was an error, print the error code before the out buffer
        Serial.print("E");
        Serial.print(error_code);
        Serial.print(": ");
        Serial.println(buffer);
        // In the case of an error, stop execution
        stop();
    } else {
        snprintf(buffer, BUFFLEN, "; Setup: OK");
        Serial.println(buffer);
    }
}

// temporarily store the hue value calculated
int hue = 0;

void loop() {
    for(int i=0; i<255; i++){
        for(int p=0; p<panel_count; p++){        
            for(int j=0; j<panel_info[p]; j++){
                hue = (int)(255 * (1.0 + (float)j / (float)panel_info[p]) + i) % 255;
                panels[p][j].setHSV(hue, 255, 255);            
            }
        }
        FastLED.show();
    }
    
}