const axios = require('axios');
const { getConfig } = require('../utils/config');

/**
 * Fetches a project.
 *
 * @param {string} projectName - Name of the project to fetch.
 * @returns {Promise<object>} The project data.
 */
async function getProject(projectName) {
    const config = getConfig();
    try {
      const response = await axios.get(`${config.baseUrl}/api/project?key=${projectName}`, {
        headers: {
          'authorization': `Bearer ${config.ctAccessToken}`,
          'x-ct-organization': `${config.organizationName}`
        }
      });
  
      if (response.status !== 200) {
        throw new Error('Project not found or error retrieving project.');
      }
      return response.data;
    } catch (error) {
      throw error; 
    }
  }

/**
 * Creates a new project.
 *
 * @param {string} projectName - Name of the new project.
 * @returns {Promise<object>} The created project data.
 */
async function createProject(projectName) {
  const config = getConfig();
  var postdata = `{    
      "project_name": "${projectName}",
            "type": "upload",
            "branch": ""

        }`;
    try {

        
        const response = await axios.post(`${config.baseUrl}/api/project/add`, postdata, {
            headers: {
                'authorization': `Bearer ${config.ctAccessToken}`,
                'x-ct-organization': `${config.organizationName}`
            }
        });
        return response.data;
    } catch (error) {
        throw error; 

    }
 
}

module.exports = {
  getProject,
  createProject
};