// Works with serial_stream_test.py
// Echo back the array sent by the python script
// TODO:
// Work on arduino_stream_pixels.ino

#define num_LED 5

void setup() {
  Serial.begin(9600);
  Serial.println("Connected");
}

void loop() {
  byte data_values[num_LED][3];
  int bytes_read = 0;
  byte LED_array = 0;
  String inString = "";    // string to hold input
  delay(100);


  Serial.println("Loop start");

  while (bytes_read < num_LED * 3) {
    int col = 0;
    while (col < 3) {
      while (Serial.available() > 0) {
        int inChar = Serial.read();
        if (isDigit(inChar)) {
          inString += (char)inChar; // convert the incoming byte to a char and add it to the string
          //Serial.println(inChar);
        }
        if (inChar == '\n') {
          data_values[bytes_read][col] = inString.toInt();
          Serial.println(data_values[bytes_read][col], DEC);
          inString = "";
        }
        col ++;
        bytes_read ++;
      }
    }
  }

  LED_array = data_values[1][0];
  Serial.println(LED_array);
  /*
  for (int i = 0; i < num_LED; i++){
    byte red = data_values[i][0];
    byte green = data_values[i][1];
    byte blue = data_values[i][2];



    //leds[i].setRGB(red, green, blue);
    Serial.print(" red ");
    Serial.print(red);
    Serial.print(" green ");
    Serial.print(green);
    Serial.print(" blue ");
    Serial.println(blue);
    Serial.print(" LED #");
    Serial.println(i);
  }
  */
  Serial.println("Loop end");
}
