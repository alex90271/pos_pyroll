//dataType options: percent, number, numberArray, bool, path.

//value specifies initial or default value and later acts as a placeholder
//for user updated vlaues.

export const defaultSettingsObject = {
    'tip_sales_percent': {
        displayName: "Tip Sales Percent",
        outputName: "tip_sales_percent",
        step: 0.01,
        dataType: 'percent',
        value: 0.03,
    },
    'tip_amt_percent': {
        displayName: "Tip Amount Percent",
        outputName: "tip_amt_percent",
        dataType: 'percent',
        value: 100
    },
    'percent_sale_codes': {
        displayName: "Percent Sales Codes",
        outputName: "percent_sale_codes",
        dataType: 'numberArray',
        options: [1, 2, 3, 5, 8, 10, 11, 12, 13, 14],
        value: [1]
    },
    'percent_tip_codes': {
        displayName: "Percent Tip Codes",
        outputName: "percent_tip_codes",
        dataType: 'numberArray',
        options: [1, 2, 3, 5, 8, 10, 11, 12, 13, 14],
        value: [11]
    },
    'tipped_codes': {
        displayName: "Tipped Codes",
        outputName: "tipped_codes",
        dataType: 'numberArray',
        options: [1, 2, 3, 5, 8, 10, 11, 12, 13, 14],
        value: [2, 3, 5, 10, 11, 12, 13, 14]
    },
    'tracked_labor': {
        displayName: "Tracked Labor",
        outputName: "tracked_labor",
        dataType: 'numberArray',
        options: [1, 2, 3, 5, 8, 10, 11, 12, 13, 14],
        value: [8]
    },
    'pay_period_days': {
        displayName: "Pay Period Days",
        outputName: "pay_period_days",
        dataType: 'number',
        value: 15
    },
    'count_salary': {
        displayName: "Count Salary",
        outputName: "count_salary",
        dataType: 'bool',
        value: true
    },
    'debug': {
        displayName: "Debug",
        outputName: "debug",
        dataType: 'bool',
        value: false
    },
    'database': {
        displayName: "Database",
        outputName: "database",
        dataType: 'path',
        value: 'D:\\Bootdrv\\Aloha\\'
    },
    'use_aloha_tipshare': {
        displayName: "Use Aloha Tipshare",
        outputName: "use_aloha_tipshare",
        dataType: 'bool',
        value: false
    }
};