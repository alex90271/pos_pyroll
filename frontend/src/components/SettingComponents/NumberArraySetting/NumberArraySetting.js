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
        <div className="ui middle aligned animated list" key={props.setting.outputName + option + "div"}>
                <div className="item">    
                    <div className={'ui toggle checkbox'}>
                        <input
                        key={props.setting.outputName + option}
                        type='checkbox' 
                        className={'ui toggle'}
                        onChange={handleOnChange}
                        checked={props.setting.value.includes(option)}
                        value={option}/>
                        <label htmlFor={option}>{option}</label>
                    </div>
            </div>
        </div>
        )
    })

    return (
        <div className={'Setting ui segment column '} id="Number-array-setting">
            <h5 className='ui header'>
                {props.setting.displayName}
            </h5>
            <div>
                {availableSettings}
            </div>
        </div>
    );
};