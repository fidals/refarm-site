class TableEditor {
  constructor(colModel, dialogs) {
    this.autocomplete = new TableEditorAutocomplete();
    this.colModel = colModel || new TableEditorColModel();
    this.dialogs = dialogs || new TableEditorDialogs();

    this.DOM = {
      $: $('#jqGrid'),
      redirectToLinks: '.js-to-site-page, .js-to-admin-page',
      $newEntityForm: $('#add-entity-form'),
      $newEntityTitle: $('#add-entity-title'),
      $newEntityTitleSuccess: $('#add-entity-title-success'),
      $modalCategoryInput: $('#entity-category'),
      $modalFields: $('.js-new-entity'),
      $modalRequiredFields: $('.js-required'),
      $modalSaveBtn: $('#entity-save'),
      $modalRefreshBtn: $('#refresh-table'),
    };

    this.urls = {
      jqGrid: '/admin/table-editor-api/',
      redirectToProduct: '/admin/redirect-to-product/',
    };

    this.excludedUpdateFields = ['removeTag', 'linksTag'];
    this.$searchField = $('#search-field');
    this.$searchClear = $('#search-clear');
    this.wasFiltered = false;
    this.lastSelectedRowId = 0;
    this.lastSelectedData = {
      id: 0,
      cellIndex: 0,
      fullData: {},
    };

    this.jsTreeSearchKey = 'search_term';

    // https://goo.gl/ZvxxoP
    this.jqGridSettings = {
      url: this.urls.jqGrid,
      editurl: 'clientArray',
      styleUI: 'Bootstrap',
      regional: 'ru',
      altRows: true,
      altclass: 'jqgrid-secondary',
      autoencode: true,
      datatype: 'json',
      colModel: this.colModel.getSettings(),
      loadonce: true,
      viewrecords: true,
      width: 1400,
      height: 500,
      rowNum: 30,
      onSelectRow: rowId => this.editRow(rowId),
      onCellSelect: (...data) => this.collectCellData(...data),
      loadComplete: () => this.afterLoad(),
    };

    this.filterFields = [
      'name',
      'category_name',
      'price',
    ];

    this.init();
  }

  init() {
    this.initUtilities();
    this.setUpListeners();
    this.setupFormatter();
    this.DOM.$.jqGrid(this.jqGridSettings);
  }

  initUtilities() {
    this.autocomplete.category(this.DOM.$modalCategoryInput);
  }

  setUpListeners() {
    $(document).on('click', `${this.DOM.redirectToLinks}`, event => this.redirectTo(event));
    this.DOM.$modalRequiredFields.on('keyup', () => this.setCreateBtnState());
    this.DOM.$modalSaveBtn.click(() => this.saveNewEntity());
    this.DOM.$modalRefreshBtn.click(() => this.refreshTable());
    this.dialogs.deleteDialog.$acceptBtn.click(event => this.deleteProduct(event));
    this.$searchField.on('keyup', () => this.searchInTable());
    this.$searchClear.click(() => this.clearSearch());
  }

  setupFormatter() {
    $.extend($.fn.fmatter, {
      removeTag: () => {
        return `
          <i class="jqgrid-remove-icon fa fa-2x fa-trash-o
            ${this.dialogs.deleteDialog.deleteClass}"
            title="Delete product" data-toggle="modal" data-target="#remove-modal"></i>
        `;
      },
      linksTag() {
        return `
          <div class="btn-group" role="group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"
              aria-haspopup="true" aria-expanded="false">
              <i class="fa fa-link" aria-hidden="true"></i>
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu dropdown-menu-right table-editor-links-list">
              <li><a class="js-to-site-page">Look on site page</a></li>
              <li><a class="js-to-admin-page">Look on admin page</a></li>
            </ul>
          </div>
        `;
      },
    });
  }

  /**
   * Afterload events for jqGrid.
   * @link http://goo.gl/5WwmTm
   */
  afterLoad() {
    this.filterTableBySearchQuery();
  }

  /**
   * Edit selected row.
   * lastSelectedRowId - need for resetting edit mode for previous row;
   * @param rowId - id of selected row;
   */
  editRow(rowId) {
    this.DOM.$.jqGrid('restoreRow', this.lastSelectedRowId);

    // Cancel method by click on delete Product icon:
    if (event && $(event.target).hasClass(
        this.dialogs.deleteDialog.deleteClass)) return;

    const self = this;
    this.DOM.$.jqGrid('editRow', rowId, {
      keys: true,
      focusField: this.lastSelectedData.cellIndex,
      aftersavefunc() {
        self.updateProduct();
      },
    });

    this.lastSelectedRowId = rowId;
  }

  getRowData(rowId) {
    return this.DOM.$.jqGrid('getRowData', rowId);
  }

  /**
   * Collect data for selected row with cell index.
   * @param rowId;
   * @param cellIndex;
   */
  collectCellData(rowId, cellIndex) {
    const $parentRow = $(event.target).closest('.jqgrow');
    const isInEditMode = Boolean($parentRow.find('.inline-edit-cell').size());

    if (!isInEditMode) {
      this.lastSelectedData.id = rowId;
      this.lastSelectedData.cellIndex = cellIndex;
      this.lastSelectedData.fullData = this.getRowData(rowId);
    }
  }

  /**
   * Get request search value from url.
   */
  getSearchValue() {
    const searchString = decodeURIComponent(document.location.search).slice(1);
    return searchString.replace(`${this.jsTreeSearchKey}=`, '');
  }

  filterTableBySearchQuery() {
    if (this.wasFiltered) return;
    const hasUrlSearchKey = key => document.location.search.includes(key);

    if (hasUrlSearchKey(this.jsTreeSearchKey)) {
      const searchTerm = this.getSearchValue();

      this.$searchField
        .val(searchTerm)
        .focus()
        .trigger('keyup');

      this.wasFiltered = true;
    }
  }

  /**
   * Filter table data by live search on client side.
   * We should to generate `filter.rules` because filters search is dynamic.
   * @link http://goo.gl/NFoUvf
   */
  searchInTable() {
    const searchText = this.$searchField.val();
    const filter = {
      groupOp: 'OR',
      rules: [{
        field: 'id',
        op: 'cn',
        data: searchText,
      }],
    };

    this.filterFields.map((field) => {
      if ($(`#jqGrid_${field}`).size()) {
        filter.rules.push({
          field,
          op: 'cn',
          data: searchText,
        });
      }

      return filter.rules;
    });

    setTimeout(() => {
      this.DOM.$[0].p.search = filter.rules.length > 0;
      $.extend(this.DOM.$[0].p.postData, {
        filters: JSON.stringify(filter),
      });

      this.DOM.$.trigger('reloadGrid', [{ page: 1 }]);
    }, 200);
  }

  clearSearch() {
    this.$searchField.val('');
  }

  /**
   * Update Product on server only if it was changed.
   */
  updateProduct() {
    const newRowData = this.getRowData(this.lastSelectedData.id);
    const isChanged = JSON.stringify(this.lastSelectedData.fullData) !== JSON.stringify(newRowData);
    if (!isChanged) return;

    const $currentRow = $(`#${this.lastSelectedData.id}`);

    $.ajax({
      url: this.urls.jqGrid,
      type: 'PUT',
      data: this.prepareFieldsForUpdate(newRowData),
      success: () => {
        $currentRow.removeClass('danger');
      },
      error: (XHR, status, err) => {
        try {
          const { field, message } = JSON.parse(XHR.responseText);
          this.dialogs.showPopover($currentRow, field, message);
        } catch (e) {
          console.warn(status, err);
        }
        $currentRow.addClass('danger');
      },
    });
  }

  deleteProduct(event) {
    event.stopPropagation();
    $.ajax({
      url: this.urls.jqGrid,
      type: 'DELETE',
      data: { id: this.lastSelectedData.id },
      success: () => {
        this.dialogs.deleteDialog.$.removeClass('modal-show');
        this.DOM.$.jqGrid('delRowData', this.lastSelectedData.id);
      },
    });
  }

  /**
   * Return trimmed fields from newRowData for ajax data arguments.
   */
  prepareFieldsForUpdate(newRowData) {
    const trimmedData = {};

    Object.keys(newRowData).forEach((key) => {
      if (this.excludedUpdateFields.every(field => field !== key)) {
        trimmedData[key] = newRowData[key].trim();
      }
    });

    return trimmedData;
  }

  redirectTo(event) {
    $.get(this.urls.redirectToProduct, {
      id: this.lastSelectedData.id,
      tosite: $(event.target).hasClass('js-to-site-page') ? 1 : 0,
    }).success((url) => {
      window.location.assign(url);
    });
  }

  setCreateBtnState() {
    const isActive = Array.from(this.DOM.$modalRequiredFields)
      .every(item => $(item).val() !== '');
    this.DOM.$modalSaveBtn.attr('disabled', !isActive);
  }

  saveNewEntity() {
    const getValue = value => this.DOM.$modalFields.filter(`#entity-${value}`).val();
    const data = {
      name: getValue('name'),
      category: getValue('category'),
      price: getValue('price'),
    };

    $.ajax({
      url: this.urls.jqGrid,
      type: 'POST',
      data,
      success: () => {
        this.setRefreshBtnState(false);
        this.afterEntitySaveCallback();
      },
      error: XHR => console.warn(XHR),
    });
  }

  afterEntitySaveCallback() {
    this.DOM.$newEntityForm.find('input').each((_, item) => $(item).val(''));
    this.DOM.$modalSaveBtn.attr('disabled', true);
    this.DOM.$newEntityTitleSuccess.addClass('active');
    setTimeout(() => {
      this.DOM.$newEntityTitleSuccess.removeClass('active');
    }, 2000);
  }

  setRefreshBtnState(value) {
    this.DOM.$modalRefreshBtn.attr('disabled', value);
  }

  refreshTable() {
    $.get(this.urls.jqGrid).then((response) => {
      this.DOM.$.jqGrid('setGridParam', { data: response }).trigger('reloadGrid');
    });
  }
}
