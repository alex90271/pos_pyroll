import React from 'react';
import './DataView.css';
import 'semantic-ui-css/semantic.min.css';
import ContentEditable from 'react-contenteditable';
import { Table } from 'semantic-ui-react';

export default function DataView() {

    const onChange = () => {
        console.log("onChange works")
    }

    const exampleObject = {
        "0":{
        "LASTNAME":"Alder",
        "FIRSTNAME":"Alex",
        "JOB_NAME":"Bitch",
        "HOURS":4.27,
        "OVERHRS":0.0,
        "SRVTIPS":0.0,
        "TIPOUT":40.422720771,
        "DECTIPS":34.894,
        "MEALS":null
    },
    "1": {
        "LASTNAME":"Baker",
        "FIRSTNAME":"Colby",
        "JOB_NAME":"Server",
        "HOURS":4.27,
        "OVERHRS":0.0,
        "SRVTIPS":0.0,
        "TIPOUT":40.0902720771,
        "DECTIPS":7.589,
        "MEALS":null
    }}

    const roundTableItems = () => {
        for (const entry in exampleObject) {
             Object.keys(exampleObject[entry]).map((item) => {
                if (item == "HOURS" || item == "OVERHRS" || item == "SRVTIPS" || item == "TIPOUT" || item == "DECTIPS" || item == "MEALS") {
                    exampleObject[entry][item] = (Math.round((exampleObject[entry][item]) * 100) / 100);
                }
            })
        }
    }
    roundTableItems();

    const tableHeaderItems = () => {
        return Object.keys(exampleObject[0]).map((key) => {
            return (
                <Table.HeaderCell>
                    {key}
                </Table.HeaderCell>
            )
        })
    }

    const tableBodyItems = () => {
        let output = [];
        for (const entry in exampleObject) {
            let currentRow = [];
            for (const item in exampleObject[entry]) {
                currentRow.push (
                    <Table.Cell>
                        <ContentEditable
                            html={exampleObject[entry][item]}
                            onChange={onChange}
                        />
                    </Table.Cell>
                    )
            }
            output.push(<Table.Row>{currentRow}</Table.Row>);
        }
        return output;
    }

    return (
        <div className="DataTable">
            <Table celled>
                <Table.Header>
                    <Table.Row>
                        {tableHeaderItems()}
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {tableBodyItems()}
                </Table.Body>
            </Table>
        </div>
        
    )
}