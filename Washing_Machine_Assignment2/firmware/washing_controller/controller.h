#ifndef WASHING_CONTROLLER_H
#define WASHING_CONTROLLER_H

#include <stdint.h>

// No Arduino calls here. The same logic runs in the sketch and in host tests.
enum class State : uint8_t { Standby, Ready, Running, Paused, Error };

struct Inputs {
    bool run = false;
    bool pause = false;
    bool stop = false;
    bool fault = false;
    uint8_t coins = 0; // bit 0: 10 cents, bit 1: 20 cents, bit 2: 50 cents
};

struct Outputs {
    bool red;
    bool blue;
    bool wash;
};

inline uint8_t coinBit(unsigned cents) {
    return cents == 10 ? 1 : cents == 20 ? 2 : cents == 50 ? 4 : 0;
}

inline const char* stateName(State state) {
    switch (state) {
        case State::Standby: return "STANDBY";
        case State::Ready: return "READY";
        case State::Running: return "RUNNING";
        case State::Paused: return "PAUSED";
        case State::Error: return "ERROR";
    }
    return "UNKNOWN";
}

class Controller {
public:
    static const uint32_t CycleMs = 30UL * 60UL * 1000UL;
    static const uint32_t BlinkHalfMs = 500;

    Controller() { reset(0); }

    // A bench reset models the board reset button. It is not a fourth control.
    void reset(uint32_t now) {
        state_ = State::Standby;
        credit_ = 0;
        stop_count_ = 0;
        started_ = now;
        entered_ = now;
    }

    void step(uint32_t now, const Inputs& in = Inputs()) {
        // Priority: fault, timeout, STOP, PAUSE, RUN.
        if (in.fault) {
            if (state_ != State::Error) {
                credit_ = 0;
                stop_count_ = 0;
                enter(State::Error, now);
            }
            return;
        }
        if (state_ == State::Error) return; // error stays latched until reset

        if (active() && uint32_t(now - started_) >= CycleMs) {
            finish(now);
            return; // do not use inputs sampled at the expired cycle boundary
        }

        if (state_ == State::Standby || state_ == State::Ready) {
            unsigned add = ((in.coins & 1) ? 10 : 0)
                         + ((in.coins & 2) ? 20 : 0)
                         + ((in.coins & 4) ? 50 : 0);
            uint32_t sum = uint32_t(credit_) + add;
            credit_ = sum > 65535 ? 65535 : uint16_t(sum);
            if (credit_ >= 50 && state_ == State::Standby)
                enter(State::Ready, now);
            if (state_ == State::Ready && in.run) {
                credit_ = 0; // surplus is discarded, with no refund
                stop_count_ = 0;
                started_ = now;
                enter(State::Running, now);
            }
            return;
        }

        if (in.stop) {
            ++stop_count_;
            if (stop_count_ >= 2) finish(now);
            return;
        }
        if (in.pause && state_ == State::Running) {
            enter(State::Paused, now);
        } else if (in.run && state_ == State::Paused) {
            // Keep started_: a pause never gives extra cycle time.
            enter(State::Running, now);
        }
    }

    Outputs outputs(uint32_t now) const {
        bool blink = (uint32_t(now - entered_) / BlinkHalfMs) % 2 == 0;
        switch (state_) {
            case State::Standby: return {true, false, false};
            case State::Ready:   return {true, true, false};
            case State::Running: return {false, blink, true};
            case State::Paused:  return {false, true, false};
            case State::Error:   return {blink, false, false};
        }
        return {false, false, false};
    }

    State state() const { return state_; }
    uint16_t credit() const { return credit_; }
    uint8_t stops() const { return stop_count_; }
    uint32_t started() const { return started_; }
    bool active() const { return state_ == State::Running || state_ == State::Paused; }

    uint32_t remaining(uint32_t now) const {
        if (!active()) return 0;
        uint32_t elapsed = uint32_t(now - started_);
        return elapsed >= CycleMs ? 0 : CycleMs - elapsed;
    }

private:
    State state_;
    uint16_t credit_;
    uint8_t stop_count_;
    uint32_t started_;
    uint32_t entered_;

    void enter(State next, uint32_t now) { state_ = next; entered_ = now; }
    void finish(uint32_t now) {
        credit_ = 0;
        stop_count_ = 0;
        enter(State::Standby, now);
    }
};

// One event per debounced press. Holding a button cannot count twice.
class DebouncedButton {
public:
    void begin(bool pressed, uint32_t now) {
        raw_ = stable_ = pressed;
        changed_ = now;
    }

    bool update(bool pressed, uint32_t now) {
        if (pressed != raw_) { raw_ = pressed; changed_ = now; }
        if (raw_ != stable_ && uint32_t(now - changed_) >= 30) {
            stable_ = raw_;
            return stable_;
        }
        return false;
    }

private:
    bool raw_ = false;
    bool stable_ = false;
    uint32_t changed_ = 0;
};

#endif
