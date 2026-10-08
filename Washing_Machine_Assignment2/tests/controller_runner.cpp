#include <iostream>
#include <sstream>
#include <string>
#include "../firmware/washing_controller/controller.h"

// Trace protocol: now_ms action value. Actions: RESET, COIN, RUN, PAUSE,
// STOP, FAULT, TICK, BOTH. BOTH value: RUN=1, PAUSE=2, STOP=4, FAULT=8.
int main() {
    Controller m;
    uint64_t wideNow;
    std::string action;
    unsigned value;
    while (std::cin >> wideNow >> action >> value) {
        uint32_t now = uint32_t(wideNow);
        Inputs in;
        if (action == "RESET") m.reset(now);
        else {
            if (action == "COIN") in.coins = coinBit(value);
            else if (action == "RUN") in.run = true;
            else if (action == "PAUSE") in.pause = true;
            else if (action == "STOP") in.stop = true;
            else if (action == "FAULT") in.fault = value != 0;
            else if (action == "BOTH") {
                in.run = value & 1; in.pause = value & 2;
                in.stop = value & 4; in.fault = value & 8;
            }
            m.step(now, in);
        }
        Outputs o = m.outputs(now);
        std::cout << "{\"state\":\"" << stateName(m.state())
                  << "\",\"credit\":" << m.credit()
                  << ",\"remaining\":" << m.remaining(now)
                  << ",\"stops\":" << unsigned(m.stops())
                  << ",\"red\":" << (o.red ? "true" : "false")
                  << ",\"blue\":" << (o.blue ? "true" : "false")
                  << ",\"wash\":" << (o.wash ? "true" : "false") << "}\n";
    }
}
