const chai = require('chai');
const fs = require('fs');
const { zipDirectory } = require('../../src/utils/zip');

const expect = chai.expect;

describe('zipDirectory', () => {
  it('should create a zip file of the specified directory', async () => {
    const zipPath = await zipDirectory('test/sampleDir');
    
    // Check that the zip file exists
    expect(fs.existsSync(zipPath)).to.be.true;

    // Cleanup: Delete the created zip file
    //fs.unlinkSync(zipPath);
  });
});