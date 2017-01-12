class AdminCommonPlugins {
  constructor() {
    this.DOM = {
      searchFieldId: '#searchbar',
    };

    this.config = {
      autocompleteURL: '/admin/autocomplete/',
      minChars: 3,
      currentPageType: document.location.pathname.split('/').slice(-2, -1)[0],
      pagesType: { categorypage: 'category', productpage: 'product' },
    };

    this.init();
  }

  init() {
    this.setupXHR();
    this.autoCompleteInit();
  }

  setupXHR() {
    const csrfUnsafeMethod = method => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
        }
      },
    });
  }

  /**
   * https://goo.gl/2UDLKC
   */
  autoCompleteInit() {
    const pageType = this.config.pagesType[this.config.currentPageType];
    if (!pageType) return;

    return new autoComplete({
      selector: this.DOM.searchFieldId,
      minChars: this.config.minChars,
      source: (term, response) => {
        $.getJSON(
          this.config.autocompleteURL,
          { term, pageType },
          namesArray => response(namesArray),
        );
      },
    });
  }
}
