class TableEditor {
  constructor(colModel = TableEditorColumnModel(), dialogBoxes = TableEditorDialogBoxes()) {
    this.DOM = {
      $: $('#jqGrid'),
      redirectToLinks: '.js-to-site-page, .js-to-admin-page',
    };

    this.urls = {
      jqGrid: '/admin/table-editor-api/',
      redirectToProduct: '/admin/redirect-to-product/',
    };

    this.excludedFieldForUpdate = ['removeTag', 'linksTag'];
    this.$searchField = $('#search-field');
    this.wasFiltered = false;
    this.lastSelectedRowId = undefined;
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
      regional : 'ru',
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
      onSelectRow: (rowId) => this.editRow(rowId),
      onCellSelect: (...data) => this.collectCellData(...data),
      loadComplete: () => this.afterLoad(),
    };

    this.filterFields = [
      'name',
      'category_name',
      'price',
    ];

    this.dialogBoxes = dialogBoxes;

    this.init();
  }

  init() {
    this.setUpListeners();
    this.setupFormatter();
    this.DOM.$.jqGrid(this.jqGridSettings);
  }

  setUpListeners() {
    this.$searchField.on('keyup', () => this.searchInTable());
    this.dialogBoxes.modalToDeleteProduct.$acceptBtn.click(event => this.deleteProduct(event));
    $(document).on('click', `${this.DOM.redirectToLinks}`, event => this.redirectTo(event));
  }

  setupFormatter() {
    $.extend($.fn.fmatter, {
      removeTag: () => {
        return `
          <i class="jqgrid-remove-icon fa fa-2x fa-trash-o
            ${this.dialogBoxes.modalToDeleteProduct.deleteProductBtnClass}"
            title="Delete product" data-toggle="modal" data-target="#remove-modal"></i>
        `;
      },
      linksTag: () => {
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
        this.dialogBoxes.modalToDeleteProduct.deleteProductBtnClass)) return;

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
      data: this.prepareFieldsForUpdate(newRowData),
      success: () => {
        $currentRow.removeClass('danger');
      },
      error: (XHR, status, err) => {
        try {
          const {field, message} = JSON.parse(XHR.responseText);
          this.dialogBoxes.showPopover($currentRow, field, message);
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
      data: { id: this.lastSelectedData.id },
      success: () => {
        this.dialogBoxes.closeModal(event, this.dialogBoxes.modalToDeleteProduct.$);
        this.DOM.$.jqGrid('delRowData', this.lastSelectedData.id);
      },
    });
  }

  /**
   * Return trimmed fields from newRowData for ajax data arguments.
   */
  prepareFieldsForUpdate(newRowData) {
    const trimmedData = {};

    for (const [key, value] of Object.entries(newRowData)) {
      if (this.excludedFieldForUpdate.every(field => field !== key)) trimmedData[key] = value.trim();
    }

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
}
