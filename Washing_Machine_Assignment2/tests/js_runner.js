const fs = require('fs');
const {Controller} = require('../simulator/controller.js');
const m = new Controller();
for (const line of fs.readFileSync(0, 'utf8').trim().split(/\r?\n/)) {
  if (!line.trim()) continue;
  const [now, action, value] = line.trim().split(/\s+/);
  console.log(JSON.stringify(m.event(Number(now) >>> 0, action, Number(value))));
}
