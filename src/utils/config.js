const fs = require('fs');
const os = require('os');
const path = require('path');

// Define the configuration file path
const CONFIG_PATH = path.join(os.homedir(), '.codethreatconfig.json');

/**
 * Retrieves the codethreat configuration.
 * 
 * The function first checks for a configuration file (~/.codethreatconfig.json).
 * If specific values are not found in the configuration file, it then looks for 
 * corresponding environment variables.
 * 
 * Environment variables checked:
 * - CODETHREAT_BASE_URL: Corresponds to the base URL of the codethreat platform.
 * - CODETHREAT_ORG_NAME: Corresponds to the organization name.
 * - CODETHREAT_ACCESS_TOKEN: Corresponds to the access token for codethreat.
 * 
 * @returns {Object} The configuration object which may be a combination of values 
 *                   from the file and environment variables.
 */
function getConfig() {
    let config = {};

    if (fs.existsSync(CONFIG_PATH)) {
        const rawData = fs.readFileSync(CONFIG_PATH, 'utf-8');
        config = JSON.parse(rawData);
    }

    // Check for environment variables if config values are missing
    if (!config.baseUrl) {
        config.baseUrl = process.env.CODETHREAT_BASE_URL;
    }

    if (!config.organizationName) {
        config.organizationName = process.env.CODETHREAT_ORG_NAME;
    }

    if (!config.ctAccessToken) {
        config.ctAccessToken = process.env.CODETHREAT_ACCESS_TOKEN;
    }

    return config;
}

/**
 * Saves the codethreat configuration.
 * @param {Object} config - The configuration object to save.
 */
function setConfig(config) {
    const data = JSON.stringify(config, null, 2);
    fs.writeFileSync(CONFIG_PATH, data);
}

module.exports = {
    getConfig,
    setConfig
};