import React from 'react';
import './NumberArraySetting.css';

export default function NumberArraySetting(props) {

    const handleOnChange = (e) => {
        const selectedNumber = Number(e.target.value);
        let newArray;
        if (props.setting.value.includes(selectedNumber)) {
            newArray = props.setting.value.filter((item) => {
                return item != selectedNumber;
            });
        } else {
            newArray = props.setting.value;
            newArray.push(selectedNumber);
        }
        let newSetting = props.setting;
        newSetting.value = newArray;
        props.handleSettingChange(newSetting);
    }
    const availableSettings = props.setting.options.map((option) => {
        return (
        <div>
            <input
            key={props.setting.outputName + option}
            type='checkbox' 
            onChange={handleOnChange}
            checked={props.setting.value.includes(option)}
            value={option}/>
            <label for={option}>{option}</label>
        </div>
        )
    })

    return(
        <div className="Setting" id="Number-array-setting">
            <h3>
                {props.setting.displayName}
            </h3>
            {availableSettings}
        </div>
    );
};