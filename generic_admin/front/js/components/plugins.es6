class AdminCommonPlugins {
  constructor() {
    this.DOM = {
      searchFieldId: '#searchbar',
      saveAndContinueButton: 'input[name="_continue"]',
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
    this.saveAndContinueShortcutInit();
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

  /*
    Setup shortcut for "Save and continue" button (Ctrl + Enter)
  */
  saveAndContinueShortcutInit() {
    $(window).keydown(function(event) {
      if(event.ctrlKey && event.keyCode == 13) {
        event.preventDefault();
        // Django Admin have two "Save and continue" buttons, at top and bottom of page
        const element = $('input[name="_continue"]')[0];
        if (element) {
          element.click();
        );
      };
    });
  }

}
