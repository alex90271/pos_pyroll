import './App.css';
import React, { useState } from 'react';
import ConfigArea from './components/ConfigArea/ConfigArea';
import DataTable from './components/DataTable/DataTable';

function App() {

  // const [tableEdited, setTableEdited] = useState(false);
  const [editedTableData, setEditedTableData] = useState();

  const columnsToRound = ["HOURS", "OVERHRS", "SRVTIPS", "TIPOUT", "DECTIPS", "MEALS"];
  // const editableColumns = ["HOURS", "OVERHRS", "SRVTIPS", "TIPOUT", "DECTIPS", "MEALS"];

  // const editTable = (row, column, newValue) => {
  //   setTableEdited(true);
  //   setEditedTableData((prevState) => {
  //     const currentRow = prevState[row];
  //     currentRow[column] = newValue;
  //     return {
  //       ...prevState,
  //       [row]: currentRow
  //     }
  //   });
  // }

  // const revertBackToOriginal = () => {
  //   setTableEdited(false);
  // }

  return (
    <div className="App">
      <ConfigArea
      setEditedTableData={setEditedTableData}
      />
      <DataTable
        tableData={editedTableData}
        roundNumbers={false}
        columnsToRound={columnsToRound}
        // editableColumns={editableColumns}
        // editTable={editTable}
        // canEditTable={false}
        // tableEdited={tableEdited}
        //revertBackToOriginal={revertBackToOriginal}
      />
    </div>
  );
}

export default App;

