use axum::{
    extract::{
        ws::{Message, WebSocket, WebSocketUpgrade},
        State,
    },
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, net::SocketAddr, sync::Arc};
use tokio::sync::{broadcast, Mutex};
use tower_http::cors::{Any, CorsLayer};
use tokio::io::{AsyncBufReadExt, BufReader};
use std::process::Stdio;

type LogChannel = broadcast::Sender<String>;

#[derive(Clone)]
struct AppState {
    tx: LogChannel,
    is_running: Arc<Mutex<bool>>,
    module_pids: Arc<Mutex<HashMap<String, u32>>>,
}

#[derive(Deserialize)]
struct InjectRequest {
    target: String,
    device_id: String,
    modules: Vec<String>,
}

#[derive(Serialize, Deserialize, Clone)]
struct Device {
    id: String,
    name: String,
    device_type: String,
}

#[derive(Serialize)]
struct StatusResponse {
    status: String,
    message: String,
}

const PROJECT_ROOT: &str = "/Users/kadirarici/Desktop/Biometric Logic Bypass/Sentinel_Hook";

#[tokio::main]
async fn main() {
    let (tx, _rx) = broadcast::channel(512);
    let state = AppState {
        tx,
        is_running: Arc::new(Mutex::new(false)),
        module_pids: Arc::new(Mutex::new(HashMap::new())),
    };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/api/ping", get(|| async { "pong" }))
        .route("/api/devices", get(list_devices))
        .route("/api/inject", post(handle_inject))
        .route("/api/stop", post(handle_stop))
        .route("/ws", get(ws_handler))
        .layer(cors)
        .with_state(state);

    let addr = SocketAddr::from(([127, 0, 0, 1], 8000));
    println!("🚀 Sentinel Tactical Backend [Diagnostic Mode] on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn list_devices() -> impl IntoResponse {
    let python_bin = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3";
    let helper_script = format!("{}/list_devices.py", PROJECT_ROOT);
    
    let output = match tokio::process::Command::new(python_bin)
        .arg(&helper_script)
        .output().await {
        Ok(o) => o,
        Err(_) => return (StatusCode::INTERNAL_SERVER_ERROR, Json(Vec::<Device>::new())).into_response(),
    };

    let stdout = String::from_utf8_lossy(&output.stdout);
    let devices: Vec<Device> = match serde_json::from_str(&stdout) {
        Ok(d) => d,
        Err(_) => Vec::new(),
    };

    (StatusCode::OK, Json(devices)).into_response()
}

async fn handle_inject(
    State(state): State<AppState>,
    Json(payload): Json<InjectRequest>,
) -> impl IntoResponse {
    let tx = state.tx.clone();
    let module_pids = state.module_pids.clone();
    
    let target = payload.target.clone();
    let device_id = payload.device_id.clone();
    let module_name = payload.modules.first().cloned().unwrap_or_else(|| "all".to_string());

    // TOGGLE LOGIC: Scope the lock to drop it before spawn
    {
        let mut pids = module_pids.lock().await;
        if let Some(&pid) = pids.get(&module_name) {
            let _ = tx.send(format!("[PURGE] SIGNAL ACQUIRED: Detaching hook '{}' (PID: {})", module_name, pid));
            let _ = tokio::process::Command::new("kill").arg("-9").arg(pid.to_string()).output().await;
            pids.remove(&module_name);
            return (
                StatusCode::OK,
                Json(StatusResponse {
                    status: "detached".to_string(),
                    message: format!("Module {} detached.", module_name),
                }),
            ).into_response();
        }
    }

    // NEW INJECTION
    tokio::spawn(async move {
        // 0. Pre-check if Target is running
        let python_bin = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3";
        let process_script = format!("{}/list_processes.py", PROJECT_ROOT);
        
        let ps_output = tokio::process::Command::new(python_bin)
            .arg(&process_script)
            .arg(&device_id)
            .output().await;

        if let Ok(o) = ps_output {
            let stdout = String::from_utf8_lossy(&o.stdout);
            if !stdout.contains(&target) {
                let _ = tx.send(format!("[!] ERROR: Target '{}' is not running on this device. Please open the app first.", target));
                return;
            }
        }

        let _ = tx.send(format!("[INIT] Operasyon hazırlığı: '{}'...", module_name));

        let bundler_script = format!("{}/inject_hooks.py", PROJECT_ROOT);
        let frida_bin = "/Library/Frameworks/Python.framework/Versions/3.12/bin/frida";
        let bundle_js = format!("{}/_sentinel_bundle.js", PROJECT_ROOT);

        // 1. Run Bundler
        let _ = tokio::process::Command::new(python_bin)
            .arg(&bundler_script)
            .arg(&module_name)
            .output()
            .await;

        // 2. Run Frida with No-Pause and Quiet Mode
        let mut cmd = tokio::process::Command::new(frida_bin);
        cmd.current_dir(PROJECT_ROOT);
        
        let args = if device_id == "local" {
            vec!["-q", "-t", "inf", "-l", &bundle_js, "-n", &target]
        } else {
            vec!["-D", &device_id, "-q", "-t", "inf", "-l", &bundle_js, "-n", &target]
        };
        cmd.args(args);

        cmd.stdout(Stdio::piped()).stderr(Stdio::piped()).stdin(Stdio::piped());

        let mut child = match cmd.spawn() {
            Ok(c) => c,
            Err(e) => {
                let _ = tx.send(format!("[!] CRITICAL ERROR: {e}"));
                return;
            }
        };

        let mut child_stdin = child.stdin.take().unwrap();
        let tx_heartbeat = tx.clone();
        let m_name = module_name.clone();
        
        // STDIN HEARTBEAT: Frida'yı uyutmamak için gecikmeli başlat
        tokio::spawn(async move {
            use tokio::io::AsyncWriteExt;
            // Frida'nın scripti yüklemesi için 3 saniye bekle
            tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;
            
            while let Ok(_) = child_stdin.write_all(b"\n").await {
                let _ = tokio::io::AsyncWriteExt::flush(&mut child_stdin).await;
                tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
            }
            let _ = tx_heartbeat.send(format!("[SYSTEM] Tactical signal lost for '{}'.", m_name));
        });

        if let Some(pid) = child.id() {
            module_pids.lock().await.insert(module_name.clone(), pid);
            let _ = tx.send(format!("[OK] Modül '{}' aktif edildi. (PID: {})", module_name, pid));
        }

        let stdout = child.stdout.take().unwrap();
        let stderr = child.stderr.take().unwrap();

        // Async STDOUT Reader
        let tx_out = tx.clone();
        tokio::spawn(async move {
            let mut reader = BufReader::new(stdout).lines();
            while let Ok(Some(line)) = reader.next_line().await {
                let _ = tx_out.send(line);
            }
        });

        // Async STDERR Reader (Gerçek Zamanlı Hata Yakalama)
        let tx_err = tx.clone();
        tokio::spawn(async move {
            let mut reader = BufReader::new(stderr).lines();
            while let Ok(Some(line)) = reader.next_line().await {
                let _ = tx_err.send(format!("[!] ERROR: {line}"));
            }
        });

        let status = child.wait().await;
        let _ = tx.send(format!("[SYSTEM] Modül '{}' oturumu kapandı. (Exit: {:?})", module_name, status));
        module_pids.lock().await.remove(&module_name);
    });

    (
        StatusCode::OK,
        Json(StatusResponse {
            status: "success".to_string(),
            message: "Tactical session initiated.".to_string(),
        }),
    ).into_response()
}

async fn handle_stop(State(state): State<AppState>) -> impl IntoResponse {
    let mut pids = state.module_pids.lock().await;
    for (&ref name, &pid) in pids.iter() {
        let _ = tokio::process::Command::new("kill").arg("-9").arg(pid.to_string()).output().await;
    }
    pids.clear();
    let _ = tokio::process::Command::new("pkill").arg("-f").arg("frida").output().await;
    let _ = state.tx.send("[SYSTEM] NUCLEAR PURGE: All hooks detached.".to_string());

    (
        StatusCode::OK,
        Json(StatusResponse { status: "success".to_string(), message: "All sessions purged.".to_string() }),
    )
}

async fn ws_handler(ws: WebSocketUpgrade, State(state): State<AppState>) -> Response {
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

async fn handle_socket(mut socket: WebSocket, state: AppState) {
    let mut rx = state.tx.subscribe();
    let _ = socket.send(Message::Text(":: SENTINEL PROTOCOL [v8.0] ONLINE ::".into())).await;
    while let Ok(msg) = rx.recv().await {
        if socket.send(Message::Text(msg.into())).await.is_err() { break; }
    }
}
