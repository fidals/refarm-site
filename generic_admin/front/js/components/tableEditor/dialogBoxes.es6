class TableEditorDialogBoxes {
  constructor() {
    this.DOM = {
      modalToDeleteProduct: {
        $: $('#confirm-modal'),
        $acceptBtn: $('.js-modal-delete'),
        $cancelBtn: $('.js-modal-delete-cancel'),
        $textField: $('#product-to-remove'),
        deleteProductBtnClass: 'js-confirm-delete-modal',
      },
    };

    this.popover = {
      className: '#popover',
      settings: {
        animation: 'pop',
        backdrop: true,
        closeable: true,
        content: 'Content',
        placement: 'top',
        title: 'Title',
        width: 300,
      },
    };

    this.init();
  }

  init() {
    this.setUpListeners();
    this.setupFormatter();
  }

  setUpListeners() {
    $(document).on('click', `.${this.DOM.modalToDeleteProduct.deleteProductBtnClass}`, (event) => {
      this.showModal(
        event, this.DOM.modalToDeleteProduct.$, this.DOM.modalToDeleteProduct.$textField);
    });

    $(document).on('keyup', event => {
      if (event.which === 27) {
        this.closeModal(event, this.DOM.modalToDeleteProduct.$);
      }
    });

    this.DOM.modalToDeleteProduct.$cancelBtn.click((event) => {
      this.closeModal(event, this.DOM.modalToDeleteProduct.$);
    });
  }

  /**
   * Extend jQgrid formatter.
   * Render html for Product removing icon.
   * @link http://goo.gl/9xcr7q
   */
  setupFormatter() {
    $.extend($.fn.fmatter, {
      removeTag: () => {
        return `
          <i
            class="jqgrid-remove-icon ${this.DOM.modalToDeleteProduct.deleteProductBtnClass} fa fa-2x fa-trash-o"
            title="Удалить товар" data-toggle="modal" data-target="#remove-modal"></i>
        `;
      },
    });
  }

  showModal(event, $modal, $textField, text = 'this product') {
    event.stopImmediatePropagation();

    $textField.text(text);
    $modal.addClass('modal-show');
  }

  closeModal(event, $modal) {
    event.stopImmediatePropagation();
    $modal.removeClass('modal-show');
  }

  showPopover($currentRow, colName, message) {
    const offset = $currentRow
      .find(`td[aria-describedby="jqGrid_${colName}"]`)
      .offset();

    const extendedSettings = $.extend(
      {}, this.popover.settings, {
        content: message,
        offsetTop: offset.top,
        offsetLeft: offset.left + (this.popover.settings.width / 2),
        title: 'Ошибка',
      });

    $(`${this.popover.className}`).webuiPopover('destroy').webuiPopover(extendedSettings);
    WebuiPopovers.show(`${this.popover.className}`);
  }
}
