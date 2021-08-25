import './ConfigArea.css';
import './calendar.css';
import React, { useState, useEffect } from 'react';
import { Calendar } from 'react-modern-calendar-datepicker';
import PrintArea from '../PrintArea/PrintArea.js';
import Settings from '../Settings/Settings.js';
import { defaultSettingsObject } from '../../defaultSettingsObject';


export default function ConfigArea(props) {

    const [settings, setSettings] = useState(defaultSettingsObject);
    const [canPrint, setCanPrint] = useState(false);

    function handleSettingChange(newSetting) {
        if (newSetting.displayName && newSetting.outputName && newSetting.dataType && (typeof(newSetting.value) !== 'undefined')) {
          setSettings((prevSettings) => ({
            ...prevSettings, [newSetting.outputName]: newSetting
          }));
        } else {
          throw Error("Something went wrong. (the newSetting object is not complete)");
        }
      }

      useEffect(() => {
          if (props.selectedDayRange.from && props.selectedDayRange.to) {
              setCanPrint(true);
          } else {
              setCanPrint(false);
          }
      }, [props.selectedDayRange]);

      let displayedRange = '';
      if (props.selectedDayRange.from && props.selectedDayRange.to) {
          if (props.selectedDayRange.from.day === props.selectedDayRange.to.day) {
              displayedRange = `Date selected: ${props.selectedDayRange.from.month}/${props.selectedDayRange.from.day}/${props.selectedDayRange.from.year}`
          } else {
              displayedRange = `Dates selected: ${props.selectedDayRange.from.month}/${props.selectedDayRange.from.day}/${props.selectedDayRange.from.year} - ${props.selectedDayRange.to.month}/${props.selectedDayRange.to.day}/${props.selectedDayRange.to.year}`;
          }
      } else {
          displayedRange = 'Select first and last day. If calculating a single day, click it twice.';
      }



    return (
        <div className="ConfigArea">
            <div className='CustomCalendar'>
                <Calendar
                value={props.selectedDayRange}
                onChange={props.setSelectedDayRange}
                inputPlaceholder='Select a day'
                shouldHighlightWeekends
                />
            </div>
            <PrintArea
            canPrint={canPrint}
            print={props.print}
            displayedRange={displayedRange}
            />
            <Settings
            settings={settings}
            handleSettingChange={handleSettingChange}
            />
            
        </div>
    );
}