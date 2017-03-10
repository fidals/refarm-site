class TableEditorDialogs {
  constructor() {
    this.deleteDialog = {
      $: $('#confirm-modal'),
      $acceptBtn: $('.js-modal-delete'),
      $cancelBtn: $('.js-modal-delete-cancel'),
      $text: $('#product-to-remove'),
      deleteClass: 'js-confirm-delete-modal',
    };

    // https://goo.gl/TzEvoR
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
  }

  setUpListeners() {
    $(document).on('click', `.${this.deleteDialog.deleteClass}`, () => {
      this.showDeleteModal();
    });

    $(document).on('keyup', (event) => {
      const escapeBtnKeyCode = 27;
      if (event.which === escapeBtnKeyCode) {
        this.deleteDialog.$.removeClass('modal-show');
      }
    });

    this.deleteDialog.$cancelBtn.click(() => {
      this.deleteDialog.$.removeClass('modal-show');
    });
  }

  showDeleteModal(text = 'this product') {
    this.deleteDialog.$text.text(text);
    this.deleteDialog.$.addClass('modal-show');
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

    $(this.popover.className).webuiPopover('destroy').webuiPopover(extendedSettings);
    WebuiPopovers.show(this.popover.className);
  }
}
