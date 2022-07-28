import React from 'react';
import './PathSetting.css';

export default function PathSetting(props) {
    return(
        <div id='Path-setting' className={'Setting ui segment input padded column'}>
            <h5 className={'ui header'}>
                {props.setting.displayName}
            </h5>
        </div>
    );
};