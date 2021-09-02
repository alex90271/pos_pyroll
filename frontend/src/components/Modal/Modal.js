import React, { useRef } from 'react';
import './Modal.css';

/* Basic modal I created. I made it a separate component to simplify/abstract
the Settings component and for the slight chance we can use it elsewhere.
It expects these props:

openButtonLabel
className
headerText
innerHTML
 */

export default function Modal(props) {

    const overlay = useRef(null);
    const modal = useRef(null);

    const openModal = () => {
        modal.current.classList.add('active');
        overlay.current.classList.add('active');
    }

    const closeModal = () => {
        modal.current.classList.remove('active');
        overlay.current.classList.remove('active');
    }

    return (
        <div>
            <button onClick={openModal} className={props.className + '-open-button'}>
                {props.openButtonLabel}
            </button>
            <div ref={modal} className={props.className}>
                <div className={props.className + '-header'}>
                    <h3>
                        {props.headerText}
                    </h3>
                    <button className={props.className + '-close-button'} onClick={closeModal}>&times;</button>
                </div>
                {props.innerHTML}
            </div>
            <div ref={overlay} onClick={closeModal} className='overlay'></div>
        </div>
    );
}