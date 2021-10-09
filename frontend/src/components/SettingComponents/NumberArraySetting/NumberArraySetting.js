import React from 'react';
import './NumberArraySetting.css';

export default function NumberArraySetting(props) {
    
    const handleOnChange = (e) => {
        let scopedSetting = Object.assign({}, props.setting);
        const selectedOption = scopedSetting.options.find(currentOption => {
            return currentOption.value === e.target.value;
        });

        let isInValueArray = scopedSetting.value.findIndex(value => {
            if (value.value === e.target.value) {
                return true;
            } else {
                return false;
            }
        });
        isInValueArray === -1 ? isInValueArray = false : isInValueArray = true;
        
        let newArray = [];
        if (isInValueArray) {
            newArray = scopedSetting.value.filter((item) => {
                return item.value !== selectedOption.value;
            });
        } else {
            newArray = scopedSetting.value;
            newArray.push(selectedOption);
        }
        scopedSetting.value = newArray;
        props.handleSettingChange(scopedSetting);
    }

    const getAvailableSettings = (setting) => {
        if (!setting.options) {
            return;
        }
        const output = setting.options.map((option) => {

            const isChecked = setting.value.some(currentValue => {
                return currentValue.value == option.value
            });

            return (
            <div className="ui middle aligned animated list" key={`${setting.outputName} ${option.displayName} div`}>
                    <div className="item">    
                        <div className={'ui toggle checkbox'}>
                            <input
                            key={setting.outputName + option.displayName}
                            type='checkbox' 
                            className={'ui toggle'}
                            onChange={handleOnChange}
                            checked={isChecked}
                            value={option.value}/>
                            <label htmlFor={option.displayName}>{option.displayName}</label>
                        </div>
                </div>
            </div>
            )
        })
        return output;
    }

    return (
        <div className={'Setting ui segment column '} id="Number-array-setting">
            <h5 className='ui header'>
                {props.setting.displayName}
            </h5>
            <div>
                {getAvailableSettings(props.setting)}
            </div>
        </div>
    );
};