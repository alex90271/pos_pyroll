import React from 'react';
import './PrintArea.css';

export default function PrintArea(props) {

    const availableOptions = () => {
        if (props.canPrint) {
            return (
                <button onClick={props.print}>
                    Print
                </button>
            )
        } else {
            return (
                <div style={{paddingBottom: '21px'}}>

                </div>
            )
        }
    }

    return (
        <div className='PrintArea'>
            {availableOptions()}
        </div>
    );
}