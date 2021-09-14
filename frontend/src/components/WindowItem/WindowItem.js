import React, { useRef, useEffect } from 'react';
import './WindowItem.css';

export default function WindowItem(props) {

    const item = useRef(null);

    const handleClick = () => {
       props.toggle(props.id, !props.selected);
    }

    useEffect(() => {
        if (props.selected) {
            item.current.classList.add("active");
        } else {
            item.current.classList.remove("active");
        }
    }, [props.selected]);
    
    return (
        <div onClick={handleClick} ref={item} className='WindowItem'>
            {props.innerText}
        </div>
    );
}