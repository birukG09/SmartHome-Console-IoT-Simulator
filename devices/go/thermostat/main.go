package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net"
	"os"
	"strings"
	"time"
)

type Message map[string]interface{}

func toJSONLine(m Message) []byte {
	b, _ := json.Marshal(m)
	return append(b, '\n')
}

func readLineJSON(r *bufio.Reader) (Message, error) {
	line, err := r.ReadString('\n')
	if err != nil {
		return nil, err
	}
	var m Message
	err = json.Unmarshal([]byte(strings.TrimSpace(line)), &m)
	return m, err
}

func main() {
	host := "127.0.0.1:5051"
	if len(os.Args) > 1 {
		host = os.Args[1]
	}
	conn, err := net.Dial("tcp", host)
	if err != nil {
		fmt.Println("connect error:", err)
		return
	}
	defer conn.Close()

	id := "go-thermo-1"
	devType := "thermostat"
	hello := Message{"action": "hello", "role": "device", "device_id": id, "device_type": devType, "capabilities": []string{"temp","setpoint"}}
	conn.Write(toJSONLine(hello))
	reader := bufio.NewReader(conn)

	// read ack
	reader.ReadString('\n')

	setpoint := 22.0
	temp := 21.0
	lastSend := time.Now()

	// Listen for commands
	go func() {
		for {
			msg, err := readLineJSON(reader)
			if err != nil {
				return
			}
			if act, ok := msg["action"].(string); ok && act == "command" {
				target, _ := msg["target"].(string)
				if target == "all" || target == id {
					if name, ok := msg["name"].(string); ok && name == "set_temp" {
						if params, ok := msg["params"].(map[string]interface{}); ok {
							if v, ok := params["value"].(float64); ok {
								setpoint = v
								fmt.Println("[thermostat] setpoint changed ->", setpoint)
							}
						}
					}
				}
			}
		}
	}()

	rand.Seed(time.Now().UnixNano())
	for {
		time.Sleep(500 * time.Millisecond)
		// approach setpoint with some noise
		diff := setpoint - temp
		temp += diff*0.1 + (rand.Float64()-0.5)*0.05
		temp = math.Round(temp*10) / 10

        if time.Since(lastSend) > 3*time.Second {
			payload := Message{"temp": temp, "setpoint": setpoint, "unit": "C"}
			tel := Message{"action":"telemetry","device_id": id, "payload": payload}
			conn.Write(toJSONLine(tel))
			lastSend = time.Now()
		}
	}
}
