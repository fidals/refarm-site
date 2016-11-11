class TableEditor {
  constructor(colModel = TableEditorColumnModel(), modals = TableEditorDialogBoxes()) {
    this.DOM = {
      $: $('#jqGrid'),
    };

    this.$searchField = $('#search-field');
    this.wasFiltered = false;
    this.lastSelectedRowId = undefined;
    this.lastSelectedData = {
      id: 0,
      cellIndex: 0,
      fullData: {},
    };

    this.jsTreeSearchKey = 'search_term';

    this.jqGridSettings = {
      url: '/admin/table-editor-api/',
      editurl: 'clientArray',
      styleUI: 'Bootstrap',
      altRows: true,
      altclass: 'jqgrid-secondary',
      autoencode: true,
      datatype: 'json',
      colModel: colModel.getSettings(),
      loadonce: true,
      viewrecords: true,
      width: 1400,
      height: 500,
      rowNum: 30,
      pager: '#jqGridPager',
      onSelectRow: this.editRow.bind(this),
      onCellSelect: this.collectCellData.bind(this),
      loadComplete: this.afterLoad.bind(this),
    };

    this.filterFields = [
      'name',
      'category_name',
      'price',
      'purchase_price',
    ];

    this.modals = modals;

    this.init();
  }

  init() {
    this.setUpListeners();
    this.DOM.$.jqGrid(this.jqGridSettings);
  }

  setUpListeners() {
    this.$searchField.on('keyup', this.searchInTable.bind(this));
    this.modals.DOM.modalToDeleteProduct.$acceptBtn.click(this.deleteProduct.bind(this));
  }

  /**
   * Afterload event of jQgrid.
   * @link http://goo.gl/5WwmTm
   */
  afterLoad() {
    this.filterTableBySearchQuery();
  }

  /**
   * Edit selected row.
   * @param lastSelectedRowId - need for resetting edit mode for previous row;
   * @param rowId - id of selected row;
   */
  editRow(rowId) {
    this.DOM.$.jqGrid('restoreRow', this.lastSelectedRowId);

    // Cancel method by click on delete Product icon:
    if ($(event.target).hasClass(
        tableEditorDialogBoxes.DOM.modalToDeleteProduct.deleteProductBtnClass)) return;

    const self = this;
    this.DOM.$.jqGrid('editRow', rowId, {
      keys: true,
      focusField: this.lastSelectedData.cellIndex,
      aftersavefunc() {
        self.updateProduct(self);
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
   * @param key - request's key
   */
  getSearchValue(key) {
    const searchQuery = decodeURIComponent(document.location.search).slice(1).split('&');
    const splitedPairs = searchQuery.map(item => item.split('='));
    const [[_, searchTerm]] = splitedPairs.filter(item => item.includes(key));

    return searchTerm;
  }

  filterTableBySearchQuery() {
    if (this.wasFiltered) return;
    const hasUrlSearchKey = requestKey => document.location.search.indexOf(requestKey) !== -1;

    if (hasUrlSearchKey(this.jsTreeSearchKey)) {
      const searchTerm = this.getSearchValue(this.jsTreeSearchKey);

      this.$searchField
        .val(searchTerm)
        .focus()
        .trigger('keyup');

      this.wasFiltered = true;
    }
  }

  /**
   * Filter table data by live search on client side.
   * We should to generate `filter.rules` cause filters for search is dynamic.
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

    for (const field of this.filterFields) {
      if ($(`#jqGrid_${field}`).size() > 0) {
        filter.rules.push({
          field,
          op: 'cn',
          data: searchText,
        });
      }
    }

    setTimeout(() => {
      this.DOM.$[0].p.search = filter.rules.length > 0;
      $.extend(this.DOM.$[0].p.postData, {
        filters: JSON.stringify(filter),
      });

      this.DOM.$.trigger('reloadGrid', [{ page: 1 }]);
    }, 200);
  }

  /**
   * Update Product on server only if row was changed.
   */
  updateProduct(self) {
    const newRowData = this.getRowData(this.lastSelectedData.id);
    const isNotChanged = JSON.stringify(this.lastSelectedData.fullData) === JSON.stringify(newRowData);

    if (isNotChanged) return;

    const $currentRow = $(`#${this.lastSelectedData.id}`);

    $.ajax({
      url: this.jqGridSettings.url,
      type: 'PUT',
      data: this.destructFields(newRowData),
      success: () => {
        $currentRow.removeClass('danger');
      },
      error: (XHR, status, err) => {
        try {
          const {field, message} = JSON.parse(XHR.responseText);
          tableEditorDialogBoxes.showPopover($currentRow, field, message);
        } catch (e) {
          console.warn(status, err);
        }
        $currentRow.addClass('danger');
      },
    });
  }

  deleteProduct(event) {
    event.stopImmediatePropagation();
    $.ajax({
      url: this.jqGridSettings.url,
      type: 'DELETE',
      data: {id: this.lastSelectedData.id},
      success: () => {
        this.modals.closeModal(event, this.modals.DOM.modalToDeleteProduct.$);
        this.DOM.$.jqGrid('delRowData', this.lastSelectedData.id);
      },
    });
  }

  /**
   * Return trimmed fields from newRowData for ajax data arguments.
   */
  destructFields(newRowData) {
    const trimmedData = {};

    for (const [key, value] of Object.entries(newRowData)) {
      if (key && key !== 'undefined' ) trimmedData[key] = value.trim();
    }

    return trimmedData;
  }
}
