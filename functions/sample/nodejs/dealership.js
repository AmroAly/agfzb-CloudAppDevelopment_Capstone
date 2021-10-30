
/*
* Get All dealerships if there is no valid state
* otherwise get the dealerships for a specific state
*/
const Cloudant = require('@cloudant/cloudant');

function main(params) {

    // Get all dealerships docs for a specific state
    if(params.state) {
        return getDealershipsForState(params)
                .then((data) => { return {data: data['docs'], is_filtered: true} })
                .catch((err) => {error: err})
    }
    
    // Get all docs from dealerships Cloudant DB
    return getAllDealerships();
}

function getDealershipsForState(params) {
    return createStateIndex(params)
    .then((data) => {
        const cloudant = getCloudant();
        var mydb = cloudant.db.use('dealerships');
        
        return new Promise(function(resolve, reject) {
            mydb.find({ selector: { "st":params.state } }, function(err, data) {
                if (!err) {
                    resolve(data);
                } else {
                    reject(err);
                }
            });
        })
        
    })
    .catch((err) => {error: err})
}

function getCloudant() {
    return  Cloudant({
        url: params.COUCH_URL,
        plugins: { iamauth: { iamApiKey: params.IAM_API_KEY } }
    });
}

function getAllDealerships() {
    const cloudant = getCloudant();
    var dealershipsDB = cloudant.db.use('dealerships');
    
    return (new Promise(function(resolve, reject) {
        dealershipsDB.list({ include_docs: true }, function(err, data) {
            if (!err) {
                resolve(data);
            } else {
                reject(err);
            }
        });
    }))
    .then((data) => { return {data: data['rows']} })
            .catch((err) => {error: err})
}


function createStateIndex(params) {
    if(params.state) {
        const cloudant = getCloudant();
        var dealershipsDB = cloudant.db.use('dealerships');

        return new Promise(function(resolve, reject) {
            var stateIndex = { name:"state", type:'json', index:{fields:['st'] }}
            dealershipsDB.index(stateIndex, function(err, data) {
                if (!err) {
                    resolve(data);
                } else {
                    reject(err);
                }
            });
        })       
    }
}

function formatResponse( {data, is_filtered} ) {
    
    if(!is_filtered) {
        return {
            entries: data.map((row) => { return {
            id: row.doc.id,
            city: row.doc.city,
            state: row.doc.state,
            st: row.doc.st,
            address: row.doc.address,
            zip: row.doc.zip,
            lat: row.doc.lat,
            long: row.doc.long,
            }}),
            include_docs: true
        };
    }    
    
    return {
      entries: data.map((row) => { return {
        id: row.id,
        city: row.city,
        state: row.state,
        st: row.st,
        address: row.address,
        zip: row.zip,
        lat: row.lat,
        long: row.long,
      }}),
      include_docs: true
    };
  }