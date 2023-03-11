#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

use tauri::api::process::Command;

fn main() {
  Command::new_sidecar("server")
  .expect("failed to create `server` binary command")
  .spawn()
  .expect("Failed to spawn sidecar");
  tauri::Builder::default()
  .run(tauri::generate_context!())
  .expect("error while running tauri application");
}

