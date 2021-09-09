import React from 'react';
import SelectionWindow from '../SelectionWindow/SelectionWindow';
import SettingsList from '../settingsList/settingsList';
import Modal from '../Modal/Modal.js';
import './Settings.css';

export default function Settings(props) {

    const getJobcodeName = (object) => {
        return object.SHORTNAME;
    }

    const getEmployeeName = (object) => {
        return `${object.FIRSTNAME} ${object.LASTNAME}`;
    }

    return (
        <div className='Settings'>
            <Modal 
                openButtonLabel={<i class='cog icon'></i>}
                className={'settings-modal'}
                headerText={'Settings'}
                innerHTML={
                    <SettingsList 
                        settings={props.settings}
                        handleSettingChange={props.handleSettingChange}
                    />
                }
            />
            <SelectionWindow 
                title={"Jobcodes"}
                parsingFunction={getJobcodeName}
                options={props.jobcodes}
                toggle={props.toggleJobcode}
            />
            <SelectionWindow
                title={"Employees"}
                parsingFunction={getEmployeeName}
                options={props.employees}
                toggle={props.toggleEmployee}
            />
        </div>
    );
}
