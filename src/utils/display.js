const chalk = require('chalk');

function displayScanProgress(progressData) {
    console.log(chalk.bold.green('Scan Progress:'));
    console.log(chalk.yellow('Severities:'));
    for (const [severity, count] of Object.entries(progressData.severities)) {
      console.log(`  ${chalk.cyan(severity)}: ${chalk.magenta(count)}`);
    }
  }
function displayProjectInfo(project) {
    console.log(chalk.bold.underline("Project Information"));
    console.log(chalk.green(`Name: ${project.project_name}`));
    console.log(chalk.green(`Owner: ${project.owner}`));
    console.log(chalk.green(`Created by: ${project.created_by}`));
    console.log(chalk.green(`Created at: ${project.created_at}`));
    console.log(chalk.green(`Type: ${project.type}`));
    console.log(chalk.green(`Total LOC: ${project.total_loc}`));
    console.log(chalk.green(`Total Files: ${project.total_files}`));
    console.log(chalk.green(`Open Issues: ${project.open_issue}`));
    console.log(chalk.green(`Closed Issues: ${project.closed_issue}`));
    console.log(chalk.green(`Description: ${project.description || "N/A"}`));

    console.log(chalk.bold.underline("\nIntegrations"));
    for (const [key, value] of Object.entries(project.integrations)) {
        if (value.type) {
            console.log(chalk.cyan(`- ${key.charAt(0).toUpperCase() + key.slice(1)}: ${value.type}`));
        }
    }

    console.log(chalk.bold.underline("\nTeam Members"));
    project.team.forEach(member => {
        console.log(chalk.magenta(`- ${member}`));
    });
}

module.exports = {
    displayProjectInfo,
    displayScanProgress
};