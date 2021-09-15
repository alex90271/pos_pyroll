import './ConfigArea.css';
import './calendar.css';
import React, { useState, useEffect } from 'react';
import { Calendar } from 'react-modern-calendar-datepicker';
import ProcessArea from '../ProcessArea/ProcessArea.js';
import Settings from '../Settings/Settings.js';
import API from '../util/API.js';
import { defaultSettingsObject } from '../../defaultSettingsObject';

export default function ConfigArea(props) {

    const [canProcess, setCanProcess] = useState(false);
    const [jobcodes, setJobcodes] = useState([]);
    const [jobcodeFilters, setJobcodeFilters] = useState({});
    const [employees, setEmployees] = useState([]);
    const [employeeFilters, setEmployeeFilters] = useState([
        {
            id: 1,
            displayName: "Show Terminated Employees",
            SELECTED: false,
            filter(employees) {
                if (!this.SELECTED) {
                    employees.map((employee) => {
                        if (employee.TERMINATED === "Y") {
                            employee.DISPLAY = false;
                        }
                        return employee;
                    });
                    return employees;
                } else {
                    return employees;
                }
            },
        }
    ]);
    const [settings, setSettings] = useState(defaultSettingsObject);
    const [selectedDayRange, setSelectedDayRange] = useState({
        from: null,
        to: null
    });

    useEffect(() => {
        API.jobcodes()
            .then(response => {
                response.map((jobcode) => {
                    jobcode['SELECTED'] = false;
                    jobcode['DISPLAY'] = true;
                    return jobcode;
                });
                setJobcodes(response);
            });
    }, []);

    useEffect(() => {
        API.employees()
            .then(response => {
                response.map((employee) => {
                    employee['SELECTED'] = false;
                    employee['DISPLAY'] = true;
                    return employee;
                });
                setEmployees(applyEmployeeFilters(response));
            });
    }, []);

    useEffect(() => {
        if (selectedDayRange.from && selectedDayRange.to) {
            setCanProcess(true);
        } else {
            setCanProcess(false);
        }
    }, [selectedDayRange]);

    // useEffect(() => {
    //     setEmployees((prevState) => {
    //         return applyEmployeeFilters(prevState);
    //     });
    // }, [employeeFilters, employees]);

    const toggleJobcode = (id, newValue) => {
        setJobcodes((prevState) => {
            let output = [...prevState];
            let index = prevState.findIndex((element) => element.ID === id);
            output[index].SELECTED = newValue;
            return output;
        });
    }

    
    const toggleEmployee = (id, newValue) => {
        setEmployees((prevState) => {
            let output = [...prevState]
            let index = prevState.findIndex((element) => element.ID === id);
            output[index].SELECTED = newValue;
            return output;
        });
    }

    const toggleEmployeeFilter = (id, newValue) => {
        setEmployeeFilters((prevState) => {
            let output = [...prevState];
            let index = prevState.findIndex((element) => element.id === id);
            output[index].SELECTED = newValue;
            return output;
        });
        setEmployees((prevState) => {
            return applyEmployeeFilters(prevState);
        });
    }

    const showAllEmployees = (employees) => {
        employees.map((employee) => {
            employee.DISPLAY = true;
            return employee;
        });
        return employees;
    }

    const applyEmployeeFilters = (employees) => {
        if (!employees) {
            return;
        }
        employees = showAllEmployees(employees);
        employeeFilters.forEach((currentFilter) => {
            employees = currentFilter.filter(employees);
        });
        employees = unSelectAllNotDisplayedEmployees(employees);
        return employees;
    }

    const unSelectAllNotDisplayedEmployees = (employees) => {
        employees.map((employee) => {
            if (!employee.DISPLAY) {
                employee.SELECTED = false;
            }
            return employee;
        });
        return employees;
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

    const displayedRange = () => {
        if (selectedDayRange.from && selectedDayRange.to) {
            if (selectedDayRange.from.day === selectedDayRange.to.day) {
                return `Date selected: ${selectedDayRange.from.month}/${selectedDayRange.from.day}/${selectedDayRange.from.year}`
            } else {
                return `Dates selected: ${selectedDayRange.from.month}/${selectedDayRange.from.day}/${selectedDayRange.from.year} - ${selectedDayRange.to.month}/${selectedDayRange.to.day}/${selectedDayRange.to.year}`;
            }
        } else {
            return 'Select first and last day. If calculating a single day, click it twice.';
        }
    }

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

    function process() {
        const range = selectedDayRange;
        API.test(formatDate(range.from), formatDate(range.to), selectedToCSV(jobcodes), selectedToCSV(employees))
            .then(data => {
            //console.log(data);
            props.setEditedTableData(data);
            });
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
            <ProcessArea
                canProcess={canProcess}
                process={process}
                displayedRange={displayedRange()}
            />
            <Settings
                settings={settings}
                handleSettingChange={handleSettingChange}
                jobcodes={jobcodes}
                toggleJobcode={toggleJobcode}
                jobcodeFilters={jobcodeFilters}
                employees={employees}
                toggleEmployee={toggleEmployee}
                employeeFilters={employeeFilters}
                toggleEmployeeFilter={toggleEmployeeFilter}
            />
            
        </div>
    );
}