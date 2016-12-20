class TableEditorColModel {
  constructor(customColModels = [], filters) {
    this.defaultColModels = [
      {
        name: 'id',
        label: 'ID',
        key: true,
        sorttype: 'integer',
        width: 30,
      },
      {
        name: 'name',
        label: 'Name',
        editable: true,
        editrules: {
          required: true,
        },
        width: 120,
      },
      {
        name: 'category_name',
        label: 'Category name',
        editable: true,
        editoptions: {
          dataInit(elem) {
            autocomplete.category(elem);
          },
        },
        width: 120,
      },
      {
        name: 'category_id',
        hidden: true,
      },
      {
        name: 'price',
        label: 'Price',
        editable: true,
        editoptions: {
          type: 'number',
          step: '1.00',
          min: '0.00',
          pattern: '[0-9]',
        },
        editrules: {
          minValue: 0,
          required: true,
          number: true,
        },
        formatter: 'currency',
        formatoptions: {
          decimalSeparator: '.',
          thousandsSeparator: ' ',
          prefix: '₽ ',
        },
        sorttype: 'integer',
        width: 30,
      },
      {
        name: 'in_stock',
        label: 'In stock',
        editable: true,
        editoptions: {
          type: 'number',
          step: '1',
          min: '0',
          pattern: '[0-9]',
        },
        editrules: {
          minValue: 0,
          number: true,
        },
        formatter: 'integer',
        sorttype: 'integer',
        width: 30,
      },
      {
        name: 'is_popular',
        label: 'Is popular',
        align: 'center',
        editable: true,
        editoptions: { value: '1:0' },
        edittype: 'checkbox',
        formatter: 'checkbox',
        width: 35,
      },
      {
        name: 'page_title',
        label: 'Title',
        editable: true,
        width: 150,
      },
      {
        name: 'page_position',
        label: 'Position',
        editable: true,
        editoptions: {
          type: 'number',
          step: '1.00',
          min: '0.00',
          pattern: '[0-9]',
        },
        editrules: {
          minValue: 0,
          number: true,
        },
        sorttype: 'integer',
        width: 50,
      },
      {
        name: 'page_h1',
        label: 'H1',
        editable: true,
        width: 150,
      },
      {
        name: 'page_keywords',
        label: 'Keywords',
        editable: true,
        width: 150,
      },
      {
        name: 'page_description',
        label: 'Description',
        editable: true,
        width: 150,
      },
      {
        name: 'page_seo_text',
        label: 'Seo text',
        editable: true,
        width: 150,
      },
      {
        name: 'page_name',
        editable: true,
        editrules: {
          required: true,
        },
        width: 150,
      },
      {
        name: 'page_menu_title',
        label: 'Menu title',
        editable: true,
        width: 150,
      },
      {
        name: 'page_is_active',
        label: 'Is active',
        align: 'center',
        editable: true,
        editoptions: { value: '1:0' },
        edittype: 'checkbox',
        formatter: 'checkbox',
        width: 44,
      },
      {
        name: 'removeTag',
        label: '<div class="text-center"><i class="fa fa-2x fa-trash-o"></i></div>',
        align: 'center',
        formatter: 'removeTag',
        sortable: false,
        width: 20,
      },
      {
        name: 'linksTag',
        label: 'Links',
        align: 'center',
        formatter: 'linksTag',
        sortable: false,
        width: 30,
      },
    ];

    this.colModels = this.mergeColModels(customColModels);
    this.filters = filters || new TableEditorFilters();
  }

  mergeColModels(customColModel) {
    return this.defaultColModels
      .filter(col => customColModel.every(customCol => customCol !== col.name))
      .concat(customColModel);
  }

  /**
   * Get jQgrid localStorage or default settings.
   * Depends on Filters.
   */
  getSettings() {
    const customFieldNames = this.getCustomFieldNames();
    const fieldNames = customFieldNames || this.getStandardFieldNames();

    return this.generateSettings(fieldNames);
  }

  static getCheckedFieldNames($checkboxes) {
    return $checkboxes.map(item => item.replace('filter-', ''));
  }

  getCustomFieldNames() {
    const storedFilters = localStorage.getItem(this.filters.storageKeys.filterFieldsPreset);
    if (storedFilters === null) return null;

    return TableEditorColModel.getCheckedFieldNames(JSON.parse(storedFilters));
  }

  getStandardFieldNames() {
    const checkboxIds = $.map(this.filters.getSelectedFields(), item => $(item).attr('id'));
    return TableEditorColModel.getCheckedFieldNames(checkboxIds);
  }

  getFieldByName(name) {
    return this.colModels.filter(field => field.name === name)[0];
  }

  generateSettings(colNames) {
    const generatedSettings = colNames
      .filter(col => this.getFieldByName(col))
      .map(col => this.getFieldByName(col));

    // We always show `id` as first column.
    // And `linksTag`, `removeTag` as last ones.
    generatedSettings.unshift(this.getFieldByName('id'));
    generatedSettings.push(this.getFieldByName('linksTag'));
    generatedSettings.push(this.getFieldByName('removeTag'));

    return generatedSettings;
  }
}
