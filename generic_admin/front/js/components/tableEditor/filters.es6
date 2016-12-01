class TableEditorFilters {
  constructor() {
    this.DOM = {
      $sortableList: $('#sortable'),
      $filterWrapper: $('.js-filter-wrapper'),
      $filterCheckbox: $('.js-filter-checkbox'),
      $toggleFilterBtn: $('.js-hide-filter'),
      $saveFiltersBtn: $('.js-save-filters'),
      $resetFiltersBtn: $('.js-drop-filters'),
      sortableClass: 'js-sortable-item',
    };

    this.storageKeys = {
      isFilterVisible: 'isFilterVisible',
      filterFieldsPreset: 'filterFieldsPreset',
    };

    this.toggleFilterButtonTexts = {
      show: 'Show filters',
      hide: 'Hide filters',
    };

    this.init();
  }

  setUpListeners() {
    this.DOM.$saveFiltersBtn.click(() => this.saveFilters());
    this.DOM.$resetFiltersBtn.click(() => this.dropFilters());
    this.DOM.$toggleFilterBtn.click(() => this.toggleFilters());
    this.DOM.$filterCheckbox.change(() => this.updateSortedFields());
  }

  init() {
    this.setUpListeners();
    this.setFiltersState();
    this.initFilters();
  }

  getSelectedFields() {
    return this.DOM.$filterCheckbox.filter((_, item) => $(item).is(':checked'));
  }

  updateSortedFields() {
    const filterName = $(event.target).attr('id');
    const filterText = $(event.target).prev().text();
    const $filterField = this.DOM.$sortableList.find(`.${this.DOM.sortableClass}`)
      .filter(`[data-name=${filterName}]`);

    if ($(event.target).is(':checked')) {
      this.DOM.$sortableList.append(`
        <li class="sortable-item ${this.DOM.sortableClass}" data-name="${filterName}">
          ${filterText}
        </li>
      `);
    } else {
      $filterField.remove();
    }
  }

  saveFilters() {
    const fields = [];

    $.each($(`.${this.DOM.sortableClass}`), (_, item) => {
      fields.push($(item).attr('data-name'));
    });

    localStorage.setItem(this.storageKeys.filterFieldsPreset, JSON.stringify(fields));
    location.reload();
  }

  dropFilters() {
    localStorage.removeItem(this.storageKeys.filterFieldsPreset);
    location.reload();
  }

  toggleFilters() {
    const $target = $(event.target);

    if (this.DOM.$filterWrapper.is(':visible')) {
      $target.html(this.toggleFilterButtonTexts.show);
      localStorage.setItem(this.storageKeys.isFilterVisible, 'false');
    } else {
      $target.html(this.toggleFilterButtonTexts.hide);
      localStorage.setItem(this.storageKeys.isFilterVisible, 'true');
    }

    this.DOM.$filterWrapper.slideToggle();
  }

  clearCheckboxes() {
    $.each(this.DOM.$filterCheckbox, (_, item) => $(item).prop('checked', false));
  }

  setFiltersState() {
    if (localStorage.getItem(this.storageKeys.isFilterVisible) === 'true') {
      this.DOM.$toggleFilterBtn.html(this.toggleFilterButtonTexts.hide);
      this.DOM.$filterWrapper.slideToggle();
    }
  }

  initFilters() {
    const storedFields = localStorage.getItem(this.storageKeys.filterFieldsPreset);
    let fieldsHtml = '';

    if (storedFields) {
      this.clearCheckboxes();
      fieldsHtml = this.renderCustomFilters(storedFields);
    } else {
      fieldsHtml = this.renderStandardFilters();
    }

    this.DOM.$sortableList
      .html(fieldsHtml)
      .sortable({
        placeholder: 'sortable-item ui-state-highlight',
      })
      .disableSelection();
  }

  renderStandardFilters() {
    let fieldsHtml = '';

    for (const field of this.getSelectedFields()) {
      const id = $(field).attr('id');
      const text = $(field).prev().text();

      fieldsHtml += `
        <li class="sortable-item ${this.DOM.sortableClass}" data-name="${id}">${text}</li>
      `;
    }

    return fieldsHtml;
  }

  renderCustomFilters(storedFields) {
    const fields = JSON.parse(storedFields);
    let fieldsHtml = '';

    for (const field of fields) {
      const $inputToCheck = $(`#${field}`);
      const filterText = $inputToCheck.prev().text();

      $inputToCheck.prop('checked', true);
      fieldsHtml += `
        <li class="sortable-item ${this.DOM.sortableClass} ui-sortable-handle" data-name="${field}">
          ${filterText}
        </li>
      `;
    }

    return fieldsHtml;
  }
}
