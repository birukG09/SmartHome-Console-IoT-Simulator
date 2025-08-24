import json
from hub.py.utils import to_json_line, parse_json_line

def test_roundtrip():
    obj = {"action":"telemetry","device_id":"x","payload":{"a":1}}
    line = to_json_line(obj)
    back = parse_json_line(line)
    assert back == obj

def test_command_schema():
    cmd = {"action":"command","target":"all","name":"ping"}
    line = to_json_line(cmd)
    back = parse_json_line(line)
    assert back["action"] == "command"
    assert "target" in back
