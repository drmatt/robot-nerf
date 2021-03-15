

#define STEP_PIN 18
#define DIR_PIN 5
#define BOTTOM_PIN 23
#define POT_PIN 15

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

  pinMode( STEP_PIN, OUTPUT );
  pinMode( DIR_PIN, OUTPUT );
  pinMode( POT_PIN, INPUT );
  pinMode( BOTTOM_PIN, INPUT_PULLUP );

  isHomed = false;
  Serial.println( "Homing Z...." );

}

void loop()
{

// Z
  //int accelerateCount = 20;
  //int rapidCount = 2000;
  // bool forward = true;
  //int minv = 400;
  //int maxv = 2000;
 
  
  if (!isHomed) {
     
      int home = digitalRead( BOTTOM_PIN );
      if (home == HIGH) {
        isHomed = true;
        Serial.println( "DONE" );
        return;
      } else {
        Serial.print( "." );
        
      }
      bool forward = false;
      
      digitalWrite( DIR_PIN, forward?HIGH:LOW );

      digitalWrite( STEP_PIN, HIGH );
      delay(1);
      digitalWrite( STEP_PIN, LOW );
      delay(1);
      
  } 
  else {
    double desiredPosition = (analogRead( POT_PIN ) / 4096.0) * 180.0;

    double f = K * (desiredPosition - position) - d*speed;

    double a = f / mass ;
    speed += a * (dt/1000000);
    position += speed * (dt/1000000);

    int desiredSteps = position * stepsPerDegree;
    
    if (actualSteps<desiredSteps) {
       digitalWrite( DIR_PIN, HIGH );
     //  Serial.println("LOW");
       actualSteps ++;
       digitalWrite( STEP_PIN, HIGH );
       delayMicroseconds( dt/2 );
       digitalWrite( STEP_PIN, LOW );
       delayMicroseconds( dt/2 );
    } else if (actualSteps>desiredSteps) {
       digitalWrite( DIR_PIN, LOW );
      // Serial.println("HIGH");
       actualSteps --;
       digitalWrite( STEP_PIN, HIGH );
       delayMicroseconds( dt/2 );
       digitalWrite( STEP_PIN, LOW );
       delayMicroseconds( dt/2 );
    } else {
      //Serial.println("---");
       delayMicroseconds( dt );
    }

    
  }

  // delayMicroseconds( dt );
//delay( 1000 );
//  
//
//   int currentSteps = 0;
//   int desiredSteps = 0;
//   while( true ) {
//
//      
//       desiredSteps += (analogRead( POT_PIN ) /5  -desiredSteps) *0.5;
//
//       int diff = desiredSteps - currentSteps;
//
//  
//      
//
//       Serial.print( "diff=" );
//       Serial.println( diff );
//
//       Serial.print( "currentSteps=" );
//       Serial.println( currentSteps );
//
//      Serial.print( "desiredSteps=" );
//       Serial.println( desiredSteps );
//       
//       digitalWrite( DIR_PIN, (diff>0)?HIGH:LOW );
//       
//       for( int i=0; i< min( 50, abs(diff)); i++) {
//        
//         digitalWrite( STEP_PIN, HIGH );
//         delayMicroseconds( 1000 );
//         digitalWrite( STEP_PIN, LOW );
//         delayMicroseconds( 1000 );
//
//          if (diff<0)
//           currentSteps --;
//          else if (diff>0)
//           currentSteps ++;
//          
//           
//        
//       }
//       
//       //delay( 100 );
//   }
  
//  forward = true;
//  digitalWrite( DIR_PIN, forward?HIGH:LOW );
//  
//  while( true ) {
//
//    // accelerate
//    for( int i=0; i<accelerateCount; i++) {
//
//      digitalWrite( STEP_PIN, HIGH );
//      
//      delayMicroseconds( minv + (maxv * (1-i/(float)accelerateCount) ) );
//      digitalWrite( STEP_PIN, LOW );
//      
//      delayMicroseconds( minv + (maxv *(1-i/(float)accelerateCount)) );
//      
//    }
//
// // rapid
//    for( int i=0; i<rapidCount; i++) {
//
//      digitalWrite( STEP_PIN, HIGH );
//      
//      delayMicroseconds( minv  );
//      digitalWrite( STEP_PIN, LOW );
//      
//      delayMicroseconds( minv  );
//      
//    }
//
//    // deccelerate
//    for( int i=0; i<accelerateCount; i++) {
//
//      digitalWrite( STEP_PIN, HIGH );
//     delayMicroseconds( minv + (maxv * (i/(float)accelerateCount) ) );
//      digitalWrite( STEP_PIN, LOW );
//      
//      delayMicroseconds( minv + (maxv * (i/(float)accelerateCount) ) );
//      
//    }
//
//  
//    forward = !forward;
//
//    Serial.println(  forward?"FORWARD":"BACKWARD" );
//      
//    digitalWrite( DIR_PIN, forward?HIGH:LOW );
//
//    
//}
  
}
