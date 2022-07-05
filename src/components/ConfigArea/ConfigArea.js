import './ConfigArea.css';
import './calendar.css';
import React, { useState, useEffect } from 'react';
import { Calendar } from 'react-modern-calendar-datepicker';
import ProcessArea from '../ProcessArea/ProcessArea.js';
import Settings from '../Settings/Settings.js';
import API from '../util/API.js';
import { defaultSettingsObject } from '../../defaultSettingsObject';
import Lodash from 'lodash';

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
            AVAILABLE: true,
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
        }, 
        {
            id: 2,
            displayName: "Only show employees active during the selected time frame",
            SELECTED: false,
            AVAILABLE: false,
            filter(employees) {
                if (this.SELECTED) {
                    if (!canProcess || !preflightReportData) {
                        throw Error("Active employee filter was fired with poor context (canProcess or preflightReportData)");
                    }
                    employees.map((employee) => {
                        let employeeInPreflight = false;
                        Object.keys(preflightReportData).forEach((key) => {
                            if (preflightReportData[key].FIRSTNAME === employee.FIRSTNAME && preflightReportData[key].LASTNAME === employee.LASTNAME) {
                                employeeInPreflight = true;
                            }
                        });
                        if (!employeeInPreflight) {
                            employee.DISPLAY = false;
                        }
                        return employee;
                    });
                } else {
                    return employees;
                }
            }
        }
    ]);
    const [settingsFromBackend, setSettingsFromBackend] = useState();
    const [settings, setSettings] = useState();
    const [settingsChanged, setSettingsChanged] = useState(false);
    const [selectedDayRange, setSelectedDayRange] = useState({
        from: null,
        to: null
    });
    const today = new Date();
    const maxDate = {
        year: today.getFullYear(),
        month: today.getMonth() + 1, //date returns month number 0-11, calendar needs 1-12, so add one
        day: today.getDate()-1 //cannot process same day at this time, so select yesterday as max date
      };

    const [preflightReportData, setPreflightReportData] = useState();

    //On startup this useEffect will use the API to get jobcodes and settings from the backend.
    //The jobcodes stored in the settings object are stored using their code-number only.
    //We use the jobcode objects from the previous get query in order to map and display their names.
    useEffect(() => {
        API.jobcodes()
            .then(response => {
                response.map((jobcode) => {
                    jobcode['SELECTED'] = false;
                    jobcode['DISPLAY'] = true;
                    return jobcode;
                });
                setJobcodes(response);
                return response;
            })
            .then(jobcodes => {
                API.settings()
                    .then(data => {
                        //formatSettings is called twice in order to prevent reference issues.
                        //the objects passed into setState need to be separate.
                        setSettingsFromBackend(formatSettings(data, defaultSettingsObject, jobcodes));
                        setSettings(formatSettings(data, defaultSettingsObject, jobcodes));
                    });
            })
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
            const range = selectedDayRange;
            API.process(formatDate(range.from), formatDate(range.to))
                .then((data) => {
                    setPreflightReportData(data);
                });
        } else {
            setCanProcess(false);
            //setPreflightReportData();
        }
    }, [selectedDayRange]);

    // useEffect(() => {
    //     //props.setEditedTableData();
    //     if (canProcess) {
    //         process();
    //     }
    // }, [settings, jobcodes, employees])

    //Checks to see if settings have been changed by user
    //in order to display the save and revert options.
    useEffect(() => {
        console.log(settings);
        // console.log(settingsFromBackend);
        let haveChanged = false;
        for (const currentSetting in settings) {
            if (settings[currentSetting].dataType != 'numberArray') {
                if (settings[currentSetting].value != settingsFromBackend[currentSetting].value) {
                    haveChanged = true;
                }
            } else {
                const valueArray = settings[currentSetting].value;
                const backendValueArray = settingsFromBackend[currentSetting].value;

                if (valueArray.length != backendValueArray.length) {
                    haveChanged = true;
                }
                valueArray.forEach(currentValue => {
                    const index = backendValueArray.findIndex(currentBackendValue => {
                        if (currentValue.value === currentBackendValue.value) {
                            return true;
                        } else {
                            return false;
                        }
                    });
                    if (index === -1) {
                        haveChanged = true;
                    }
                });
            }
        }
        setSettingsChanged(haveChanged);
    }, [settings])

    // useEffect(() => {
    //     if (canProcess && preflightReportData) {
    //         setEmployeeFilters((prevState) => {
    //             let output = [...prevState];
    //             console.log(output)
    //             let index = output.findIndex((element) => element.ID === 2);
    //             output[index].AVAILABLE = true;
    //         });
    //     } else if (employeeFilters[1].AVAILABLE) {
    //         setEmployeeFilters((prevState) => {
    //             let output = [...prevState];
    //             let index = prevState.findIndex((element) => element.ID === 2);
    //             output[index].AVAILABLE = false;
    //         });
    //     }
    // }, [canProcess, preflightReportData]);

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
        employees.forEach((employee) => {
            employee.DISPLAY = true;
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

    const formatSettings = (backendSettingsArray, defaultSettings, backendJobcodes) => {
        let output = {};
        Object.keys(defaultSettings).forEach(currentSetting => {
            if (currentSetting in backendSettingsArray) {
                output[currentSetting] = Object.assign({}, defaultSettings[currentSetting]);
                if (defaultSettings[currentSetting].dataType === 'numberArray') {
                    let valueArray = backendSettingsArray[currentSetting].split(',');
                    valueArray = addDisplayNamesToValues(backendJobcodes, valueArray);
                    output[currentSetting].value = valueArray;
                    let optionsArray = getOptionsArray(backendJobcodes);
                    output[currentSetting].options = optionsArray;
                } else {
                    output[currentSetting].value = backendSettingsArray[currentSetting];
                }
            } else {
                console.log(`Could not find setting from backend: ${currentSetting}`);
            }
        });
        return output;
    }

    const addDisplayNamesToValues = (backendJobcodes, backendSettingsArray) => {
        if (!backendJobcodes) {
            return backendSettingsArray;
        }
        const output = [];
        backendSettingsArray.forEach(setting => {
            backendJobcodes.forEach(jobcode => {
                if (jobcode.ID == setting) {
                    output.push({
                        value: setting,
                        displayName: jobcode.SHORTNAME
                    });
                }
            });
        });
        return output;
    }

    const getOptionsArray = (backendJobcodes) => {
        return backendJobcodes.map((jobcode) => {
            return ({
                value: String(jobcode.ID),
                displayName: jobcode.SHORTNAME
            });
        });
    }

    const saveSettings = () => {
        API.saveSettings(settings);
    }

    const revertSettings = () => {
        setSettings(Lodash.cloneDeep(settingsFromBackend));
    }

    const process = () => {
        const range = selectedDayRange;
        API.process(formatDate(range.from), formatDate(range.to), selectedToCSV(jobcodes), selectedToCSV(employees))
            .then(data => {
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
                    maximumDate={maxDate}
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
                saveSettings={saveSettings}
                revertSettings={revertSettings}
                settingsChanged={settingsChanged}
            />
            
        </div>
    );
}