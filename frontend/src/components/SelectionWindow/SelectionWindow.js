import React from 'react';
import WindowItem from '../WindowItem/WindowItem.js';
import './SelectionWindow.css';

export default function SelectionWindow(props) {

    const options = (array) => {
        if (!array) {
            return;
        }
        const output = [];
        array.forEach((item) => {
            if (!item.DISPLAY) {
                return;
            }
            output.push(
                <WindowItem
                    innerText={props.parsingFunction(item)}
                    key={props.title + item.ID}
                    id={item.ID}
                    toggle={props.toggle}
                    selected={item.SELECTED}
                />
            );
        });
        return output;
    }

    return (
        <div className={'selection-window ui raised segment'}>
            <h3>{props.title}</h3>
            <div className={'box'}>
                {options(props.options)}
            </div>
        </div>
    );
}