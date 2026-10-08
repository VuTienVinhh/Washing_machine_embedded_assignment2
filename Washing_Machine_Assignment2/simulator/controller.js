(function (root) {
  'use strict';
  const CYCLE_MS = 1800000;
  const elapsed = (now, then) => (now - then) >>> 0;
  class Controller {
    constructor() { this.reset(0); }
    reset(now) {
      this.state = 'STANDBY'; this.credit = 0; this.stops = 0;
      this.started = now >>> 0; this.entered = now >>> 0;
    }
    active() { return this.state === 'RUNNING' || this.state === 'PAUSED'; }
    enter(state, now) { this.state = state; this.entered = now >>> 0; }
    finish(now) { this.credit = 0; this.stops = 0; this.enter('STANDBY', now); }
    step(now, input = {}) {
      now >>>= 0;
      if (input.fault) {
        if (this.state !== 'ERROR') {
          this.credit = 0; this.stops = 0; this.enter('ERROR', now);
        }
        return;
      }
      if (this.state === 'ERROR') return;
      if (this.active() && elapsed(now, this.started) >= CYCLE_MS) {
        this.finish(now); return;
      }
      if (this.state === 'STANDBY' || this.state === 'READY') {
        const coins = input.coins || 0;
        const add = ((coins & 1) ? 10 : 0) + ((coins & 2) ? 20 : 0)
                  + ((coins & 4) ? 50 : 0);
        this.credit = Math.min(65535, this.credit + add);
        if (this.credit >= 50 && this.state === 'STANDBY') this.enter('READY', now);
        if (this.state === 'READY' && input.run) {
          this.credit = 0; this.stops = 0; this.started = now;
          this.enter('RUNNING', now);
        }
        return;
      }
      if (input.stop) {
        this.stops += 1;
        if (this.stops >= 2) this.finish(now);
        return;
      }
      if (input.pause && this.state === 'RUNNING') this.enter('PAUSED', now);
      else if (input.run && this.state === 'PAUSED') this.enter('RUNNING', now);
    }
    snapshot(now) {
      const blink = Math.floor(elapsed(now, this.entered) / 500) % 2 === 0;
      const outputs = {
        STANDBY: [true, false, false], READY: [true, true, false],
        RUNNING: [false, blink, true], PAUSED: [false, true, false],
        ERROR: [blink, false, false]
      }[this.state];
      return {
        state: this.state, credit: this.credit,
        remaining: this.active() ? Math.max(0, CYCLE_MS - elapsed(now, this.started)) : 0,
        stops: this.stops, red: outputs[0], blue: outputs[1], wash: outputs[2]
      };
    }
    event(now, action, value = 0) {
      if (action === 'RESET') { this.reset(now); return this.snapshot(now); }
      const inpt = {};
      if (action === 'COIN') inpt.coins = ({10: 1, 20: 2, 50: 4})[value] || 0;
      else if (action === 'RUN') inpt.run = true;
      else if (action === 'PAUSE') inpt.pause = true;
      else if (action === 'STOP') inpt.stop = true;
      else if (action === 'FAULT') inpt.fault = Boolean(value);
      else if (action === 'BOTH') {
        inpt.run = Boolean(value & 1); inpt.pause = Boolean(value & 2);
        inpt.stop = Boolean(value & 4); inpt.fault = Boolean(value & 8);
      }
      this.step(now, inpt);
      return this.snapshot(now);
    }
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {Controller, CYCLE_MS};
  else root.Washing = {Controller, CYCLE_MS};
})(typeof globalThis !== 'undefined' ? globalThis : this);
