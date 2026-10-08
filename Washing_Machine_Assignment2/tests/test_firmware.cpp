#include <cstdlib>
#include <iostream>
#include "Arduino.h"
uint32_t mockNow = 0;
uint8_t levels[20], modes[20], written[20];
SerialShim Serial;
#include "../firmware/washing_controller/washing_controller.ino"

unsigned checks = 0;
void require(bool ok, const char* message) {
    ++checks;
    if (!ok) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}
void tick(uint32_t delta) { mockNow += delta; loop(); }
void press(uint8_t pin) {
    levels[pin]=LOW; tick(1); tick(30);
    levels[pin]=HIGH; tick(1); tick(30);
}
void benchReset() {
    for (uint8_t i=0;i<20;++i) levels[i]=HIGH;
    mockNow=0; Serial.queue.clear(); setup(); loop();
}

int main() {
    benchReset();
    require(modes[STOP_PIN] == INPUT_PULLUP && modes[RUN_PIN] == INPUT_PULLUP && modes[PAUSE_PIN] == INPUT_PULLUP, "controls use pullups");
    require(written[RLED_PIN] == HIGH && written[BLED_PIN] == LOW && written[WASH_ENABLE_PIN] == LOW, "standby GPIO outputs");
    press(COIN50_PIN);
    require(machine.state() == State::Ready && machine.credit() == 50 && written[BLED_PIN] == HIGH, "coin input reaches READY");
    press(RUN_PIN);
    require(machine.state() == State::Running && machine.credit() == 0 && written[WASH_ENABLE_PIN] == HIGH, "RUN clears credit and enables wash");
    uint32_t cycleStart=machine.started();
    levels[STOP_PIN]=LOW; tick(1); tick(30);
    require(machine.stops() == 1 && machine.state() == State::Running, "first STOP only arms stop");
    tick(10000);
    require(machine.stops() == 1 && machine.state() == State::Running, "holding STOP cannot force stop");
    levels[STOP_PIN]=HIGH; tick(1); tick(30);
    press(PAUSE_PIN);
    require(machine.state() == State::Paused && written[WASH_ENABLE_PIN] == LOW && written[BLED_PIN] == HIGH, "PAUSE GPIO outputs");
    tick(60000);
    require(machine.remaining(mockNow) == Controller::CycleMs - uint32_t(mockNow-cycleStart), "paused timer keeps counting");
    press(RUN_PIN);
    require(machine.state() == State::Running && machine.started() == cycleStart, "resume does not restart timer");
    press(STOP_PIN);
    require(machine.state() == State::Standby && written[WASH_ENABLE_PIN] == LOW, "second STOP ends cycle");
    benchReset();
    Serial.queue="5r"; loop();
    require(machine.state() == State::Ready, "serial coin emulator");
    loop(); require(machine.state() == State::Running, "serial RUN emulator");
    levels[FAULT_PIN]=LOW; tick(1);
    require(machine.state() == State::Error && written[WASH_ENABLE_PIN] == LOW && written[BLED_PIN] == LOW, "fault cuts wash output");
    levels[FAULT_PIN]=HIGH; tick(500);
    require(machine.state() == State::Error && written[RLED_PIN] == LOW, "fault latch and blink");
    benchReset(); Serial.queue="5rp"; loop(); loop(); loop();
    mockNow=1800000; loop();
    require(machine.state() == State::Standby && written[RLED_PIN] == HIGH, "paused firmware timeout");
    std::cout << "PASS: " << checks << " firmware adapter checks using mocked Arduino IO\n";
}
