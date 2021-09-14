import React from 'react';
import './Checkbox.css';

export default function Checkbox(props) {

    const handleOnChange = (e) => {
      props.toggle(props.id, !props.selected)
    }

    return (
        <div className="Checkbox">
              <input 
                type="checkbox"
                onChange={handleOnChange}
                checked={props.selected}
              />
              <label>{props.displayName}</label>
        </div>
    )
}
