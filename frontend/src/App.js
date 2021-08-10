import './App.css';
import React, { useState } from 'react';
import Test from './components/test/test';
import API from './components/util/API.js';
import ConfigArea from './components/ConfigArea/ConfigArea';
import DataTable from './components/DataTable/DataTable';
import EditedTableWarning from './components/EditedTableWarning/EditedTableWarning';

function App() {

  const exampleObject = API.getExampleObject();

  const [tableEdited, setTableEdited] = useState(false);
  const [editedTableData, setEditedTableData] = useState(exampleObject);

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
    API.send();
  }

  return (
    <div className="App">
      <ConfigArea
      print={print}
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
