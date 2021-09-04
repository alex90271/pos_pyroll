import './ConfigArea.css';
import './calendar.css';
import React, { useState, useEffect } from 'react';
import { Calendar } from 'react-modern-calendar-datepicker';
import PrintArea from '../PrintArea/PrintArea.js';
import Settings from '../Settings/Settings.js';
import API from '../util/API.js';
import { defaultSettingsObject } from '../../defaultSettingsObject';

export default function ConfigArea(props) {

    const [canPrint, setCanPrint] = useState(false);
    const [jobcodes, setJobcodes] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [settings, setSettings] = useState(defaultSettingsObject);
    const [selectedDayRange, setSelectedDayRange] = useState({
        from: null,
        to: null
    });
    let displayedRange = '';

    const toggleJobcode = (id) => {
        setJobcodes((prevState) => {
            let output = prevState;
            let index = prevState.findIndex((element) => element.ID == id);
            output[index].SELECTED = !output[index].SELECTED;
            return output;
        });
    }

    useEffect(() => {
        if (jobcodes.length === 0) {
            API.jobcodes()
                .then(response => {
                    response.map((jobcode) => {
                        jobcode['SELECTED'] = false;
                    });
                    setJobcodes(response);
                })
        }
    }, []);

    const toggleEmployee = (id) => {
        setEmployees((prevState) => {
            let output = prevState;
            let index = prevState.findIndex((element) => element.ID == id);
            output[index].SELECTED = !output[index].SELECTED;
            return output;
        });
    }

    useEffect(() => {
        if (employees.length === 0) {
            API.employees()
                .then(response => {
                    response.map((employee) => {
                        employee['SELECTED'] = false;
                    });
                    setEmployees(response);
                })
        }
    }, []);

    useEffect(() => {
        if (selectedDayRange.from && selectedDayRange.to) {
            setCanPrint(true);
            if (selectedDayRange.from.day === selectedDayRange.to.day) {
                displayedRange = `Date selected: ${selectedDayRange.from.month}/${selectedDayRange.from.day}/${selectedDayRange.from.year}`
            } else {
                displayedRange = `Dates selected: ${selectedDayRange.from.month}/${selectedDayRange.from.day}/${selectedDayRange.from.year} - ${selectedDayRange.to.month}/${selectedDayRange.to.day}/${selectedDayRange.to.year}`;
            }
        } else {
            setCanPrint(false);
            displayedRange = 'Select first and last day. If calculating a single day, click it twice.';
        }
    }, [selectedDayRange]);










  

  //converts the selectedDayRange(.from or .to) object into yyyymmdd format for use with the API.
  //1 is subtracted from range.month as the Date constructor uses a month index starting at 0 for January.
  const formatDate = (range) => {
    return new Date(range.year, range.month - 1, range.day).toISOString().slice(0, 10).replace(/-/g, "");
  }

  const selectedToCSV = (inputArray) => {
      let output = [];
      inputArray.forEach((item) => {
          if (item.SELECTED === true) {
              output.push(item.ID);
          }
      });
      if (output.length === 0) {
          return "0";
      } else {
          return output.join();
      }
  }

  

  function handleSettingChange(newSetting) {
    if (newSetting.displayName && newSetting.outputName && newSetting.dataType && (typeof(newSetting.value) !== 'undefined')) {
      setSettings((prevSettings) => ({
        ...prevSettings, [newSetting.outputName]: newSetting
      }));
    } else {
      throw Error("Something went wrong. (the newSetting object is not complete)");
    }
  }

  function print() {
    const range = selectedDayRange;
    API.test(formatDate(range.from), formatDate(range.to), selectedToCSV(jobcodes), selectedToCSV(employees))
      .then(data => {
        //console.log(data);
        props.setEditedTableData(data);
      })
  }

    return (
        <div className="ConfigArea">
            <div className='CustomCalendar'>
                <Calendar
                    value={selectedDayRange}
                    onChange={setSelectedDayRange}
                    inputPlaceholder='Select a day'
                    shouldHighlightWeekends
                />
            </div>
            <PrintArea
                canPrint={canPrint}
                print={print}
                displayedRange={displayedRange}
            />
            <Settings
                settings={settings}
                handleSettingChange={handleSettingChange}
                jobcodes={jobcodes}
                toggleJobcode={toggleJobcode}
                employees={employees}
                toggleEmployee={toggleEmployee}
            />
            
        </div>
    );
}