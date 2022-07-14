import React from 'react'
import { Dropdown, DropdownItem, Icon } from 'semantic-ui-react'

export default function DrownMenu(props) {

  var selected = (array) => array[1];

  const options = (array) => {
    const output = [];
    array.forEach((item) => {
        output.push(
          <Dropdown.Item>
            {item}
          </Dropdown.Item>
        );
    });
    return output;
  }

return (
  <Dropdown text={selected(props.reports)} floating labeled button className='icon'>
    <Dropdown.Menu className='left'>
      {options(
            props.reports
        )}
    </Dropdown.Menu>
  </Dropdown>
)
}
