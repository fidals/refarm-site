class TableEditorFilters {
  constructor(toggleFilterBtnText) {
    this.defaultToggleFilterBtnText = {
      show: 'Show filters',
      hide: 'Hide filters',
    };
    this.toggleFilterBtnText = toggleFilterBtnText || this.defaultToggleFilterBtnText;

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

    this.init();
  }

  setUpListeners() {
    this.DOM.$saveFiltersBtn.click(() => this.saveFilters());
    this.DOM.$resetFiltersBtn.click(() => this.dropFilters());
    this.DOM.$toggleFilterBtn.click(event => this.toggleFilters(event));
    this.DOM.$filterCheckbox.change(event => this.updateSortedFields(event));
  }

  init() {
    this.setUpListeners();
    this.setFiltersState();
    this.initFilters();
  }

  getSelectedFields() {
    return this.DOM.$filterCheckbox.filter((_, item) => $(item).is(':checked'));
  }

  updateSortedFields(event) {
    const $target = $(event.target);
    const filterName = $target.attr('id');
    const filterText = $target.prev().text();
    const $filterField = this.DOM.$sortableList.find(`.${this.DOM.sortableClass}`)
      .filter(`[data-name=${filterName}]`);

    if ($target.is(':checked')) {
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

  toggleFilters(event) {
    const $target = $(event.target);

    if (this.DOM.$filterWrapper.is(':visible')) {
      $target.html(this.toggleFilterBtnText.show);
      localStorage.setItem(this.storageKeys.isFilterVisible, 'false');
    } else {
      $target.html(this.toggleFilterBtnText.hide);
      localStorage.setItem(this.storageKeys.isFilterVisible, 'true');
    }

    this.DOM.$filterWrapper.slideToggle();
  }

  clearCheckboxes() {
    $.each(this.DOM.$filterCheckbox, (_, item) => $(item).prop('checked', false));
  }

  setFiltersState() {
    if (localStorage.getItem(this.storageKeys.isFilterVisible) === 'true') {
      this.DOM.$toggleFilterBtn.html(this.toggleFilterBtnText.hide);
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
      fieldsHtml = this.renderDefaultFilters();
    }

    this.DOM.$sortableList
      .html(fieldsHtml)
      .sortable({
        placeholder: 'sortable-item ui-state-highlight',
      })
      .disableSelection();
  }

  renderDefaultFilters() {
    return $.map(this.getSelectedFields(), (item) => {
      const id = $(item).attr('id');
      const text = $(item).prev().text();

      return `
        <li class="sortable-item ${this.DOM.sortableClass}" data-name="${id}">${text}</li>
      `;
    }).join('');
  }

  renderCustomFilters(storedFields) {
    const fields = JSON.parse(storedFields);

    return fields.reduce((prev, next) => {
      const $inputToCheck = $(`#${next}`);
      const filterText = $inputToCheck.prev().text();
      $inputToCheck.prop('checked', true);

      return `
        ${prev}
        <li class="sortable-item ${this.DOM.sortableClass} ui-sortable-handle" data-name="${next}">
          ${filterText}
        </li>
      `;
    }, '');
  }
}
