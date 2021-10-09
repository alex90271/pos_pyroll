import React from 'react';
import './EditedSettingsBox.css';

export default function EditedSettingsBox(props) {

    const content = () => {
        if (props.display) {
            return (
                <div>
                    <h2>
                    Would you like to save these changes?
                    </h2>
                    <button
                        onClick={props.revert}
                        className={`EditedSettingsBox-button ${'-open-button ui compact button'}`}
                        id={'EditedSettingsBox-revert'}
                    >
                        Revert
                    </button>
                    <button 
                        onClick={props.save}
                        className={`EditedSettingsBox-button ${'-open-button ui compact button'}`}
                        id={'EditedSettingsBox-save'}
                    >
                        Save
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
        <div className={`EditedSettingsBox ${props.display ? 'settings-edited' : 'settings-not-edited'}`}>
            {content()}
        </div>
    )
} 