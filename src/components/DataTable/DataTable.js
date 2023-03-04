import React from 'react';
import './DataTable.css';
import 'semantic-ui-css/semantic.min.css';
import ContentEditable from 'react-contenteditable';
import { Table } from 'semantic-ui-react';
import EditedTableWarning from '../EditedTableWarning/EditedTableWarning';

export default function DataTable(props) {

    const handleChange = (e) => {
        const { row, column } = e.currentTarget.dataset;
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
                currentRow.push(
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
    if (!props.tableData) {
        return (
            <div className="empty-data-table">
                <h1>To get Started: <br></br>Select the report type in dropdown, then report date range<br></br>(for a single day, click it twice)</h1>
                    <h2>General Notes</h2>
                        <p>-It is important to verify totals against Aloha (total tips paid out should equal total tips on aloha)</p>
                        <p>-The data reported here is only as accurate as Aloha (ex. incorrect clockins)</p>
                        <p>-Reports with an * can be filtered by Jobcode or Employee (export file is never filtered)</p>
                    <h2>Report Info</h2>
                    <h3>Cout_eod</h3>
                        <p>-This report lists any clockins that were force closed by the end of day (3am)</p>
                    <h3>Labor Rate</h3>
                        <p>-Labor rate report pulls from pay rates set in Aloha</p>
                    <h3>Hourly</h3>
                        <p>-Hourly shows the actual hourly rate someone made, tips and all (uses pay rates set in aloha)</p>
                    <h3>Labor Average Hours</h3>
                        <p>-Labor Average shows the average hours and employee worked during the selected period</p>
                    <h3>House Account</h3>
                        <p>-House Acct report can only show transactions made between the selected dates (not a total balance)</p>
                    <h3>Labor Reports</h3>
                        <p>-Srvtips column accounts for removed tipshare (currently 4% of sales)</p>
                        <p>-Tipout is calculated on a per day, per hour basis, see the 'tip rate' report for a breakdown</p>
                        <p>-Total Tips are both Srvtips and Tipout added together</p>
            </div>
        )
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

    if (props.tableData === "exported") {
        return (
            <div className="empty-data-table">
                <h1>
                    Data has been exported
                </h1>
            </div>
        )
    }

    if (props.tableData === "day_error") {
        return (
            <div className="empty-data-table">
                <h1>
                    Dates cannot be used for export, please select a payroll interval <br></br> (ex. 1st-15th, 16th-31st)
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