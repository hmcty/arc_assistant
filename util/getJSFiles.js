const fs = require("fs");

const getJSFiles = function (dirPath, commandFiles) {
  const dirItems = fs.readdirSync(dirPath);

  commandFiles = commandFiles || [];
  dirItems.forEach(function (file) {
    if (fs.statSync(dirPath + "/" + file).isDirectory()) {
      commandFiles = getJSFiles(dirPath + "/" + file, commandFiles);
    } else if (file.endsWith(".js")) {
      commandFiles.push(dirPath + "/" + file);
    }
  });
  return commandFiles;
};

module.exports = { getJSFiles };
