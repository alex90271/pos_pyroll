#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

fn main() {
  /***
    use std::process::Command as StdCommand;
    use tauri::api::process::Command;
    let mut command = StdCommand::from(
        Command::new_sidecar("server")
            .expect("Failed to create `server` binary command"),
    );
    let mut child = command.spawn()
        .expect("Failed to spawn backend sidecar");
      //child.kill().expect("Failed to shutdown backend.");
     */
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");

}
