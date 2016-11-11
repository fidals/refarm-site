/**
 * Return absolute path for requested file.
 */
const getAbsPath = fileName => `${__dirname}/${fileName}`;
const getAbsPaths = fileNames => fileNames.map(getAbsPath);

module.exports = {
  admin: getAbsPaths([
    'js/components/plugins.es6',
    'js/components/sidebar.es6',
    'js/components/tableEditor/dialogBoxes.es6',
    'js/components/tableEditor/filters.es6',
    'js/components/tableEditor/colModels.es6',
    'js/components/tableEditor/jqGrid.es6',
  ]),
  vendors: getAbsPaths([
    'js/vendors/jquery-2.2.3.min.js',
    'js/vendors/js.cookie.js',
    'js/vendors/autocomplete.min.js',
    'js/vendors/jquery-ui.min.js',
    'js/vendors/jquery.slimscroll.min.js',
    'js/vendors/jqGrid.locale-ru.js',
    'js/vendors/jqGrid.min.js',
    'js/vendors/jquery.webui-popover.min.js',
    'js/vendors/jstree.min.js',
  ]),
  watch: getAbsPath('js/**/*'),
  css: getAbsPath('css/*'),
  img: getAbsPath('imgages/**/*'),
};
