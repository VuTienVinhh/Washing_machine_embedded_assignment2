#include <cstdlib>
#include <iostream>
#include "../firmware/washing_controller/controller.h"

void check(bool ok, const char* message) {
    if (!ok) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}

int main() {
    DebouncedButton b;
    b.begin(false, 0);
    check(!b.update(true, 10), "first edge waits for debounce");
    check(!b.update(false, 15), "bounce does not count");
    check(!b.update(true, 20), "second edge waits");
    check(!b.update(true, 49), "29 ms is too short");
    check(b.update(true, 50), "stable 30 ms press counts once");
    check(!b.update(true, 100), "held press does not repeat");
    check(!b.update(true, 10000), "long hold does not repeat");
    check(!b.update(false, 10010), "release begins debounce");
    check(!b.update(false, 10040), "release gives no press");
    check(!b.update(true, 10050), "new press begins debounce");
    check(b.update(true, 10080), "new press counts after release");
    b.begin(false, 0xFFFFFFF0u);
    check(!b.update(true, 0xFFFFFFF5u), "rollover edge begins");
    check(b.update(true, 19), "debounce also works across rollover");
    std::cout << "PASS: 13 debounce checks (bounce, hold, release, rollover)\n";
}
