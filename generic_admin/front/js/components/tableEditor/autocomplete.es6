class TableEditorAutocomplete {
  constructor(url) {
    this.url = url || '/admin/autocomplete/';
  }

  category(elem) {
    const url = this.url;

    $(elem).autocomplete({
      source(request, response) {
        $.ajax({
          type: 'GET',
          url,
          data: {
            term: request.term,
            pageType: 'category',
          },
          success(responseData) {
            response(responseData);
          },
          error(jqXhr, textStatus, errorThrown) {
            console.group('Autocomplete failed.');
            console.warn(jqXhr);
            console.warn(textStatus);
            console.warn(errorThrown);
            console.groupEnd();
          },
        });
      },
      // Set autocompleted value to input.
      select(_, ui) {
        $(elem).val(ui.item.label);
      },
      open(event) {
        $('.ui-menu').css('width', event.target.offsetWidth);
      },
    });
  }
}
