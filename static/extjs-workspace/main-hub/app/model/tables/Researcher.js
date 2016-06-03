Ext.define('MainHub.model.tables.Researcher', {
    extend: 'MainHub.model.Base',

    fields: [
        {
            type: 'string',
            name: 'firstName'
        },
        {
            type: 'string',
            name: 'lastName'
        },
        {
            type: 'string',
            name: 'telephone'
        },
        {
            type: 'string',
            name: 'email'
        },
        {
            type: 'string',
            name: 'pi'
        },
        {
            type: 'string',
            name: 'organization'
        },
        {
            type: 'string',
            name: 'costUnit'
        }
    ]
});
