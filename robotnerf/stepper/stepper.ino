

#define PIN_STEP_X  2
#define PIN_DIR_X   5

#define PIN_LIMIT_X 9
#define PIN_POT     15

bool isHomed;
int accelerateCount = 20;
int rapidCount = 100;
double dt = 50.0; // microseconds

int minv = 300;
int maxv = 2000;

float stepsPerDegree = 4 * 900.0 / 180.0; 


// simulation
double mass = 1;
double K = 25;
double d = 10;
double position = 0;
double speed = 0;

int actualSteps = 0;

void setup()
{
  Serial.begin(9600);
  Serial.println("Stepper test!");

  pinMode( PIN_STEP_X, OUTPUT );
  pinMode( PIN_DIR_X, OUTPUT );
  // pinMode( PIN_POT_PIN, INPUT );
  pinMode( PIN_LIMIT_X, INPUT_PULLUP );

  isHomed = false;
  Serial.println( "Homing Z...." );

}

double desiredPosition = 0;

void loop()
{

//Serial.println( "loop" );

// Z
  //int accelerateCount = 20;
  //int rapidCount = 2000;
  // bool forward = true;
  //int minv = 400;
  //int maxv = 2000;
  
  // send data only when you receive data:
  // if (Serial.available() > 0) {

  //   String s1 = Serial.readStringUntil('\r\n');
  //   int n = s1.toInt();
  //   desiredPosition = (double)n;
  //   if (desiredPosition<0) desiredPosition=0;
  //   if (desiredPosition>180) desiredPosition=180;

  //  Serial.print( "Desired:" );
  //  Serial.println( desiredPosition );
  //   // read the incoming byte:
  //   // int incomingByte = Serial.read();
  //   // desiredPosition = incomingByte;
  //   // Serial.println( desiredPosition );
  //   // // say what you got:
  //   // Serial.print("I received: ");
  //   // Serial.println(incomingByte, DEC);
  // }
 
  
  if (!isHomed) {
     
      int home = digitalRead( PIN_LIMIT_X );
      if (home == HIGH) {
        isHomed = true;
        Serial.println( "HOME" );
        return;
      } 
      
      bool forward = false;
      
      digitalWrite( PIN_DIR_X, forward?HIGH:LOW );

      digitalWrite( PIN_STEP_X, HIGH );
      delay(1);
      digitalWrite( PIN_STEP_X, LOW );
      delay(1);
      
  } 
  // else {
  //   //double desiredPosition = 90 ; //(analogRead( POT_PIN ) / 4096.0) * 180.0;

  //   double f = K * (desiredPosition - position) - d*speed;

  //   double a = f / mass ;
  //   speed += a * (dt/1000000);
  //   position += speed * (dt/1000000);

  //   int desiredSteps = position * stepsPerDegree;
    
  //   if (actualSteps<desiredSteps) {
  //      digitalWrite( PIN_DIR_X, HIGH );
  //    //  Serial.println("LOW");
  //      actualSteps ++;
  //      digitalWrite( PIN_STEP_X, HIGH );
  //      delayMicroseconds( dt/2 );
  //      digitalWrite( PIN_STEP_X, LOW );
  //      delayMicroseconds( dt/2 );
  //   } else if (actualSteps>desiredSteps) {
  //      digitalWrite( PIN_DIR_X, LOW );
  //     // Serial.println("HIGH");
  //      actualSteps --;
  //      digitalWrite( PIN_STEP_X, HIGH );
  //      delayMicroseconds( dt/2 );
  //      digitalWrite( PIN_STEP_X, LOW );
  //      delayMicroseconds( dt/2 );
  //   } else {
  //     //Serial.println("---");
  //      delayMicroseconds( dt );
  //   }

    
  // }

}
