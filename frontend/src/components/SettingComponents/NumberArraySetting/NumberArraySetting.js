import React from 'react';
import './NumberArraySetting.css';

export default function NumberArraySetting(props) {

    const handleOnChange = (e) => {
        const selectedNumber = Number(e.target.value);
        let newArray;
        if (props.setting.value.includes(selectedNumber)) {
            newArray = props.setting.value.filter((item) => {
                return item !== selectedNumber;
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
        <div key={props.setting.outputName + option + "div"} class='ui label'>
            <input
            key={props.setting.outputName + option}
            type='checkbox' 
            class='ui checkbox'
            onChange={handleOnChange}
            checked={props.setting.value.includes(option)}
            value={option}/>
            <label htmlFor={option}>{option}</label>
        </div>
        )
    })

    return (
        <div className="Setting" id="Number-array-setting" class='ui label column'>
            <h3 class='ui header'>
                {props.setting.displayName}
            </h3>
            <div>
                {availableSettings}
            </div>
        </div>
    );
};