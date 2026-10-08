#include <Arduino.h>
#include "controller.h"

// Inputs are active LOW. Each switch connects its pin to GND.
const uint8_t STOP_PIN = 2;
const uint8_t RUN_PIN = 3;
const uint8_t PAUSE_PIN = 4;
const uint8_t COIN10_PIN = 5;
const uint8_t COIN20_PIN = 6;
const uint8_t COIN50_PIN = 7;
const uint8_t RLED_PIN = 8;
const uint8_t BLED_PIN = 9;
const uint8_t WASH_ENABLE_PIN = 10; // logic output for a driver, not a motor supply
const uint8_t FAULT_PIN = A0;      // optional fault switch, LOW means fault

const uint8_t inputPins[] = {STOP_PIN, RUN_PIN, PAUSE_PIN,
                           COIN10_PIN, COIN20_PIN, COIN50_PIN};
DebouncedButton buttons[6];
Controller machine;
State printedState = State::Error;
uint16_t printedCredit = 65535;
uint8_t printedStops = 255;
uint32_t lastLog = 0;

void setup() {
    Serial.begin(115200);
    uint32_t now = millis();
    for (uint8_t i = 0; i < 6; ++i) {
        pinMode(inputPins[i], INPUT_PULLUP);
        buttons[i].begin(digitalRead(inputPins[i]) == LOW, now);
    }
    pinMode(FAULT_PIN, INPUT_PULLUP);
    pinMode(RLED_PIN, OUTPUT);
    pinMode(BLED_PIN, OUTPUT);
    pinMode(WASH_ENABLE_PIN, OUTPUT);
    machine.reset(now);
    Serial.println(F("Washing controller. Coins: 1=10c, 2=20c, 5=50c."));
    Serial.println(F("Controls: r=RUN, p=PAUSE, s=STOP. Hardware reset clears ERROR."));
}

void loop() {
    uint32_t now = millis();
    Inputs in;
    in.stop = buttons[0].update(digitalRead(STOP_PIN) == LOW, now);
    in.run = buttons[1].update(digitalRead(RUN_PIN) == LOW, now);
    in.pause = buttons[2].update(digitalRead(PAUSE_PIN) == LOW, now);
    if (buttons[3].update(digitalRead(COIN10_PIN) == LOW, now)) in.coins |= 1;
    if (buttons[4].update(digitalRead(COIN20_PIN) == LOW, now)) in.coins |= 2;
    if (buttons[5].update(digitalRead(COIN50_PIN) == LOW, now)) in.coins |= 4;
    in.fault = digitalRead(FAULT_PIN) == LOW;

    // Serial and the three coin switches emulate a validated coin acceptor.
    if (Serial.available() > 0) {
        char c = Serial.read();
        if (c == '1') in.coins |= 1;
        else if (c == '2') in.coins |= 2;
        else if (c == '5') in.coins |= 4;
        else if (c == 'r' || c == 'R') in.run = true;
        else if (c == 'p' || c == 'P') in.pause = true;
        else if (c == 's' || c == 'S') in.stop = true;
    }

    machine.step(now, in);
    Outputs out = machine.outputs(now);
    digitalWrite(RLED_PIN, out.red ? HIGH : LOW);
    digitalWrite(BLED_PIN, out.blue ? HIGH : LOW);
    digitalWrite(WASH_ENABLE_PIN, out.wash ? HIGH : LOW);

    if (machine.state() != printedState || machine.credit() != printedCredit ||
        machine.stops() != printedStops || uint32_t(now - lastLog) >= 1000) {
        printedState = machine.state();
        printedCredit = machine.credit();
        printedStops = machine.stops();
        lastLog = now;
        Serial.print(stateName(machine.state()));
        Serial.print(F(" credit=")); Serial.print(machine.credit());
        Serial.print(F(" remaining_ms=")); Serial.print(machine.remaining(now));
        Serial.print(F(" stop_count=")); Serial.println(machine.stops());
    }
    // No delay(): inputs, timer and LEDs are updated on every pass.
}
