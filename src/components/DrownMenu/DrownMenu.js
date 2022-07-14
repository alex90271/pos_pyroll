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
  <div className='thediv'>
    <Dropdown
      placeholder='select report'
      floating labeled button
      className='icon' 
      options={options(props.reports)}
    />
  </div>
)
}
