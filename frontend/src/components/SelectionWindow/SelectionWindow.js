import React from 'react';
import WindowItem from '../WindowItem/WindowItem.js';
import './SelectionWindow.css';

export default function SelectionWindow(props) {

    const options = (array) => {
        if (!array) {
            return;
        }
        let output = [];
        array.forEach((item) => {
            output.push(
                <WindowItem
                    innerText={props.parsingFunction(item)}
                    key={item.ID}
                    id={item.ID}
                    toggle={props.toggle}
                    selected={item.SELECTED}
                />
            );
        })
        return output;
    }

    return (
        <div className='selection-window'>
            <h1>{props.title}</h1>
            <div className='box'>
                {options(props.options)}
            </div>
        </div>
    );
}