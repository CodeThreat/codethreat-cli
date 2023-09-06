const fs = require('fs-extra');
const path = require('path');
const archiver = require('archiver');

/**
 * @param {String} sourceDir: /some/folder/to/compress
 * @returns {Promise}
 */
function zipDirectory(sourceDir) {
  const archive = archiver('zip', { zlib: { level: 9 }});
    // Check if sourceDir is empty
    const files = fs.readdirSync(sourceDir);
    if (files.length === 0) {
        console.error(`The directory ${sourceDir} is empty. Nothing to zip.`);
        return Promise.reject(new Error(`The directory ${sourceDir} is empty. Nothing to zip.`));
    }
    // Define the outPath based on the sourceDir
    const outPath = path.join(path.dirname(sourceDir), `${path.basename(sourceDir)}.zip`);
    const stream = fs.createWriteStream(outPath);


    return new Promise((resolve, reject) => {
        archive
          .directory(sourceDir, false)
          .on('error', err => {
            console.error("Archiver error:", err);
            reject(err);
          })
          .on('warning', warning => {
            console.warn("Archiver warning:", warning);
          })
          .pipe(stream);
    
        stream
          .on('close', () => resolve(outPath))
          .on('error', err => {
            console.error("Stream error:", err);
            reject(err);
          });
    
        console.log(`Starting to zip directory: ${sourceDir} to ${outPath}`);
        archive.finalize();
      });
}

module.exports = {
  zipDirectory
};