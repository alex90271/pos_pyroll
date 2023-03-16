var fs = require('fs');
console.log('Incrementing build number...');
//const configs = ['src/metadata.json','package.json', 'src-tauri/tauri.conf.json']
var buildMajor
var buildMinor
var buildRevision

fs.readFile('src/metadata.json',function(err,content) {
    if (err) throw err;
    var metadata = JSON.parse(content);
    
    const today = new Date();
    metadata.buildRevision = metadata.buildRevision + 1;
    metadata.buildMinor = today.getMonth() + 1;

    buildRevision = metadata.buildRevision;
    buildMinor = metadata.buildMinor;
    buildMajor = metadata.buildMajor;
    fs.writeFile('src/metadata.json',JSON.stringify(metadata),function(err){
        if (err) throw err;
        console.log(`Current build number: ${metadata.buildMajor}.${metadata.buildMinor}.${metadata.buildRevision} ${metadata.buildTag}`);
    })
});

fs.readFile('package.json',function(err,content) {
    if (err) throw err;
    var metadata = JSON.parse(content);
    metadata.version = (`${buildMajor}.${buildMinor}.${buildRevision}`)
    fs.writeFile('package.json',JSON.stringify(metadata),function(err){
        if (err) throw err;
    })
});

fs.readFile('src-tauri/tauri.conf.json',function(err,content) {
    if (err) throw err;
    var metadata = JSON.parse(content);
    metadata.package.version = (`${buildMajor}.${buildMinor}.${buildRevision}`)
    fs.writeFile('src-tauri/tauri.conf.json',JSON.stringify(metadata),function(err){
        if (err) throw err;
    })
});