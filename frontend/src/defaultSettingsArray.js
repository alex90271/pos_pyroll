//dataType options: percent, number, numberArray, bool, path

export const defaultSettingsArray = [
    {
        displayName: "Tip Sales Percent",
        outputName: "tip_sales_percent",
        dataType: 'percent',
        defaultValue: 0.03
    }, 
    {
        displayName: "Tip Amount Percent",
        outputName: "tip_amt_percent",
        dataType: 'percent',
        defaultValue: 100
    }, 
    {
        displayName: "Percent Sales Codes",
        outputName: "percent_sale_codes",
        dataType: 'numberArray',
        defaultValue: [1]
    },
    {
        displayName: "Percent Tip Codes",
        outputName: "percent_tip_codes",
        dataType: 'numberArray',
        defaultValue: [11]
    },
    {
        displayName: "Tipped Codes",
        outputName: "tipped_codes",
        dataType: 'numberArray',
        defaultValue: [2, 3, 5, 10, 11, 12, 13, 14]
    },
    {
        displayName: "Tracked Labor",
        outputName: "tracked_labor",
        dataType: 'numberArray',
        defaultValue: [8]
    },
    {
        displayName: "Pay Period Days",
        outputName: "pay_period_days",
        dataType: 'number',
        defaultValue: 15
    },
    {
        displayName: "Count Salary",
        outputName: "count_salary",
        dataType: 'bool',
        defaultValue: true
    }, 
    {
        displayName: "Debug",
        outputName: "debug",
        dataType: 'bool',
        defaultValue: false
    },
    {
        displayName: "Database",
        outputName: "database",
        dataType: 'path',
        defaultValue: 'D:\\Bootdrv\\Aloha\\'
    }, 
    {
        displayName: "Use Aloha Tipshare",
        outputName: "use_aloha_tipshare",
        dataType: 'bool',
        defaultValue: false
    }
];