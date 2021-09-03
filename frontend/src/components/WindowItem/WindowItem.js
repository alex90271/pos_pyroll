import React, { useRef, useEffect } from 'react';
import './WindowItem.css';

export default function WindowItem(props) {

    const item = useRef(null);

    const toggleItem = () => {
       props.toggle(props.id);
        item.current.classList.toggle('active');
    }
    
    return (
        <div onClick={toggleItem} ref={item} className='WindowItem'>
            {props.innerText}
        </div>
    );
}