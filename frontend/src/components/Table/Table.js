import React from 'react';
import './Table.css';
import 'semantic-ui-css/semantic.min.css';
import ContentEditable from 'react-contenteditable';
import { Table } from 'semantic-ui-react';

export default function Table(props) {

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

    const tableHeaderItems = (tableObject) => {
        return (
            <Table.Row>
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
                            disabled={!props.canEditTable}
                        />
                    </Table.Cell>
                )
            }
            output.push(<Table.Row key={row + "Table.Row"}>{currentRow}</Table.Row>);
        }
        return output;
    }

    const handleChange = (e) => {
        const {row, column} = e.currentTarget.dataset;
        const newValue = e.target.value;
        props.editTable(row, column, newValue);
    }

    return (
        <div className="DataTable">
            <Table celled>
                <Table.Header>
                    {tableHeaderItems(props.tableData)}
                </Table.Header>
                <Table.Body>
                    {tableBodyItems(props.tableData)}
                </Table.Body>
            </Table>
        </div>
        
    )
}