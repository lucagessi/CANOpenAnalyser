#include <Arduino.h>
#include <SPI.h>
#include <mcp2515.h>
#include <PacketSerial.h>

//#include <Arduino_FreeRTOS.h>

#define COBID_TO_U16(cid)  ( ((cid & 0x0000ff00)>>8) + ((cid & 0x000000ff)<<8) )

struct can_frame canMsg;
MCP2515 mcp2515(10);

PacketSerial CanSerial;

#define BASIC_CAN_PKT_LEN 8
#define BASIC_COBS_PKT_LEN 24
// https://wiki.wireshark.org/Development/LibpcapFileFormat
typedef struct {
	uint32_t seconds;
	uint32_t micro_seconds;
  uint32_t incl_len;      // BASIC_CAN_PKT_LEN + can_packet_t.length
  uint32_t orig_len;      // BASIC_CAN_PKT_LEN + can_packet_t.length
  uint16_t flags = 0;
	uint16_t cob_id;
  uint8_t length;
  uint8_t reserved[3];
  uint8_t data[8];
}can_packet_t;

uint8_t CanPacket[20];
can_packet_t pkt;

uint32_t us = 0,ms_total = 0;
uint32_t s = 0;
uint32_t us_start;
byte index = 0;
const byte max_index = 2;
uint16_t can_ids[3] = { 0x0080, 0x0481, 0x381 };
uint8_t lengths[3] = {0, 1 , 3 };
uint8_t data[3][4] = { {},{1},{1,2,3} };

void setup() {
  Serial.begin(115200);
  CanSerial.begin(115200);
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS,MCP_8MHZ);
  mcp2515.setNormalMode();

}
const uint8_t en_debug = 0;
const uint8_t en_simula = 0;

void simula(){
  delay(10);
  ms_total = millis();
  uint32_t div = ms_total / 1000;
  s = 0;
  us = (ms_total % 1000) * 1000;
  pkt.cob_id = COBID_TO_U16(can_ids[index]);
  pkt.micro_seconds = us;
  pkt.seconds = s;
  pkt.length = lengths[index];
  pkt.incl_len = pkt.orig_len = pkt.length + BASIC_CAN_PKT_LEN;
  memcpy(pkt.data, data[index], pkt.length);
  if (en_debug){
    Serial.println( pkt.micro_seconds );
    Serial.println( pkt.seconds );
  }else{
    CanSerial.send((const uint8_t *)&pkt, pkt.length + BASIC_COBS_PKT_LEN); 
  }
  index++;
  index = index > max_index ? 0 : index; 
}

void can_analyse(){

  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    ms_total = millis();
    uint32_t div = ms_total / 1000;
    s = 0;
    us = (ms_total % 1000) * 1000;
    pkt.cob_id = COBID_TO_U16(canMsg.can_id);
    pkt.micro_seconds = us;
    pkt.seconds = s;
    pkt.length = canMsg.can_dlc;
    pkt.incl_len = pkt.orig_len = pkt.length + BASIC_CAN_PKT_LEN;
    memcpy(pkt.data, canMsg.data, pkt.length);
    if (en_debug){
      Serial.println( pkt.micro_seconds );
      Serial.println( pkt.seconds );
    }else{
      CanSerial.send((const uint8_t *)&pkt, pkt.length + BASIC_COBS_PKT_LEN); 
    }
  }
}

void loop() {
    if (en_simula){
      simula();
    }else{
      can_analyse();
    }
}