/**
 * Return absolute path for requested file.
 */
const getAbsPath = fileName => `${__dirname}/${fileName}`;

module.exports = {
  backcall: getAbsPath('backcall.es6'),
  trackers: getAbsPath('trackers.es6'),
  watch: getAbsPath('*.es6'),
};
