#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]
use std::{collections::HashMap};
use std::error::Error;
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
                    println!("tell it to kill itself");
                    let _ = killsrv();
                    println!("trying to kill it in case");
                    child.kill().expect("Failed to shutdown backend.");
                    println!("Backend gracefully shutdown.");
                }
            }      
            _ => {}
        });
}


fn killsrv() -> Result<(), Box<dyn Error>> {        
    let resp = reqwest::blocking::get("http://127.0.0.1:5000/v01/1365438ff5213531a63c246846814a")?
    .json::<HashMap<String, String>>()?;
    println!("{:#?}", resp);
    Ok(())
}