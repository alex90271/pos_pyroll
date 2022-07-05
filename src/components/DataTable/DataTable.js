import React from 'react';
import './DataTable.css';
import 'semantic-ui-css/semantic.min.css';
import ContentEditable from 'react-contenteditable';
import { Table } from 'semantic-ui-react';
import EditedTableWarning from '../EditedTableWarning/EditedTableWarning';

export default function DataTable(props) {

    const handleChange = (e) => {
        const {row, column} = e.currentTarget.dataset;
        const newValue = e.target.value;
        props.editTable(row, column, newValue);
    }

    const roundTableItems = (tableObject) => {
        for (const row in tableObject) {
            for (const column in tableObject[row]) {
                if (props.columnsToRound.includes(column)) {
                    tableObject[row][column] = (Math.round((tableObject[row][column]) * 100) / 100);
                }
            }
        }
        return tableObject;
    }
    
    const canEditCell = (column) => {
        if (!props.canEditTable) {
            return false;
        } else if (props.editableColumns.includes(column)) {
            return true;
        } else {
            return false;
        }
    }
    
    const tableHeaderItems = (tableObject) => {
        if (!props.tableData) {
            return;
        }
        return (
            <Table.Row className={"TableHeader"}>
                {Object.keys(tableObject[0]).map((column) => {
                    return (
                        <Table.HeaderCell
                            key={column}
                        >
                            {column}
                        </Table.HeaderCell>
                        
                    )
                })}  
            </Table.Row>          
        )
    }

    const tableBodyItems = (tableObject) => {
        if (!props.tableData) {
            return;
        }
        if (props.roundNumbers) {
            tableObject = roundTableItems(tableObject);
        }
        let output = [];
        for (const row in tableObject) {
            let currentRow = [];
            for (const column in tableObject[row]) {
                let value = tableObject[row][column];
                if (value === null) {
                    value = 0;
                }
                currentRow.push (
                    <Table.Cell
                    key={row + column + "Table.cell"}
                    >
                        <ContentEditable
                            html={value.toString()}
                            onChange={handleChange}
                            key={row + column + "ContentEditable"}
                            data-row={row}
                            data-column={column}
                            disabled={!canEditCell(column)}
                        />
                    </Table.Cell>
                )
            }
            output.push(<Table.Row key={row + "Table.Row"}>{currentRow}</Table.Row>);
        }
        return output;
    }



    if (props.tableData === "empty") {
        return (
            <div className="empty-data-table">
                <h1>
                    No data for selected date/s
                </h1>
            </div>
        )
    }

    return (
        <div className="DataTable">
            <Table striped>
                <Table.Header className={"TableHeader"} >
                    {tableHeaderItems(props.tableData)}
                </Table.Header>
                <Table.Body className={"TableBody"}>
                    {tableBodyItems(props.tableData)}
                </Table.Body>
            </Table>
            <EditedTableWarning 
            tableEdited={props.tableEdited}
            //revertBackToOriginal={props.revertBackToOriginal}
            />
        </div>
        
    )
}