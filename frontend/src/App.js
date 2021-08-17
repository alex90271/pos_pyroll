import './App.css';
import React, { useEffect, useState } from 'react';
import Test from './components/test/test';
import API from './components/util/API.js';
import ConfigArea from './components/ConfigArea/ConfigArea';
import DataTable from './components/DataTable/DataTable';
import EditedTableWarning from './components/EditedTableWarning/EditedTableWarning';

function App() {

  const exampleObject = API.getExampleObject();

  const [tableEdited, setTableEdited] = useState(false);
  const [editedTableData, setEditedTableData] = useState();
  const [selectedDayRange, setSelectedDayRange] = useState({
    from: null,
    to: null
  });

  //converts the selectedDayRange(.from or .to) object into yyyymmdd format for use with the API.
  const formatDate = (range) => {
    return new Date(range.year, range.month - 1, range.day).toISOString().slice(0, 10).replace(/-/g, "");
  }

  const editTable = (row, column, newValue) => {
    setTableEdited(true);
    setEditedTableData((prevState) => {
      const currentRow = prevState[row];
      currentRow[column] = newValue;
      return {
        ...prevState,
        [row]: currentRow
      }
    })
  }

  const revertBackToOriginal = () => {
    setEditedTableData(exampleObject);
    setTableEdited(false);
  }

  const columnsToRound = ["HOURS", "OVERHRS", "SRVTIPS", "TIPOUT", "DECTIPS", "MEALS"];

  function print() {
    const range = selectedDayRange;
    console.log(formatDate(selectedDayRange.from))
    API.test(formatDate(selectedDayRange.from), formatDate(selectedDayRange.to))
      // .then(data => {
      //   setEditedTableData(data);
      // })
  }

  return (
    <div className="App">
      <ConfigArea
      print={print}
      selectedDayRange={selectedDayRange}
      setSelectedDayRange={setSelectedDayRange}
      />
      <div className='table-area'>
        <DataTable
          tableData={editedTableData}
          roundNumbers={true}
          columnsToRound={columnsToRound}
          editTable={editTable}
          canEditTable={false}
        />
        <EditedTableWarning
          tableEdited={tableEdited}
          revertBackToOriginal={revertBackToOriginal}
        />
      </div>
    </div>
  );
}

export default App;

