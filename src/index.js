import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { Command } from '@tauri-apps/api/shell'

const launchServer = async () => {
  // the EXACT value specified on `tauri.conf.json > tauri > bundle > externalBin`
  const command = Command.sidecar('bin/python/server')
  await command.execute()
};
launchServer();

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
