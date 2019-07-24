/*******************************************************************************
End node da rede Lora WAN: enviamensagem para rede com periodicidade de um segundo

Társis Natan Boff da Silva
19/03/2019
 *******************************************************************************/

#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <MPU9250_asukiaaa.h>

#include <Arduino.h>
#include <stdint.h>
#include<string.h>


#ifdef _ESP32_HAL_I2C_H_
#define SDA_PIN 21
#define SCL_PIN 22
#endif
// LoRaWAN NwkSKey, network session key
// This is the default Semtech key, which is used by the early prototype TTN
// network.

static const PROGMEM u1_t NWKSKEY[16] = { 0x8F, 0xCB, 0x4B, 0x78, 0xDA, 0xD2, 0x1B, 0x14, 0x35, 0xD0, 0xFF, 0x1D, 0x88, 0xA1, 0xEE, 0x5F };

// LoRaWAN AppSKey, application session key
// This is the default Semtech key, which is used by the early prototype TTN
// network.
static const u1_t PROGMEM APPSKEY[16] =  { 0xCE, 0xD2, 0xA5, 0x18, 0xEB, 0xFC, 0x09, 0xD0, 0xDB, 0x05, 0xFB, 0x99, 0xB7, 0x19, 0xE0, 0x10 };

// LoRaWAN end-device address (DevAddr)
static const u4_t DEVADDR = 0x2603172D ; // <-- Change this address for every node!

// These callbacks are only used in over-the-air activation, so they are
// left empty here (we cannot leave them out completely unless
// DISABLE_JOIN is set in config.h, otherwise the linker will complain).
void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

static uint8_t mydata[6];
static osjob_t sendjob;

// Schedule TX every this many seconds (might become longer due to duty
// cycle limitations).
const unsigned TX_INTERVAL = 1;

// Pin mapping
const lmic_pinmap lmic_pins = {
    .nss = 18,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 23,
    .dio = {26, 33, 32},
};
uint8_t flag_sent = 1;
//IMU 
MPU9250 imu;
uint8_t sensorId;
float aX_f, aY_f, aZ_f, aSqrt, gX_f, gY_f, gZ_f, mDirection, mX_f, mY_f, mZ_f;
//declarar "estrtura imu" mais completa posteriormente


void onEvent (ev_t ev) {
    Serial.print(os_getTime());
    Serial.print(": ");
    switch(ev) {
        case EV_SCAN_TIMEOUT:
            Serial.println(F("EV_SCAN_TIMEOUT"));
            break;
        case EV_BEACON_FOUND:
            Serial.println(F("EV_BEACON_FOUND"));
            break;
        case EV_BEACON_MISSED:
            Serial.println(F("EV_BEACON_MISSED"));
            break;
        case EV_BEACON_TRACKED:
            Serial.println(F("EV_BEACON_TRACKED"));
            break;
        case EV_JOINING:
            Serial.println(F("EV_JOINING"));
            break;
        case EV_JOINED:
            Serial.println(F("EV_JOINED"));
            break;
        case EV_RFU1:
            Serial.println(F("EV_RFU1"));
            break;
        case EV_JOIN_FAILED:
            Serial.println(F("EV_JOIN_FAILED"));
            break;
        case EV_REJOIN_FAILED:
            Serial.println(F("EV_REJOIN_FAILED"));
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE (includes waiting for RX windows)"));
            if (LMIC.txrxFlags & TXRX_ACK)
              Serial.println(F("Received ack"));
            if (LMIC.dataLen) {
              Serial.println(F("Received "));
              Serial.println(LMIC.dataLen);
              Serial.println(F(" bytes of payload"));
            }
            // Schedule next transmission
            os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(TX_INTERVAL), do_send);
            break;
        case EV_LOST_TSYNC:
            Serial.println(F("EV_LOST_TSYNC"));
            break;
        case EV_RESET:
            Serial.println(F("EV_RESET"));
            break;
        case EV_RXCOMPLETE:
            // data received in ping slot
            Serial.println(F("EV_RXCOMPLETE"));
            break;
        case EV_LINK_DEAD:
            Serial.println(F("EV_LINK_DEAD"));
            break;
        case EV_LINK_ALIVE:
            Serial.println(F("EV_LINK_ALIVE"));
            break;
         default:
            Serial.println(F("Unknown event"));
            break;
    }
}

void do_send(osjob_t* j){
  //prepara dados do imu para enviar
    int16_t ax;
    uint8_t x_byte[2], *axp = (uint8_t*)&ax;
    char strnumber[3];
    //Serial.print("accelX float: ");
    //Serial.println(aX_f);
    Serial.print("accelX int: ");
    ax = (int16_t)(aX_f);
    Serial.println(ax);
    sprintf(strnumber, "%d", (ax) );
    
    Serial.print("accelX bytes:  ");
    Serial.print(strnumber[0]);
    Serial.print(strnumber[1]);
    Serial.println(strnumber[2]);
    mydata[0] = 'X';
    mydata[1] = ':';
    mydata[2] = strnumber[0];
    mydata[3] = strnumber[1];
    mydata[4] = strnumber[2];
    mydata[5] = 'º';
    
    
    
    // Check if there is not a current TX/RX job running
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, not sending"));
    } else {
        // Prepare upstream data transmission at the next possible time.
        LMIC_setTxData2(1, mydata, sizeof(mydata)-1, 0);
        Serial.println(F("Packet queued"));
       
        //for(int i = 0;i<8;i++)Serial.print(mydata[i]);
    }
    // Next TX is scheduled after TX_COMPLETE event.
}

void float_to_string(double number, char *res, int afterpoint)
{
  // parte inteira em aux
  int32_t aux = (int32_t) number;
  // parte fracionária em aux2
  float aux2 = number - (float) aux;

  // salva a parte inteira do número na string e já coloca o ponto
  sprintf(res, "%d.", aux);

  uint8_t loop;
  for (loop = 0; loop < afterpoint; loop++)
  {
    aux2 = aux2 * 10;
    printf("%f\n", aux2 );
    aux = (int32_t) aux2;
    char strnumber[2];
    sprintf(strnumber, "%d", abs(aux) );
    strcat(res, strnumber);

    aux2 = aux2 - aux;
  }
}
void setup() {
    Serial.begin(115200);
    Serial.println(F("Starting"));
    
    // imu esp32 setup/////
    #ifdef _ESP32_HAL_I2C_H_ // For ESP32
      Wire.begin(SDA_PIN, SCL_PIN); // SDA, SCL
    #else
      Wire.begin();
    #endif
     imu.setWire(&Wire);
     imu.beginAccel();
     imu.beginGyro();
     imu.beginMag();
     sensorId = imu.readId();
    //////////////////////
    #ifdef VCC_ENABLE
    // For Pinoccio Scout boards
    pinMode(VCC_ENABLE, OUTPUT);
    digitalWrite(VCC_ENABLE, HIGH);
    delay(1000);
    #endif

    // LMIC init
    os_init();
    // Reset the MAC state. Session and pending data transfers will be discarded.
    LMIC_reset();

    // Set static session parameters. Instead of dynamically establishing a session
    // by joining the network, precomputed session parameters are be provided.
    #ifdef PROGMEM
    // On AVR, these values are stored in flash and only copied to RAM
    // once. Copy them to a temporary buffer here, LMIC_setSession will
    // copy them into a buffer of its own again.
    uint8_t appskey[sizeof(APPSKEY)];
    uint8_t nwkskey[sizeof(NWKSKEY)];
    memcpy_P(appskey, APPSKEY, sizeof(APPSKEY));
    memcpy_P(nwkskey, NWKSKEY, sizeof(NWKSKEY));
    LMIC_setSession (0x1, DEVADDR, nwkskey, appskey);
    #else
    // If not running an AVR with PROGMEM, just use the arrays directly
    LMIC_setSession (0x1, DEVADDR, NWKSKEY, APPSKEY);
    #endif

   
    #if defined(CFG_us915)
    // NA-US channels 0-71 are configured automatically
    // but only one group of 8 should (a subband) should be active
    // TTN recommends the second sub band, 1 in a zero based count.
    // https://github.com/TheThingsNetwork/gateway-conf/blob/master/US-global_conf.json
    LMIC_selectSubBand(1);
    #endif

    // Disable link check validation
    LMIC_setLinkCheckMode(0);

    // TTN uses SF9 for its RX2 window.
    LMIC.dn2Dr = DR_SF12;

    // Set data rate and transmit power for uplink (note: txpow seems to be ignored by the library)
    LMIC_setDrTxpow(DR_SF12,14);

    // Start job
    do_send(&sendjob);
}

void loop() {
        if (flag_sent)
    {
      do_send(&sendjob);
      //gps_get_coordinates_ublox(&coord); 
    
      
      flag_sent = 0;
    }
     imu.accelUpdate();
    imu.eulerGet();
    aX_f = imu.pitch;
    os_runloop_once();
}
