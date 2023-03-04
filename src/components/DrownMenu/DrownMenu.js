import React from 'react'
import { Dropdown } from 'semantic-ui-react'

export default function DrownMenu(props) {

  const options = (array) => {
    const output = [];
    array.forEach((item) => {
      output.push(
        item
      );
    });
    return output;
  }

  return (
    <Dropdown
      placeholder='Change Report'
      floating labeled button
      className='icon'
      onChange={props.change}
      options={options(props.reports)}
    />
  )
}
