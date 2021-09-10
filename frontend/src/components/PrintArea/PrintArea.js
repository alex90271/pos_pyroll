import React from 'react';
import './PrintArea.css';

export default function PrintArea(props) {

    const availableOptions = () => {
        if (props.canPrint) {
            return (
                <button onClick={props.print} className='ui light blue button'>
                    Process
                </button>
            )
        } else {
            return (
                <div>

                </div>
            )
        }
    }

    return (
        <div className='PrintArea'>
            <h3>
                {props.displayedRange}
            </h3>
            {availableOptions()}
        </div>
    );
}