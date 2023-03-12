import { Command } from '@tauri-apps/api/shell'
import React, { useEffect } from 'react';
import './Header.css';

async function ForcedRefresh_s() {
    await new Promise(res => setTimeout(res, 1000));
    window.location.reload(true);
}

function ServerEvent_s() {
    const cnd = Command.sidecar('bin/python/server')
    ForcedRefresh_s();
    var srv = cnd.execute();

    const kill = () => {
        srv.kill();
    }

    return srv
}



export default function Header() {
    return (
        <div className='header'>
            <button onClick={ServerEvent_s} className='ui light blue button'>
                Connect
            </button>
            <button onClick={ServerEvent_s.kill} className='ui light disabled red button'>
                Disconnect
            </button>
            <p>
                **warning currently manual disconnect is required** TO DISCONNECT: (task manager, kill server.exe) or (reboot pc)
            </p>
        </div>
    )
}