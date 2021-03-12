import './calendar.css';
import { Calendar } from 'react-modern-calendar-datepicker';
import React, { useState } from 'react';

const CalendarComponent = (props) => {
    const [selectedDayRange, setSelectedDayRange] = useState({
        from: null,
        to: null
    });


    let displayedRange = '';
    if (selectedDayRange.from && selectedDayRange.to) {
        displayedRange = `Dates selected: ${selectedDayRange.from.month}/${selectedDayRange.from.day}/${selectedDayRange.from.year} - ${selectedDayRange.to.month}/${selectedDayRange.to.day}/${selectedDayRange.to.year}`
    }

    return (
        <div className='calendar-container' >
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