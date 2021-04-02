

#define PIN_STEP_X  2
#define PIN_STEP_Y  3
#define PIN_STEP_Z  4

#define PIN_DIR_X   5
#define PIN_DIR_Y   6
#define PIN_DIR_Z   7

#define PIN_GUN   12

#define PIN_LIMIT_X 9
#define PIN_POT     15

bool isHomed;
int accelerateCount = 20;
int rapidCount = 100;
double dt = 200.0;
int desiredSteps = 0;

int minv = 300;
int maxv = 2000;

float minAngle = -113;
float maxAngle = 113;

float stepsPerDegree = 4 * 900.0 / 180.0; 

double desiredPosition = 0;

double mass = 4;
double K = 20;
double d = 20;
double position = minAngle;
double speed = 0;

bool isTriggerPulled = false;
float triggerPosition = 0;
float triggerMax = 250;

int actualSteps = 0;

bool isDecelerating = false;

int angleToSteps( float angle ) {
  return (angle+90)/180.0 * 3410 + 500;
}

float stepsToAngle( int steps ) {
  return  ((steps-500)/3410.0) * 180 - 90;
}

void setup()
{
  Serial.begin(9600);
  Serial.println("Stepper test!");

  pinMode( PIN_STEP_X, OUTPUT );
  pinMode( PIN_DIR_X, OUTPUT );

  pinMode( PIN_STEP_Y, OUTPUT );
  pinMode( PIN_DIR_Y, OUTPUT );

  pinMode( PIN_GUN, OUTPUT );
  
  // pinMode( PIN_POT_PIN, INPUT );
  pinMode( PIN_LIMIT_X, INPUT_PULLUP );

  triggerPosition = 0;
  isHomed = false;
  Serial.println( "Homing Z...." );

  desiredPosition = 0;
  position = stepsToAngle(0);

  Serial.print( "desiredPosition: " );
  Serial.println( desiredPosition );

  Serial.print( "position: " );
  Serial.println( position );

}


void update() {
    double f = K * (desiredPosition - position) - d*speed;

    double a = f / mass ;

    speed += a * (dt/1000000);
    position += speed * (dt/1000000);

    int desiredSteps = angleToSteps( position );
    bool stepY = false;
    bool stepX = false;

    if (isTriggerPulled && triggerPosition<triggerMax) {
      stepY = true;
      digitalWrite( PIN_DIR_Y, HIGH );
      triggerPosition ++;
    } else if (!isTriggerPulled && triggerPosition>0) {
      stepY = true;
      triggerPosition --;
      digitalWrite( PIN_DIR_Y, LOW );
    }

    if (actualSteps<desiredSteps) {
      digitalWrite( PIN_DIR_X, HIGH );
      actualSteps ++;
      stepX = true;
    } else if (actualSteps>desiredSteps) {
      digitalWrite( PIN_DIR_X, LOW );
      actualSteps --;
      stepX = true;
    }

    // Serial.print( "triggerPosition: " );
    // Serial.println( triggerPosition );

    if (stepY) digitalWrite( PIN_STEP_Y, HIGH );
    if (stepX) digitalWrite( PIN_STEP_X, HIGH );
    delayMicroseconds( dt/2 );

    if (stepY)  digitalWrite( PIN_STEP_Y, LOW );
    if (stepX) digitalWrite( PIN_STEP_X, LOW );
    delayMicroseconds( dt/2 );

   
}


void loop()
{

  
  // send data only when you receive data:
  if (Serial.available() > 0) {

    String s1 = Serial.readStringUntil('\r\n');
    s1.trim();
    
    Serial.print(">"+s1+"<");

    if (s1.equals( "h" )) {
      isHomed = false;
    } else if (s1.equals( "g1" )) {
      Serial.println("GUN ON");
      digitalWrite( PIN_GUN, HIGH );
    } else if (s1 == "g0") {
      Serial.println("GUN OFF");
      digitalWrite( PIN_GUN, LOW );
    } else if (s1.equals( "t1" )) {
      Serial.println("trigger ON");
      isTriggerPulled = true;
      // digitalWrite( PIN_GUN, HIGH );
    } else if (s1 == "t0") {
      Serial.println("trigger OFF");
      isTriggerPulled = false;
    } else {
      int n = s1.toInt();
      desiredPosition = (double)n;
      
      if (desiredPosition<minAngle) desiredPosition=minAngle;
      if (desiredPosition>maxAngle) desiredPosition=maxAngle;
    
      Serial.print( "Desired:" );
      Serial.println( desiredPosition );
    
    }

  }
 
  
  if (!isHomed) {
     
      int home = digitalRead( PIN_LIMIT_X );
       if (home == HIGH) {
         isHomed = true;
         Serial.println("HOME");
         return;
       } 
      
      bool forward = false;
      
      digitalWrite( PIN_DIR_X, forward?HIGH:LOW );

      digitalWrite( PIN_STEP_X, HIGH );
      delay(2);
      digitalWrite( PIN_STEP_X, LOW );
      delay(2);
      
  } 
  else {
    update();

    
  }

}
