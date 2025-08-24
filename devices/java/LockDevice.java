import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class LockDevice {
    static class Msg {
        static String json(Map<String, Object> m) {
            try {
                return new com.google.gson.Gson().toJson(m) + "\n";
            } catch (Throwable t) {
                // Fallback minimal JSON (no external deps needed)
                StringBuilder sb = new StringBuilder();
                sb.append("{");
                int i = 0;
                for (Map.Entry<String, Object> e : m.entrySet()) {
                    if (i++ > 0) sb.append(",");
                    sb.append("\"").append(e.getKey()).append("\":");
                    Object v = e.getValue();
                    if (v instanceof Number || v instanceof Boolean) sb.append(v.toString());
                    else sb.append("\"").append(v.toString().replace("\"","\\\"")).append("\"");
                }
                sb.append("}\n");
                return sb.toString();
            }
        }
    }

    public static void main(String[] args) throws Exception {
        String host = "127.0.0.1";
        int port = 5051;
        if (args.length >= 1) host = args[0];
        String id = "java-lock-1";
        String type = "door-lock";
        Socket sock = new Socket(host, port);
        InputStream in = sock.getInputStream();
        OutputStream out = sock.getOutputStream();
        BufferedReader br = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));
        // hello
        Map<String, Object> hello = new LinkedHashMap<>();
        hello.put("action","hello");
        hello.put("role","device");
        hello.put("device_id", id);
        hello.put("device_type", type);
        hello.put("capabilities", Arrays.asList("lock","unlock","state"));
        out.write(Msg.json(hello).getBytes(StandardCharsets.UTF_8));
        out.flush();
        // skip ack
        br.readLine();

        final Map<String,Object> state = new HashMap<>();
        state.put("locked", true);
        state.put("battery", 98);

        // Telemetry heartbeat
        Thread heart = new Thread(() -> {
            try {
                while (true) {
                    Thread.sleep(3000);
                    Map<String,Object> tel = new LinkedHashMap<>();
                    tel.put("action","telemetry");
                    tel.put("device_id", id);
                    tel.put("payload", new LinkedHashMap<>(state));
                    out.write(Msg.json(tel).getBytes(StandardCharsets.UTF_8));
                    out.flush();
                }
            } catch (Exception e) { /* exit */ }
        });
        heart.setDaemon(true);
        heart.start();

        // Command listener
        String line;
        while ((line = br.readLine()) != null) {
            try {
                if (!line.trim().startsWith("{")) continue;
                if (line.contains("\"action\":\"command\"") && (line.contains("\"target\":\"all\"") || line.contains("\"target\":\""+id+"\""))) {
                    if (line.contains("\"name\":\"lock\"")) state.put("locked", true);
                    if (line.contains("\"name\":\"unlock\"")) state.put("locked", false);
                }
            } catch (Exception ignored) {}
        }
        sock.close();
    }
}
