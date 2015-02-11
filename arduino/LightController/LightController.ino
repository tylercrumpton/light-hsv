#include <Adafruit_NeoPixel.h>
#include <SoftwareSerial.h>

// LED Strip Parameters:
#define LED_PIN   6
#define LED_COUNT 300
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

uint8_t fgRed   = 255;
uint8_t fgGreen = 255;
uint8_t fgBlue  = 255;
uint8_t bgRed   = 0;
uint8_t bgGreen = 0;
uint8_t bgBlue  = 0;

int NORMAL_SEG_LENGTH = 5;
int NORMAL_BLUR_STEPS = 3;

typedef enum {
    NORMAL_STATE,
    COMMAND_STATE,
    RAINBOW_STATE
} state_t;
state_t state = NORMAL_STATE;

const uint8_t SET_LIGHT_MODE = 0x01;
const uint8_t RAINBOW_MODE   = 0x02;
const uint8_t TEAM_MODE      = 0x03;
const uint8_t GLITTER_MODE   = 0x04;

int jump=0;
uint8_t degreeold=0;
#define SensorPin1      0
#define filterSamples   3              // filterSamples should  be an odd number, no smaller than 3
int sensSmoothArray1 [filterSamples];   // array for holding raw sensor values for sensor1 

int rawData1, smoothData1;  // variables for sensor1 data



//Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(120, PIN2, NEO_GRB + NEO_KHZ800);

SoftwareSerial softserial(A4, A3);

void setup() {
    softserial.begin(9600); //setup Serial
    Serial.begin(9600);
    // Serial.setTimeout(10);

    //Setup Strip 1
    strip.begin();
    strip.show(); // Initialize all pixels to 'off'
    strip.setBrightness(255); //Setup global brightness

    //Setup Strip 2
    //strip2.begin();
    //strip2.show(); // Initialize all pixels to 'off'
    //strip2.setBrightness(255); //Setup global brightness

    // initialize serial communication with computer:
    Serial.begin(9600);      
    Serial.println("Initialized.");    
}

void loop() {
    if(softserial.available()) {
        uint8_t degree = softserial.read(); //incoming serial stream
        if (degree== 255) {
            state = COMMAND_STATE;
            Serial.println("Received COMMAND_STATE byte.");
        }
        if(state==NORMAL_STATE) {
            degree=(degree/2);
            rawData1 = degree;                       // read sensor 1
            degree = digitalSmooth(rawData1, sensSmoothArray1);  // every sensor you use with digitalSmooth needs its own array

            if(degree>degreeold) {
                jump= ((degree - degreeold)/10) +1;
                for(int i= degreeold; i <= degree; i+=jump) {
                    colorSeg(strip.Color(fgRed,fgGreen,fgBlue), strip.Color(bgRed, bgGreen, bgBlue),  i, NORMAL_SEG_LENGTH);
                }
            }
            
            if(degree<degreeold) {
                jump= ((degreeold -degree)/10) +1;
                for(int i= degreeold; i >= degree; i-=jump) {
                    colorSeg(strip.Color(fgRed,fgGreen,fgBlue), strip.Color(bgRed, bgGreen, bgBlue),  i, NORMAL_SEG_LENGTH);
                }
            }
            
            degreeold=degree;
        }
        else if(state==RAINBOW_STATE) {
            degree=(degree/2);
            rawData1 = degree;                       // read sensor 1
            degree = digitalSmooth(rawData1, sensSmoothArray1);  // every sensor you use with digitalSmooth needs its own array

            if(degree>degreeold) {
                jump= ((degree - degreeold)/10) +1;
                for(int d= degreeold; d <= degree; d+=jump) {
                    for(int i=0; i<strip.numPixels(); i++) {
                        strip.setPixelColor(i, Wheel((i+d) & 255));
                    }
                    strip.show();
                }
            }
            
            if(degree<degreeold) {
                jump= ((degreeold -degree)/10) +1;
                for(int d= degreeold; d >= degree; d-=jump) {
                    for(int i=0; i<strip.numPixels(); i++) {
                        strip.setPixelColor(i, Wheel((i+d) & 255));
                    }
                    strip.show();
                }
            }
            
            degreeold=degree;
        }
        else if(state==COMMAND_STATE) {
            while(!softserial.available()) {
                // Spin here while we wait for more bytes
            }
            uint8_t infeed  = softserial.read(); //incoming serial stream
            if (infeed == SET_LIGHT_MODE) {
                Serial.println("Received SET_LIGHT_MODE byte.");
                serialReadRGB(fgRed, fgGreen, fgBlue);
                state=NORMAL_STATE;
            }
            else if(infeed == RAINBOW_MODE) {
                Serial.println("Received RAINBOW_MODE byte.");
                Serial.println("Entering RAINBOW_STATE.");
                state=RAINBOW_STATE;
            }
            else if(infeed == TEAM_MODE) {
                // TODO: Add Team Mode
                Serial.println("Received TEAM_MODE byte.");
                serialReadRGB(fgRed, fgGreen, fgBlue);
                serialReadRGB(bgRed, bgGreen, bgBlue);
                Serial.println("Returning to NORMAL_STATE.");
                state=NORMAL_STATE;
            }
            else if(infeed == GLITTER_MODE) {
                // TODO: Add Glitter Mode
                Serial.println("Received GLITTER_MODE byte.");
                Serial.println("Returning to NORMAL_STATE.");
                state=NORMAL_STATE;
            }
            else {
                Serial.print("Returning to normal state, value:");
                Serial.println(infeed);
                state=NORMAL_STATE;
            }
        }
    }
}

void serialReadRGB(uint8_t &red, uint8_t &green, uint8_t &blue)
{
    while(!softserial.available()) {
        // Spin here while we wait for more bytes
    }
    red  = softserial.read();
    Serial.print("r:");
    Serial.print(red);
    while(!softserial.available()) {
        // Spin here while we wait for more bytes
    }
    green  = softserial.read();
    Serial.print(",g:");
    Serial.print(green);
    while(!softserial.available()) {
        // Spin here while we wait for more bytes
    }
    blue  = softserial.read();
    Serial.print(",b:");
    Serial.println(blue);
}

// "int *sensSmoothArray" passes an array to the function - the asterisk indicates the array name is a pointer
int digitalSmooth(int rawIn, int *sensSmoothArray)
{     
    int j, k, temp, top, bottom;
    long total;
    static int i;
    // static int raw[filterSamples];
    static int sorted[filterSamples];
    boolean done;

    i = (i + 1) % filterSamples;    // increment counter and roll over if necc. -  % (modulo operator) rolls over variable
    sensSmoothArray[i] = rawIn;                 // input new data into the oldest slot

    // Serial.print("raw = ");

    for (j=0; j<filterSamples; j++){     // transfer data array into anther array for sorting and averaging
        sorted[j] = sensSmoothArray[j];
    }

    done = 0;                // flag to know when we're done sorting              
    while(done != 1){        // simple swap sort, sorts numbers from lowest to highest
        done = 1;
        for (j = 0; j < (filterSamples - 1); j++){
            if (sorted[j] > sorted[j + 1]){     // numbers are out of order - swap
                temp = sorted[j + 1];
                sorted [j+1] =  sorted[j] ;
                sorted [j] = temp;
                done = 0;
            }
        }
    }


    // throw out top and bottom 15% of samples - limit to throw out at least one from top and bottom
    bottom = max(((filterSamples * 15)  / 100), 1); 
    top = min((((filterSamples * 85) / 100) + 1  ), (filterSamples - 1));   // the + 1 is to make up for asymmetry caused by integer rounding
    k = 0;
    total = 0;
    for ( j = bottom; j< top; j++){
        total += sorted[j];  // total remaining indices
        k++;
    }

    return total / k;    // divide by number of samples
}

void turnoff() {
    for(uint16_t i=0; i<LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0,0,0));
        //strip2.setPixelColor(i, strip.Color(0,0,0));
    }
}

//short segment of moving color
void colorSeg(uint32_t fgColor, uint32_t bgColor, uint8_t location, uint32_t length) {
    // Set all of the pixels up to the start of the blue to the background color:
    for(int n=0; n<location; n++) {
        strip.setPixelColor(n, bgColor);
    }
    // Blur a number of pixels up to the start of the segment (and on the downside):
    int blueDiff = (fgColor & 0xFF) - (bgColor & 0xFF);
    int greenDiff = (fgColor>>8 & 0xFF) - ((bgColor>>8) & 0xFF);
    int redDiff = (fgColor>>16 & 0xFF) - ((bgColor>>16) & 0xFF);
    for(int i=0; i<NORMAL_BLUR_STEPS; i++) {
        int blurRed = redDiff * (i + 1) / (NORMAL_BLUR_STEPS + 1);
        blurRed += (bgColor>>16) & 0xFF;
        int blurGreen = greenDiff * (i + 1) / (NORMAL_BLUR_STEPS + 1);
        blurGreen += (bgColor>>8) & 0xFF;
        int blurBlue = blueDiff * (i + 1) / (NORMAL_BLUR_STEPS + 1);
        blurBlue += bgColor & 0xFF;
        uint32_t blurColor = strip.Color(blurRed, blurGreen, blurBlue);
        strip.setPixelColor(location + i, blurColor);
        strip.setPixelColor(location + NORMAL_BLUR_STEPS + length + NORMAL_BLUR_STEPS - i - 1, blurColor);
    }
    // Set the color of the segement pixels:
    for(uint16_t i=location+NORMAL_BLUR_STEPS; i<location+NORMAL_BLUR_STEPS+length; i++) {
        strip.setPixelColor(i, fgColor);
    }
    // Fill the rest of the strip with background:
    for(int n=location+NORMAL_BLUR_STEPS+length+NORMAL_BLUR_STEPS; n<LED_COUNT; n++) {
        strip.setPixelColor(n, bgColor);
    }
    strip.show();

}

void rainbow(uint8_t wait) {
    uint16_t i, j;

    for(j=0; j<256; j++) {
        for(i=0; i<strip.numPixels(); i++) {
            strip.setPixelColor(i, Wheel((i+j) & 255));
            //strip2.setPixelColor(i, Wheel((i+j) & 255));
        }
        strip.show();
        //strip2.show();
        delay(wait);
    }
}

uint32_t Wheel(byte WheelPos) {
    WheelPos = 255 - WheelPos;
    if(WheelPos < 85) {
        return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
    } else if(WheelPos < 170) {
        WheelPos -= 85;
        return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
    } else {
        WheelPos -= 170;
        return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
    }
}
