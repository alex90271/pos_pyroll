import './ConfigArea.css';
import './calendar.css';
import React, { useState, useEffect } from 'react';
import { Calendar } from 'react-modern-calendar-datepicker';
import PrintArea from '../PrintArea/PrintArea.js';
import Settings from '../Settings/Settings.js';
import API from '../util/API.js';

export default function ConfigArea(props) {

    const [canPrint, setCanPrint] = useState(false);
    const [jobcodes, setJobcodes] = useState([]);
    const [employees, setEmployees] = useState([]);

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
                settings={props.settings}
                handleSettingChange={props.handleSettingChange}
                jobcodes={jobcodes}
                toggleJobcode={toggleJobcode}
                employees={employees}
                toggleEmployee={toggleEmployee}
            />
            
        </div>
    );
}