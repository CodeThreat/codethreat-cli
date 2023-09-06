const chai = require('chai');
const { getConfig, setConfig } = require('../../src/utils/config');

const expect = chai.expect;

describe('config utilities', () => {
  it('should store and retrieve configuration', () => {
    const testConfig = {
      baseUrl: 'https://test.com',
      organizationName: 'TestOrg',
      ctAccessToken: 'testToken'
    };

    //setConfig(testConfig);

    const retrievedConfig = getConfig();
    expect(retrievedConfig).to.deep.equal(testConfig);
  });
});
