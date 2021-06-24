import './calendar.css';
import { Calendar } from 'react-modern-calendar-datepicker';
import React, { useState, useEffect } from 'react';

const CalendarComponent = (props) => {
    const [selectedDayRange, setSelectedDayRange] = useState({
        from: null,
        to: null
    });

    useEffect(() => {
        if (selectedDayRange.from && selectedDayRange.to) {
            props.setCanPrint(true);
        } else {
            props.setCanPrint(false);
        }
    })


    let displayedRange = '';
    if (selectedDayRange.from && selectedDayRange.to) {
        if (selectedDayRange.from.day === selectedDayRange.to.day) {
            displayedRange = `Date selected: ${selectedDayRange.from.month}/${selectedDayRange.from.day}/${selectedDayRange.from.year}`
        } else {
            displayedRange = `Dates selected: ${selectedDayRange.from.month}/${selectedDayRange.from.day}/${selectedDayRange.from.year} - ${selectedDayRange.to.month}/${selectedDayRange.to.day}/${selectedDayRange.to.year}`;
        }
    } else {
        displayedRange = 'Select first and last day. If calculating a single day, click it twice.';
    }
        


    return (
        <div className='Custom-calendar'>
            <Calendar
            value={selectedDayRange}
            onChange={setSelectedDayRange}
            inputPlaceholder='Select a day'
            shouldHighlightWeekends
            />
            <h3>
                {displayedRange}
            </h3>
        </div>
        
    );
};

export default CalendarComponent;