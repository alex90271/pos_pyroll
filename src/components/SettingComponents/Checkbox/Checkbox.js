import React from 'react';
import './Checkbox.css';

export default function Checkbox(props) {

    const handleOnChange = (e) => {
      props.toggle(props.id, !props.selected)
    }

    return (
        <div className="Checkbox ui toggle checkbox">
              <input 
                type="checkbox"
                onChange={handleOnChange}
                checked={props.selected}
                className={'ui toggle'}
              />
              <label>{props.displayName}</label>
        </div>
    )
}
