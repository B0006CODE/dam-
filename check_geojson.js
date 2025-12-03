
const https = require('https');

const url = 'https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json';

https.get(url, (res) => {
    let data = '';

    res.on('data', (chunk) => {
        data += chunk;
    });

    res.on('end', () => {
        try {
            const geoJson = JSON.parse(data);
            console.log('Province names in GeoJSON:');
            geoJson.features.forEach(feature => {
                console.log(feature.properties.name);
            });
        } catch (e) {
            console.error(e.message);
        }
    });

}).on('error', (e) => {
    console.error(e);
});
