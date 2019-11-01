// 소프트웨어 동아리 경진대회 Main 아두이노 파일
// 파일 이름: Rfid_Arduino.ino
// 제작 : 일산대진고등학교 2학년 '재간둥이 Team'
// 최근 업데이트: 19.11.1 (Ver 1.1)


// 라이브러리 해더
#include <SPI.h>
#include <MFRC522.h>

// SS(Chip Select)과 RST(Reset) 핀 설정
// 나머지 PIN은 SPI 라이브러리를 사용하기에 별도의 설정이 필요없다.
#define SS_PIN 10
#define RST_PIN 9

#include <LiquidCrystal_I2C.h>     //LiquidCrystal 라이브러리 추가
LiquidCrystal_I2C lcd(0x3F, 16, 2);  //lcd 객체 선언

// 라이브러리 생성
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class

MFRC522::MIFARE_Key key;

//이전 ID와 비교하기위한 변수
byte nuidPICC[4];

void setup() {

        lcd.begin(); //LCD 사용 시작

        Serial.begin(9600);
        SPI.begin(); // SPI 시작
        rfid.PCD_Init(); // RFID 시작

        //초기 키 ID 초기화
        for (byte i = 0; i < 6; i++) {
                key.keyByte[i] = 0xFF;
        }
//
//  Serial.println(F("This code scan the MIFARE Classsic NUID."));
//  Serial.print(F("Using the following key:"));
        printHex(key.keyByte, MFRC522::MF_KEY_SIZE);
}

void loop() {
        Serial.print(F("Off "));
        delay(1000);
        // 카드가 인식되었다면 다음으로 넘어가고 아니면 더이상
        // 실행 안하고 리턴
        if ( !rfid.PICC_IsNewCardPresent())
                return;

        // ID가 읽혀졌다면 다음으로 넘어가고 아니면 더이상
        // 실행 안하고 리턴
        if ( !rfid.PICC_ReadCardSerial())
                return;
//  Serial.print(F("PICC type: "));

        //카드의 타입을 읽어온다.
        MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

        //모니터에 출력
//  Serial.println(rfid.PICC_GetTypeName(piccType));


        // 만약 바로 전에 인식한 RF 카드와 다르다면..
        if (rfid.uid.uidByte[0] != nuidPICC[0] ||
            rfid.uid.uidByte[1] != nuidPICC[1] ||
            rfid.uid.uidByte[2] != nuidPICC[2] ||
            rfid.uid.uidByte[3] != nuidPICC[3] ) {
//    Serial.println(F("A new card has been detected."));

                // ID를 저장해둔다.
                for (byte i = 0; i < 4; i++) {
                        nuidPICC[i] = rfid.uid.uidByte[i]
                        ;
                }

                //모니터 출력
//    Serial.println(F("The NUID tag is:"));

                Serial.print(F("ON"));
                delay(2000);


                //16진수로 변환해서 출력
//    printHex(rfid.uid.uidByte, rfid.uid.size);
//    Serial.println();


//    Serial.print(F("In dec: "));
//    //10진수로 출력
//    printDec(rfid.uid.uidByte, rfid.uid.size);
//    Serial.println();

                lcd.setCursor(3, 0); // 커서를 5, 0에 가져다 놓아라. (열, 행)
                lcd.print("Black box");
                lcd.setCursor(3, 1); // 커서를 3, 1로 가져다 놓아라. (열, 행)
                lcd.print("will work");
                delay(1000);
                lcd.clear(); // 글자를 모두 지워라.
                delay(1000);
                lcd.setCursor(3, 0); // 커서를 5, 0에 가져다 놓아라. (열, 행)
                lcd.print("Connecting");
                lcd.setCursor(3, 1); // 커서를 3, 1로 가져다 놓아라. (열, 행)
                lcd.print("with owner");
                delay(5000);
                lcd.clear();
        }
        else {
                Serial.println(F("Card read previously.")); //바로 전에 인식한 것과 동일하다면
        }

        // PICC 종료
        rfid.PICC_HaltA();

        // 암호화 종료(?)
        rfid.PCD_StopCrypto1();

        //다시 처음으로 돌아감.
}

//16진수로 변환하는 함수
void printHex(byte *buffer, byte bufferSize) {
        for (byte i = 0; i < bufferSize; i++) {
                Serial.print(buffer[i] < 0x10 ? " 0" : " ");
                Serial.print(buffer[i], HEX);
        }
}

//10진수로 변환하는 함수
void printDec(byte *buffer, byte bufferSize) {
        for (byte i = 0; i < bufferSize; i++) {
                Serial.print(buffer[i] < 0x10 ? " 0" : " ");
                Serial.print(buffer[i], DEC);
        }
}
