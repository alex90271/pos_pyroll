import { Command } from '@tauri-apps/api/shell'
import React from 'react';
import './Header.css';

async function ServerEvent_s() {
    const cnd = Command.sidecar('bin/python/server')
    return await cnd.execute()
}

export default function Header() {
    return (
        <div>
            <button onClick={ServerEvent_s} className='ui light blue button'>
                Connect
            </button>
        </div>
    )
}