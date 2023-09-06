const chai = require('chai');
const nock = require('nock');
const { getProject, createProject } = require('../../src/api/project');

const expect = chai.expect;

describe('project API', () => {
  it('should fetch a project', async () => {
    const mockResponse = { id: '1', name: 'TestProject' };

    nock('https://api.example.com')
      .get('/project-endpoint')
      .reply(200, mockResponse);

    const project = await getProject('TestProject');
    expect(project).to.deep.equal(mockResponse);
  });

  it('should create a project', async () => {
    const mockResponse = { id: '1', name: 'NewProject' };

    nock('https://api.example.com')
      .post('/project-endpoint')
      .reply(200, mockResponse);

    const project = await createProject('NewProject');
    expect(project).to.deep.equal(mockResponse);
  });
});