import { Command } from '@tauri-apps/api/shell'
import React, { useEffect } from 'react';
import './Header.css';
import API from '../util/API.js';

async function ForcedRefresh_s() {
    await new Promise(res => setTimeout(res, 1000));
    window.location.reload(true);
}

function ServerEvent_s() {
    const cnd = Command.sidecar('bin/python/server')
    ForcedRefresh_s();
    return cnd.spawn();

}

function KillServerEvent_s() {
    var link = document.createElement('a');
    link.href = (`http://127.0.0.1:5000/v01/1365438ff5213531a63c246846814a`)
    link.dispatchEvent(new MouseEvent('click'));
}


export default function Header() {
    return (
        <div className='header'>
            <button onClick={ServerEvent_s} className='ui light blue button'>
                Connect
            </button>
            <button onClick={KillServerEvent_s} className='ui light disabled red button'>
                Disconnect
            </button>
            <p>
                **warning currently manual disconnect is required** TO DISCONNECT: (task manager, kill server.exe) or (reboot pc)
            </p>
        </div>
    )
}