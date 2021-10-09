import React from 'react';
import SelectionWindow from '../SelectionWindow/SelectionWindow';
import SettingsList from '../settingsList/settingsList';
import Modal from '../Modal/Modal.js';
import './Settings.css';
import Checkbox from '../SettingComponents/Checkbox/Checkbox.js';
import EditedSettingsBox from '../EditedSettingsBox/EditedSettingsBox.js';

export default function Settings(props) {

    const getJobcodeName = (object) => {
        return object.SHORTNAME;
    }

    const getEmployeeName = (object) => {
        return `${object.FIRSTNAME} ${object.LASTNAME}`;
    }

    const getEmployeeFilters = (filters) => {
        if (!filters) {
            return;
        }
        return filters.map((currentFilter) => {
            //console.log(currentFilter.AVAILABLE)
            if (!currentFilter.AVAILABLE) {
                return;
            }
            return (
                <Checkbox
                    displayName={currentFilter.displayName}
                    id={currentFilter.id}
                    key={"Checkbox-" + currentFilter.displayName}
                    selected = {currentFilter.SELECTED}
                    toggle={props.toggleEmployeeFilter}
                />
            );
        });
    }

    return (
        <div className='Settings'>
            <Modal 
                openButtonLabel={'Settings'}
                className={'settings-modal'}
                headerText={'Settings'}
                innerHTML={
                    <div style={{height: "100%"}}>
                    <SettingsList 
                        settings={props.settings}
                        handleSettingChange={props.handleSettingChange}
                    />
                    <EditedSettingsBox
                        save={props.saveSettings}
                        revert={props.revertSettings}
                        display={props.settingsChanged}
                    />
                    </div>
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
            {getEmployeeFilters(props.employeeFilters)}
        </div>
    );
}
