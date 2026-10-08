#ifndef TEST_ARDUINO_H
#define TEST_ARDUINO_H
// Host-only Arduino shim. This file is never copied into the sketch directory.
#include <stdint.h>
#include <string>
const uint8_t LOW = 0, HIGH = 1, INPUT_PULLUP = 2, OUTPUT = 3, A0 = 14;
#define F(x) x
extern uint32_t mockNow;
extern uint8_t levels[20], modes[20], written[20];
inline unsigned long millis() { return mockNow; }
inline void pinMode(uint8_t pin, uint8_t mode) { modes[pin] = mode; }
inline int digitalRead(uint8_t pin) { return levels[pin]; }
inline void digitalWrite(uint8_t pin, uint8_t value) { written[pin] = value; }
class SerialShim {
public:
    std::string queue;
    void begin(unsigned long) {}
    int available() { return int(queue.size()); }
    char read() { char c=queue[0]; queue.erase(0,1); return c; }
    template<class T> void print(const T&) {}
    template<class T> void println(const T&) {}
};
extern SerialShim Serial;
#endif
