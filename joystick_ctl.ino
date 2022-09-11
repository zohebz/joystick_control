int VRx= A0;
int VRy= A1;

int read_x = 0;
int read_y = 0;

int map_x = 0;
int map_y = 0;

int out1 = 8;
int out2 = 9;
int out3 = 2;
int out4 = 3;
int out5 = 4;
int out6 = 5;
int out7 = 6;
int out8 = 7;

//out1 and out3 LOW --> front force
//out2 and out4 LOW --> back force
//out5 and out7 LOW --> left force
//out6 and out8 LOW --> right force

char initial_input = '0';
char mode = '0'; 

// mode=1 for no force feedback
// mode=2 for force feedback

unsigned long start_time = 0;
unsigned long stop_time = 0;

int feedback;
int feedback_duration = 1000; //feedback applied for 1 sec
unsigned long feedback_start_time = 0;

void front_force() {
  digitalWrite(out1, LOW);
  digitalWrite(out2, HIGH);
  digitalWrite(out3, LOW);
  digitalWrite(out4, HIGH);
  digitalWrite(out5, HIGH);
  digitalWrite(out6, HIGH);
  digitalWrite(out7, HIGH);
  digitalWrite(out8, HIGH);
}

void back_force() {
  digitalWrite(out1, HIGH);
  digitalWrite(out2, LOW);
  digitalWrite(out3, HIGH);
  digitalWrite(out4, LOW);
  digitalWrite(out5, HIGH);
  digitalWrite(out6, HIGH);
  digitalWrite(out7, HIGH);
  digitalWrite(out8, HIGH);
}

void left_force() {
  digitalWrite(out1, HIGH);
  digitalWrite(out2, HIGH);
  digitalWrite(out3, HIGH);
  digitalWrite(out4, HIGH);
  digitalWrite(out5, LOW);
  digitalWrite(out6, HIGH);
  digitalWrite(out7, LOW);
  digitalWrite(out8, HIGH);
}

void right_force() {
  digitalWrite(out1, HIGH);
  digitalWrite(out2, HIGH);
  digitalWrite(out3, HIGH);
  digitalWrite(out4, HIGH);
  digitalWrite(out5, HIGH);
  digitalWrite(out6, LOW);
  digitalWrite(out7, HIGH);
  digitalWrite(out8, LOW);
}

void zero_force() {
  digitalWrite(out1, HIGH);
  digitalWrite(out2, HIGH);
  digitalWrite(out3, HIGH);
  digitalWrite(out4, HIGH);
  digitalWrite(out5, HIGH);
  digitalWrite(out6, HIGH);
  digitalWrite(out7, HIGH);
  digitalWrite(out8, HIGH);
}


void setup() {
  Serial.begin(9600);
   
  pinMode(VRx, INPUT);
  pinMode(VRy, INPUT);
  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT);
  pinMode(out3, OUTPUT);
  pinMode(out4, OUTPUT);
  pinMode(out5, OUTPUT);
  pinMode(out6, OUTPUT);
  pinMode(out7, OUTPUT);
  pinMode(out8, OUTPUT);  
  digitalWrite(out1, HIGH);
  digitalWrite(out2, HIGH);
  digitalWrite(out3, HIGH);
  digitalWrite(out4, HIGH);
  digitalWrite(out5, HIGH);
  digitalWrite(out6, HIGH);
  digitalWrite(out7, HIGH);
  digitalWrite(out8, HIGH);

  feedback=0;
}

void loop() {
  //Serial.println("start loop");
  unsigned long current_time = millis();
  //Serial.println(current_time);
  if(mode=='0'){
    if(Serial.available()){
        initial_input = Serial.read();
        Serial.print("mode: " );
        Serial.print(initial_input);
        Serial.println();
    }
    mode = initial_input;
    start_time = current_time;
  }
  else if(mode!='\0'){
    read_x = analogRead(VRx);
    read_y = analogRead(VRy);
  
    map_x = map(read_x, 0, 1023, -512, 512);
    map_y = map(read_y, 0, 1023, -512, 512);

    Serial.print("X:");
    Serial.print(map_x);
    Serial.print("| Y:");
    Serial.print(map_y);

    Serial.println();

    if(mode == '2'){
      if(feedback==0){
        int random_force=(rand() % 4)+1;
        if(random_force==1){
          front_force();
          Serial.println("front force");
        }
        if(random_force==2){
          back_force();
          Serial.println("back force");
        }
        if(random_force==3){
          left_force();
          Serial.println("left force");
        }
        if(random_force==4){
          right_force();
          Serial.println("right force");
        }
        feedback=1;
        feedback_start_time = current_time;
      }
      else{
        if((current_time - feedback_start_time)>feedback_duration){
          zero_force();
          Serial.println("stop force");
          feedback=0;
        }
      }
    }
    
    //Serial.println(current_time - start_time);
    if((current_time - start_time)>120000){
      Serial.println("reset");
      start_time = current_time;
      initial_input = '0';
      mode = '0';
      feedback=0;
      zero_force();
    }
  }
  delay(100);
  //Serial.println("end loop");
}
