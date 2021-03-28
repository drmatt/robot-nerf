

#define PIN_STEP_X  2
#define PIN_DIR_X   5

#define PIN_GUN   12

#define PIN_LIMIT_X 9
#define PIN_POT     15

bool isHomed;
int accelerateCount = 20;
int rapidCount = 100;
double dt = 200.0;//50.0; // microseconds
int desiredSteps = 0;

int minv = 300;
int maxv = 2000;

float minAngle = -113;
float maxAngle = 113;

float stepsPerDegree = 4 * 900.0 / 180.0; 



double desiredPosition = 0;

// simulation
// double mass = 0.5;
// double K = 60;
// double d = 17;
// double position = minAngle;
// double speed = 0;

double mass = 4;
double K = 20;
double d = 20;
double position = minAngle;
double speed = 0;

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
  pinMode( PIN_GUN, OUTPUT );
  
  // pinMode( PIN_POT_PIN, INPUT );
  pinMode( PIN_LIMIT_X, INPUT_PULLUP );

  isHomed = false;
  Serial.println( "Homing Z...." );

  desiredPosition = 0;
  position = stepsToAngle(0);

  Serial.print( "desiredPosition: " );
  Serial.println( desiredPosition );

  Serial.print( "position: " );
  Serial.println( position );

}

void update3() {
  double a = 800;

  double maxSpeed = 50;

    if (!isDecelerating) {

      if (desiredPosition>position) {
        speed += a * (dt / 1000000);
      } else { 
        speed -= a * (dt / 1000000);
      }

        if (speed>maxSpeed)
          speed = maxSpeed;
        else if (speed<-maxSpeed)
          speed = -maxSpeed;
        
        position += speed * (dt / 1000000);

        float distanceToDecelerate = abs( 0.5*speed*speed/a );
        float d = abs(desiredPosition-position);

        if (distanceToDecelerate>=d)
            isDecelerating = true;

    } else {
        // need to adjust this to make it stop in the right place
        float d = abs( desiredPosition-position );
        float dec = abs( 0.5*speed*speed / d );


        if (desiredPosition >position) {
            speed -= dec * (dt / 1000000);
            if (speed<0)
                speed = 0;
        } else {
            speed += dec * (dt / 1000000);
            if (speed>0)
              speed = 0;
        }
            
        position += speed * (dt / 1000000);
    }


    int desiredSteps = angleToSteps( position );
    
    if (actualSteps<desiredSteps) {
       digitalWrite( PIN_DIR_X, HIGH );
     //  Serial.println("LOW");
       actualSteps ++;
       digitalWrite( PIN_STEP_X, HIGH );
       delayMicroseconds( dt/2 );
       digitalWrite( PIN_STEP_X, LOW );
       delayMicroseconds( dt/2 );
    } else if (actualSteps>desiredSteps) {
       digitalWrite( PIN_DIR_X, LOW );
      // Serial.println("HIGH");
       actualSteps --;
       digitalWrite( PIN_STEP_X, HIGH );
       delayMicroseconds( dt/2 );
       digitalWrite( PIN_STEP_X, LOW );
       delayMicroseconds( dt/2 );
    } else {
      //Serial.println("---");
       delayMicroseconds( dt );
    }
}

void update2() {
    double maxAcceleration = 10000;
    double decceleration = 10000;
    double deccelerateDistance = 5;
    
    double e = (desiredPosition - position);
    
    // calculate if it should deccelerate
    double distance = abs(e);
    if (distance < deccelerateDistance) {
      Serial.println( "deccelerate" );
      if (e>0) {
        speed -= decceleration;
        if (speed<0) speed =0;
      } else {
        speed += decceleration;
        if (speed>0) speed =0;
      }
      
    } else {

  //     //speed factor
  //     double f = 100;

  //     double maxSpeed = 1000;

  //     double desiredSpeed = e * f;

  //     if (desiredSpeed>maxSpeed) desiredSpeed=maxSpeed;
  //     if (desiredSpeed<-maxSpeed) desiredSpeed=-maxSpeed;
      
  //     Serial.print( "accelerate" );

  // Serial.print( "e:" );
  //     Serial.println( e);

  //     Serial.print( " desiredSpeed:" );
  //     Serial.println( desiredSpeed);

  //     if (desiredSpeed>speed) {


  //       speed += maxAcceleration;
  //       if (speed>desiredSpeed)
  //         speed = desiredSpeed;

  //     } else if (desiredSpeed<speed)  {

  //       speed -= maxAcceleration;
  //       if (speed<desiredSpeed)
  //         speed = desiredSpeed;

  //     }
   }
}

void update() {
    double f = K * (desiredPosition - position) - d*speed;

    double a = f / mass ;

    speed += a * (dt/1000000);
    position += speed * (dt/1000000);

    // if (position<minAngle) position=minAngle;
    // if (position>maxAngle) position=maxAngle;

    int desiredSteps = angleToSteps( position );
    
    if (actualSteps<desiredSteps) {
       digitalWrite( PIN_DIR_X, HIGH );
     //  Serial.println("LOW");
       actualSteps ++;
       digitalWrite( PIN_STEP_X, HIGH );
       delayMicroseconds( dt/2 );
       digitalWrite( PIN_STEP_X, LOW );
       delayMicroseconds( dt/2 );
    } else if (actualSteps>desiredSteps) {
       digitalWrite( PIN_DIR_X, LOW );
      // Serial.println("HIGH");
       actualSteps --;
       digitalWrite( PIN_STEP_X, HIGH );
       delayMicroseconds( dt/2 );
       digitalWrite( PIN_STEP_X, LOW );
       delayMicroseconds( dt/2 );
    } else {
      //Serial.println("---");
       delayMicroseconds( dt );
    }
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
    } else {
        int n = s1.toInt();
       // desiredSteps = n;
        desiredPosition = (double)n;
        if (desiredPosition<minAngle) desiredPosition=minAngle;
        if (desiredPosition>maxAngle) desiredPosition=maxAngle;
    
      Serial.print( "Desired:" );
      Serial.println( desiredPosition );
       
      // int desiredSteps = angleToSteps( desiredPosition );
    
      // Serial.print( "Desired:" );
      // Serial.println( desiredSteps );
    
       isDecelerating = false;
    }

  }
 
  
  if (!isHomed) {
     
      int home = digitalRead( PIN_LIMIT_X );
       if (home == HIGH) {
         isHomed = true;
         Serial.println("HOME");
         //Serial.println( (home == LOW)?"LOW":"HIGH" );
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
