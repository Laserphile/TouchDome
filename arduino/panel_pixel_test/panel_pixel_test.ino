#include <Arduino.h>
#include <FastLED.h>

// This is kind of bullshit but you have to define the pins like this
// because FastLED.addLeds needs to know the pin numbers at compile time.
// Panels must be contiguous. The firmware stops defining panels after the first 
// undefined panel.

#include "panel_config.h"
#include "sram_size.h"

#define NEEDS_CLK( type ) (type == APA102 || type == DOTSTAR || type == WS2801 || type == LPD8806 || type == P9813 || type == SM16716 )

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

void stop() {
    while(1);
}

void init_panels() {
    panels = (CRGB**) malloc( MAX_PANELS * sizeof(CRGB*));
    panel_count = 0;
    pixel_count = 0;
    
    // This is such bullshit but you gotta do it like this because addLeds needs to know pins at compile time
    #if PANEL_00_DATA_PIN > 0 && PANEL_00_LEN > 0
        panel_count++; pixel_count += PANEL_00_LEN;
        if(panel_count > MAX_PANELS || pixel_count > MAX_PIXELS){
            return;
        }
        panels[0] = (CRGB*) malloc( PANEL_00_LEN * sizeof(CRGB));
        if(!panels[0]){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "malloc failed for PANEL_00");
            return;
        }
        panel_info[0] = PANEL_00_LEN;
        #if NEEDS_CLK(PANEL_00_TYPE) && PANEL_00_CLK_PIN > 0
          FastLED.addLeds<PANEL_00_TYPE, PANEL_00_DATA_PIN, PANEL_00_CLK_PIN>(panels[0], PANEL_00_LEN);
        #else
          FastLED.addLeds<PANEL_00_TYPE, PANEL_00_DATA_PIN>(panels[0], PANEL_00_LEN);
        #endif
    #else
        return;
    #endif
    #if PANEL_01_DATA_PIN > 0 && PANEL_01_LEN > 0
        panel_count++; pixel_count += PANEL_01_LEN;
        if(panel_count > MAX_PANELS || pixel_count > MAX_PIXELS){
            return;
        }
        panels[1] = (CRGB*) malloc( PANEL_01_LEN * sizeof(CRGB));
        if(!panels[1]){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "malloc failed for PANEL_01");
            return;
        }
        panel_info[1] = PANEL_01_LEN;
        #if NEEDS_CLK(PANEL_01_TYPE) && PANEL_01_CLK_PIN > 0
          FastLED.addLeds<PANEL_01_TYPE, PANEL_01_DATA_PIN, PANEL_01_CLK_PIN>(panels[1], PANEL_01_LEN);
        #else
          FastLED.addLeds<PANEL_01_TYPE, PANEL_01_DATA_PIN>(panels[1], PANEL_01_LEN);
        #endif
    #else
        return;
    #endif
    #if PANEL_02_DATA_PIN > 0 && PANEL_02_LEN > 0
        panel_count++; pixel_count += PANEL_02_LEN;
        if(panel_count > MAX_PANELS || pixel_count > MAX_PIXELS){
            return;
        }
        panels[2] = (CRGB*) malloc( PANEL_02_LEN * sizeof(CRGB));
        if(!panels[2]){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "malloc failed for PANEL_02");
            return;
        }
        panel_info[2] = PANEL_02_LEN;
        #if NEEDS_CLK(PANEL_02_TYPE) && PANEL_02_CLK_PIN > 0
          FastLED.addLeds<PANEL_02_TYPE, PANEL_02_DATA_PIN, PANEL_02_CLK_PIN>(panels[2], PANEL_02_LEN);
        #else
          FastLED.addLeds<PANEL_02_TYPE, PANEL_02_DATA_PIN>(panels[2], PANEL_02_LEN);
        #endif
    #else
        return;
    #endif
    #if PANEL_03_DATA_PIN > 0 && PANEL_03_LEN > 0
        panel_count++; pixel_count += PANEL_03_LEN;
        if(panel_count > MAX_PANELS || pixel_count > MAX_PIXELS){
            return;
        }
        panels[3] = (CRGB*) malloc( PANEL_03_LEN * sizeof(CRGB));
        if(!panels[3]){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "malloc failed for PANEL_03");
            return;
        }
        panel_info[3] = PANEL_03_LEN;
        #if NEEDS_CLK(PANEL_03_TYPE) && PANEL_03_CLK_PIN > 0
          FastLED.addLeds<PANEL_03_TYPE, PANEL_03_DATA_PIN, PANEL_03_CLK_PIN>(panels[3], PANEL_03_LEN);
        #else
          FastLED.addLeds<PANEL_03_TYPE, PANEL_03_DATA_PIN>(panels[3], PANEL_03_LEN);
        #endif
    #else
        return;
    #endif
}

void setup() {
    // initialize serial
    Serial.begin(SERIAL_BAUD);

    // Clear out buffer
    buffer[0] = '\0';
    error_code = 0;

    init_panels();

    // Check that there are not too many panels or pixels for the board
    if(!error_code){
        if(panel_count <= 0){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "panel_count is %d. No panels defined. Exiting", panel_count);
        } else if(panel_count > MAX_PANELS){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "MAX_PANELS is %d but panel_count is %d. Exiting", MAX_PANELS, panel_count);
        } else if(pixel_count <= 0){
            error_code = 10;
            snprintf(buffer, BUFFLEN, "pixel_count is %d. No pixels defined. Exiting", pixel_count);        
        } else if(pixel_count > MAX_PIXELS) {
            error_code = 10;
            snprintf(buffer, BUFFLEN, "MAX_PIXELS is %d but pixel_count is %d. Not enough memory. Exiting", MAX_PIXELS, pixel_count);        
        } else {
            error_code = 10;
            snprintf(buffer, BUFFLEN, "Setup: OK");
        }
    }
    if(error_code){
        // If there was an error, print the error code before the out buffer
        Serial.print("E");
        Serial.print(error_code);
    } else {
        // Else the buffer is a comment
        Serial.print("; ");
    }
    if(buffer[0] != '\0'){
        if(error_code){
            // In the case of an error code and a non-blank out buffer, print a delimeter
            Serial.print(": ");
        }
    }
    Serial.println(buffer);
    if(error_code){
        // In the case of an error, stop execution
        stop();
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