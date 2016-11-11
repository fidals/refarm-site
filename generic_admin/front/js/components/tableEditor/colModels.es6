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
        label: 'Название',
        editable: true,
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'category_name',
        label: 'Категория',
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
        width: 150,
      },
      {
        name: 'category_id',
        hidden: true,
      },
      {
        name: 'price',
        label: 'Цена',
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
        width: 50,
      },
      {
        name: 'in_stock',
        label: 'Наличие',
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
        width: 40,
      },
      {
        name: 'is_popular',
        label: 'Топ',
        align: 'center',
        editable: true,
        editoptions: { value: '1:0' },
        edittype: 'checkbox',
        formatter: 'checkbox',
        width: 42,
      },
      {
        name: 'page_title',
        label: 'Title',
        editable: true,
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'page_position',
        label: 'Позиция',
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
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'page_keywords',
        label: 'Ключевые слова',
        editable: true,
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'page_description',
        label: 'Описание',
        editable: true,
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'page_seo_text',
        label: 'СЕО текст',
        editable: true,
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'page_name',
        editable: true,
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'page_menu_title',
        label: 'Название в крошках',
        editable: true,
        editrules: {
          required: true,
        },
        width: 200,
      },
      {
        name: 'page_is_active',
        label: 'Активность',
        align: 'center',
        editable: true,
        editoptions: { value: '1:0' },
        edittype: 'checkbox',
        formatter: 'checkbox',
        width: 44,
      },
      {
        label: '<div class="text-center"><i class="fa fa-2x fa-trash-o"</i></div>',
        align: 'center',
        formatter: 'removeTag',
        sortable: false,
        width: 30,
      },
    ];
  }

  mergeColumnModels(customColumnModel) {
    const [rowId, ...filteredColumns] = this.getDefaultColumnModels.call(this)
      .filter((col) => {
        for (let customCol of customColumnModel) {
          if (customCol.name === col.name) return false;
        }
        return true;
      });
    // RowId should be a first in jqGrid and removalTag last.
    return [rowId].concat(customColumnModel, filteredColumns)
  }

  /**
   * Get jQgrid settings from localStorage or default.
   * Has dependence on Filters.
   */
  getSettings() {
    const storedFilters = localStorage.getItem(this.filters.storageKeys.filterFieldsPreset);
    const fieldNames = storedFilters ?
      this.getCustomFieldNames(storedFilters) : this.getStandardFieldNames();

    return this.generateSettings(fieldNames);
  }

  /**
   * Return checked filters field names.
   */
  getFieldNames($checkboxes) {
    return $checkboxes.map(item => item.replace('filter-', ''));
  }

  getCustomFieldNames(storedFilters) {
    return this.getFieldNames(JSON.parse(storedFilters));
  }

  getStandardFieldNames() {
    const checkboxIds = [];
    const $checkboxes = this.filters.getCheckedCheckboxes();
    $.each($checkboxes, (_, item) => checkboxIds.push($(item).attr('id')));

    return this.getFieldNames(checkboxIds);
  }

  /**
   * Generate settings from colModel object.
   * @param fieldNames - filter checked names
   */
  generateSettings(fieldNames) {
    const allSettings = this.columnModels;
    const generatedSettings = [];

    for (const field of fieldNames) {
      for (const item of allSettings) {
        if (item.name === field) {
          generatedSettings.push(item);
        }
      }
    }

    generatedSettings.unshift(allSettings[0]);
    generatedSettings.push(allSettings[allSettings.length - 1]);

    return generatedSettings;
  }
}
