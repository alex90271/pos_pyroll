import React from 'react';
import './ProcessArea.css';

export default function ProcessArea(props) {

    const availableOptions = () => {
        if (props.canProcess) {
            return (
                <div>
                <button onClick={props.process} className='ui light blue button'>
                    Process
                </button>
                 <button onClick={props.print} className='ui light grey button'>
                    Print
                </button>
                </div>
            )
        } else {
            return (
                <div>

                </div>
            )
        }
    }

    return (
        <div className='ProcessArea'>
            <h3>
                {props.displayedRange}
            </h3>
            {availableOptions()}
        </div>
    );
}