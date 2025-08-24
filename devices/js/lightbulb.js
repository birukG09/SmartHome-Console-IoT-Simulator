const net = require('net');

const HOST = '127.0.0.1';
const PORT = 5051;
const id = 'js-light-1';
const type = 'lightbulb';

let state = { on: false, brightness: 50 };

function send(conn, obj) {
  conn.write(JSON.stringify(obj) + '\n');
}

const conn = net.createConnection({host: HOST, port: PORT}, () => {
  send(conn, {action:'hello', role:'device', device_id:id, device_type:type, capabilities:['on','brightness']});
});

let buf = '';
conn.on('data', (chunk) => {
  buf += chunk.toString('utf8');
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx);
    buf = buf.slice(idx+1);
    try {
      const msg = JSON.parse(line);
      if (msg.action === 'command' && (msg.target === 'all' || msg.target === id)) {
        if (msg.name === 'toggle') state.on = !state.on;
        if (msg.name === 'set_brightness' && msg.params && typeof msg.params.value === 'number') {
          state.brightness = Math.max(0, Math.min(100, Math.floor(msg.params.value)));
        }
        // Send confirmation telemetry
        send(conn, {action:'telemetry', device_id:id, payload: state});
      }
    } catch (e) {
      // ignore
    }
  }
});

setInterval(() => {
  send(conn, {action:'telemetry', device_id:id, payload: state});
}, 2500);
