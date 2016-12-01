class TableEditorColumnModel {
  constructor(filters = new TableEditorFilters(), customColumnModels = []) {
    this.columnModels = this.mergeColumnModels(customColumnModels);
    this.filters = filters;
  }

  getDefaultColumnModels() {
    return [
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
        width: 150,
      },
      {
        name: 'category_name',
        label: 'Category name',
        editable: true,
        editoptions: {
          dataInit(elem) {
            $(elem).autocomplete({
              source(request, response) {
                $.ajax({
                  type: 'GET',
                  url: '/admin/autocomplete/',
                  data: {
                    term: request.term,
                    pageType: 'category',
                  },
                  success(responseData) {
                    response(responseData);
                  },
                  error(jqXhr, textStatus, errorThrown) {
                    console.group('Autocomplete failed.');
                    console.log(jqXhr);
                    console.log(textStatus);
                    console.log(errorThrown);
                    console.groupEnd();
                  },
                });
              },
              // Set autocompleted value to input.
              select(_, ui) {
                $(elem).val(ui.item.label);
              },
            });
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
          required: true,
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
          required: true,
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
        label: '<div class="text-center"><i class="fa fa-link"></i></div>',
        align: 'center',
        formatter: 'linksTag',
        sortable: false,
        width: 30,
      },
    ];
  }

  mergeColumnModels(customColumnModel) {
    return this.getDefaultColumnModels()
      .filter(col => customColumnModel.every(customCol => customCol !== col.name))
      .concat(customColumnModel);
  }

  /**
   * Get jQgrid settings from localStorage or return default.
   * Depends on Filters.
   */
  getSettings() {
    const customFieldNames = this.getCustomFieldNames();
    const fieldNames = customFieldNames ? customFieldNames : this.getStandardFieldNames();

    return this.generateSettings(fieldNames);
  }

  getCheckedFieldNames($checkboxes) {
    return $checkboxes.map(item => item.replace('filter-', ''));
  }

  getCustomFieldNames() {
    const storedFilters = localStorage.getItem(this.filters.storageKeys.filterFieldsPreset);
    if (storedFilters === null) return null;

    return this.getCheckedFieldNames(JSON.parse(storedFilters));
  }

  getStandardFieldNames() {
    const checkboxIds = $.map(this.filters.getSelectedFields(), item => $(item).attr('id'));
    return this.getCheckedFieldNames(checkboxIds);
  }

  getFieldByName(name, fields) {
    return fields.filter(field => field.name === name)[0];
  }

  generateSettings(colNames) {
    const generatedSettings = colNames
      .map(col => this.getFieldByName(col, this.columnModels));

    // We always show id and tags columns.
    generatedSettings.unshift(this.getFieldByName('id', this.columnModels));
    generatedSettings.push(this.getFieldByName('linksTag', this.columnModels));
    generatedSettings.push(this.getFieldByName('removeTag', this.columnModels));

    return generatedSettings;
  }
}
