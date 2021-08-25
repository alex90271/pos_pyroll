import React, { useRef } from 'react';
import SettingsList from '../settingsList/settingsList';
import './Settings.css';

export default function Settings(props) {

    const openModal = () => {
        settingsModal.current.classList.add('active');
        overlay.current.classList.add('active');
    }

    const closeModal = () => {
        settingsModal.current.classList.remove('active');
        overlay.current.classList.remove('active');
    }

    const overlay = useRef(null);
    const settingsModal = useRef(null);

    return (
        <div className='Settings'>
            <button onClick={openModal}>
                Settings
            </button>
            <div ref={settingsModal} className='settings-modal'>
                <div className='settings-header'>
                    <h3>
                        Settings
                    </h3>
                    <button className='close-button' onClick={closeModal}>&times;</button>
                </div>
                <SettingsList 
                settings={props.settings}
                handleSettingChange={props.handleSettingChange}
                />
            </div>
            <div ref={overlay} onClick={closeModal} className='overlay'></div>
        </div>
    );
};
