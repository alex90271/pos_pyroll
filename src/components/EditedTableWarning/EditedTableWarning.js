import './EditedTableWarning.css';

export default function EditedTableWarning (props) {

    const content = () => {
        if (props.tableEdited) {
            return (
                <div>
                    <h2>
                        Table above has unsaved changes, would you like to revert back to original?
                    </h2>
                    <button
                        onClick={props.revertBackToOriginal}
                        >
                        Revert
                    </button>
                </div>
                
            )
        } else {
            return (
                <div>

                </div>
            )
        }
    }

    return (
        <div className={`EditedTableWarning ${props.tableEdited ? 'table-edited' : 'table-not-edited'}`}>
            {content()}
        </div>
    )
}