/**
 * Common helper classes for Admin Table Editor.
 */
class Autocomplete {
  constructor(url, pageType) {
    this.url = url || '/admin/autocomplete/';
    this.pageType = pageType || 'category';
  }

  category(elem) {
    const url = this.url;
    const pageType = this.pageType;

    $(elem).autocomplete({
      source(request, response) {
        $.ajax({
          type: 'GET',
          url,
          data: {
            term: request.term,
            pageType,
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
      open(event) {
        $('.ui-menu').css('width', event.target.offsetWidth);
      },
    });
  }
}
