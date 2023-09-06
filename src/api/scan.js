const axios = require('axios');
const { getConfig } = require('../utils/config');
const fs = require('fs-extra');
const FormData = require('form-data');

/**
 * Starts a scan for a project.
 *
 * @param {string} projectName - Name of the project to scan.
 * @param {string} zipFilePath - Path to the zipped target directory.
 * @returns {Promise<object>} Scan status.
 */
async function startScan(projectName, zipFilePath) {
    try {
            const config = getConfig();
        const formData = new FormData();
            formData.append('upfile', fs.createReadStream(zipFilePath), {
            filename: 'target.zip',
            contentType: 'application/zip',
            });

        formData.append('project', `${projectName}`);

        const response = await axios.post(`${config.baseUrl}/api/scan/start`, formData, {
            headers: {
            'authorization': `Bearer ${config.ctAccessToken}`,
            'x-ct-organization': `${config.organizationName}`,
            ...formData.getHeaders()
            } 
    });

  return response.data;
    } catch (error) {
        throw new Error(`Failed to start the scan: ${error.message}`);

    }
  
}

/**
 * Fetches the progress of a scan.
 *
 * @param {string} scanId - ID of the scan to fetch progress for.
 * @returns {Promise<object>} Scan progress data.
 */
async function getScanProgress(scanId) {
    try {
        const config = getConfig();
        const response = await axios.get(`${config.baseUrl}/api/scan/status/${scanId}`, {
          headers: {
            'authorization': `Bearer ${config.ctAccessToken}`,
            'x-ct-organization': `${config.organizationName}`
          }
        });
        return response.data;
    } catch (error) {
        throw new Error(`Failed to fetch the scan progress: ${error.message}`);

    }
 
}

module.exports = {
  startScan,
  getScanProgress
};