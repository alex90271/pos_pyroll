#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]
use std::process::Command as StdCommand;
use tauri::{api::process::{Command, CommandChild}, RunEvent};

#[derive(Default)]
struct Backend(Option<CommandChild>);



fn main() {
    let mut backend = Backend::default();

    tauri::Builder::default()
        .build(tauri::generate_context!())
        .expect("Error building app")
        .run(move |app_handle, event| match event {
            RunEvent::Ready => {
                let (_, child) = Command::new_sidecar("server")
                    .expect("Failed to create `backend_server` binary command")
                    .spawn()
                    .expect("Failed to spawn backend sidecar");

                _ = backend.0.insert(child);
            }
            RunEvent::ExitRequested { api, .. } => {
                if let Some(child) = backend.0.take() {
                    child.kill().expect("Failed to shutdown backend.");
                    reqwest::get("http://127.0.0.1:5000/v01/1365438ff5213531a63c246846814a"); //tells the backend to kill itself
                    println!("Backend gracefully shutdown.");
                }
            }      
            _ => {}
        });
}
