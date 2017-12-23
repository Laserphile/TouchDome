
int redPin = 6, greenPin = 5, bluePin = 3;

int delayLed = 10; // The time that passes between each change of LED (ms)
// Variables that store the last colour of each LED
int red_old = 0, green_old = 0, blue_old = 0; 

void setup() {

  // Starting the serial port.
  Serial.begin(9600);
  // We mark the pins used as output.
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  Serial.println("Ready!");
}

void loop() {

  // If information is available in the serial port we will use it:
  while (Serial.available() == 1) {
    Serial.println("Received");
    
    int red = 0, green = 0, blue = 0;

    // search for the next valid chain of whole numbers and 
    // assign the value converted to a whole number to the corresponding variable
    red = Serial.parseInt();
    Serial.println("Red");
    // search again.
    green = Serial.parseInt();
    // search again:
    blue = Serial.parseInt();

    // search for the end of line character. Tell the program that the entering of data has been finished.
    // If you use the Arduino IDE or another IDE that allows the format to be included
    // of the new line on sending data via the serial monitor, delete the comment
    // from line 33 and comment on line 34.
    
    if (Serial.read() == '\n'){
    //if (Serial.read() == '*'){

      // Using constrain, we make sure that the value is within the PWM range
      // For common anode LEDS use, for example, for red: red = 255 - constrain(red, 0, 255);
      red = constrain(red, 0, 255);
      green = constrain(green, 0, 255);
      blue = constrain(blue, 0, 255);

      // print the three numbers in one string as hexadecimal:
      Serial.print(red, HEX);
      Serial.print(green, HEX);
      Serial.println(blue, HEX);

      // We change the colour of the RGB LED
      fade(redPin, red, red_old);
      fade(greenPin, green, green_old);
      fade(bluePin, blue, blue_old);
      
      Serial.println("Colour changed");
      // We store the data of the previous colours.
      red_old = red;
      green_old = green;
      blue_old = blue;
    }
  }
}

void fade(int pin, int newValue, int aktValue) {

  //  This function changes each colour from the current value to the next
  //  We can distinguish between two cases:
  //  1 - The new value is higher than the current value, so we need to increase it
  //  2 - The new value is lower than the current value, so we need to reduce it

  if (newValue > aktValue) {
    for (int i = aktValue; i <= newValue; i++) {       analogWrite(pin, i);       delay(delayLed);     }   } else if (newValue > aktValue) {
     for (int i = aktValue; i >= newValue; i--) {
      analogWrite(pin, i);
      delay(delayLed);
    }
  }
}
