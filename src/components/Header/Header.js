import { Command } from '@tauri-apps/api/shell'
import React, { useRef, useState } from 'react';
import './Header.css';


export default function Header() {

    const [connected, updateConnection] = useState(null);
    const connect = useRef(null);
    const disconnect = useRef(null);

    function ServerEvent_s() {
        Command.sidecar('bin/python/server').spawn();
        updateConnection(true);
        connect.current.classList.add('disabled');
        disconnect.current.classList.remove('disabled');

    }
    
    function KillServerEvent_s() {
        fetch(`http://127.0.0.1:5000/v01/1365438ff5213531a63c246846814a`)
        updateConnection(false);
        connect.current.classList.remove('disabled');
        disconnect.current.classList.add('disabled');

    }
    
    
    const isConnected = () => {
        if (connected === true) {
            return ('currently connected')
        }
        else if (connected === false) {
            return ('disconnected')
        } else {
            return ('click connect to start')
        }
    }

    
    return (
        <div className='header'>
        <button ref={connect} onClick={ServerEvent_s} className='ui light blue button'>
            Connect
        </button>
        <button ref={disconnect} onClick={KillServerEvent_s} className='ui light red button disabled'>
            Disconnect
        </button>
            {isConnected()}
        </div>
    )
}