*&---------------------------------------------------------------------*
*& Report ZMIRO_REPROCESS_OO
*&---------------------------------------------------------------------*
*& OO Program to reprocess MIRO invoice postings
*&---------------------------------------------------------------------*
REPORT zmiro_reprocess_oo.

TABLES: rbkp, rseg.

*----------------------------------------------------------------------*
*       CLASS lcl_miro_reprocess DEFINITION
*----------------------------------------------------------------------*
CLASS lcl_miro_reprocess DEFINITION FINAL.
  PUBLIC SECTION.
    TYPES: BEGIN OF ty_invoice_data,
             belnr TYPE rseg-belnr,
             gjahr TYPE rbkp-gjahr,
             bukrs TYPE rbkp-bukrs,
             belnr_i TYPE rbkp-belnr,
             sapnr  TYPE rbkp-sapnr,
             xblnr  TYPE rbkp-xblnr,
             lifnr  TYPE rbkp-lifnr,
             wrbtr  TYPE rbkp-wrbtr,
           END OF ty_invoice_data.

    TYPES: tt_invoice_data TYPE TABLE OF ty_invoice_data.

    METHODS:
      constructor,
      get_invoice_data
        RETURNING VALUE(rt_data) TYPE tt_invoice_data,
      process_invoice
        IMPORTING IS_KEY TYPE ty_invoice_data
        RETURNING VALUE(rv_success) TYPE abap_bool,
      process_selected_invoices
        IMPORTING IT_DATA TYPE tt_invoice_data
        EXPORTING ET_LOG  TYPE string_table,
      display_invoices
        IMPORTING IT_DATA TYPE tt_invoice_data,
      show_log
        IMPORTING IT_LOG TYPE string_table.

  PRIVATE SECTION.
    DATA:
      gt_invoice_data TYPE tt_invoice_data,
      go_container   TYPE REF TO cl_gui_custom_container,
      go_alv         TYPE REF TO cl_gui_alv_grid,
      gt_fieldcat    TYPE lvc_t_fcat,
      gs_layout      TYPE lvc_s_layo.

    METHODS:
      build_fieldcat,
      build_layout.
ENDCLASS.

*----------------------------------------------------------------------*
*       CLASS lcl_miro_reprocess IMPLEMENTATION
*----------------------------------------------------------------------*
CLASS lcl_miro_reprocess IMPLEMENTATION.
  METHOD constructor.
    " Initial setup
  ENDMETHOD.

  METHOD get_invoice_data.
    " Get invoices with errors for reprocessing
    SELECT rseg~belnr rseg~gjahr rbkp~bukrs rbkp~belnr AS belnr_i 
           rbkp~sapnr rbkp~xblnr rbkp~lifnr rbkp~wrbtr
      FROM rseg
      INNER JOIN rbkp ON rseg~belnr = rbkp~belnr AND rseg~gjahr = rbkp~gjahr
      INTO CORRESPONDING FIELDS OF TABLE rt_data
      WHERE rbkp~xrech = ''  " Not posted
        OR rbkp~cpudt < sy-datum - 30  " Older than 30 days
      UP TO 100 ROWS.
  ENDMETHOD.

  METHOD process_invoice.
    DATA: ls_header TYPE bapi_incinv_create_header,
          lt_item   TYPE TABLE OF bapi_incinv_create_item,
          ls_item   TYPE bapi_incinv_create_item,
          lt_return TYPE TABLE OF bapiret2,
          ls_return TYPE bapiret2,
          lv_invoice TYPE bapi_incinv_fld-inv_doc_no,
          lv_fiscal  TYPE bapi_incinv_fld-fisc_year,
          lt_rseg   TYPE TABLE OF rseg,
          ls_rseg   TYPE rseg.

    " Get invoice items
    SELECT * FROM rseg
      INTO TABLE lt_rseg
      WHERE belnr = is_key-belnr_i
        AND gjahr = is_key-gjahr.

    IF lt_rseg IS INITIAL.
      MESSAGE s001(zm) WITH 'No items found' DISPLAY LIKE 'E'.
      RETURN.
    ENDIF.

    " Build header data for recreation
    ls_header-invoice_ind = 'X'.
    ls_header-invoice_doc  = is_key-belnr_i.
    ls_header-fisc_year    = is_key-gjahr.
    ls_header-doc_date     = sy-datum.
    ls_header-pstng_date   = sy-datum.
    ls_header-comp_code    = is_key-bukrs.
    ls_header-ref_doc_no   = is_key-xblnr.

    " Build items
    LOOP AT lt_rseg INTO ls_rseg.
      ls_item-invoice_doc_item = ls_rseg-buzei.
      ls_item-po_number        = ls_rseg-ebeln.
      ls_item-po_item         = ls_rseg-ebelp.
      ls_item-quantity        = ls_rseg-menge.
      ls_item-po_unit         = ls_rseg-meins.
      ls_item-tax_code        = ls_rseg-mwskz.
      ls_item-item_amount     = ls_rseg-wrbtr.
      APPEND ls_item TO lt_item.
    ENDLOOP.

    " Call BAPI to reprocess invoice
    CALL FUNCTION 'BAPI_INCOMINGINVOICE_CREATE'
      EXPORTING
        headerdata       = ls_header
      IMPORTING
        invoiceno        = lv_invoice
        fiscalyear       = lv_fiscal
      TABLES
        itemdata         = lt_item
        return           = lt_return.

    " Check for errors
    READ TABLE lt_return INTO ls_return WITH KEY type = 'E'.
    IF sy-subrc <> 0.
      " Success - commit
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
        EXPORTING
          wait = 'X'.
      rv_success = abap_true.
    ELSE.
      " Error - rollback
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rv_success = abap_false.
    ENDIF.
  ENDMETHOD.

  METHOD process_selected_invoices.
    DATA: ls_invoice TYPE ty_invoice_data,
          lv_success  TYPE abap_bool,
          lv_message  TYPE string,
          lt_log      TYPE string_table.

    LOOP AT it_data INTO ls_invoice.
      lv_success = process_invoice( ls_invoice ).
      IF lv_success = abap_true.
        lv_message = |Invoice { ls_invoice-belnr_i } processed successfully|.
      ELSE.
        lv_message = |Failed to process invoice { ls_invoice-belnr_i }|.
      ENDIF.
      APPEND lv_message TO et_log.
    ENDLOOP.
  ENDMETHOD.

  METHOD display_invoices.
    IF go_container IS INITIAL.
      CREATE OBJECT go_container
        EXPORTING
          container_name = 'CONTAINER'.

      CREATE OBJECT go_alv
        EXPORTING
          i_parent = go_container.

      build_fieldcat( ).
      build_layout( ).
    ENDIF.

    CALL METHOD go_alv->set_table_for_first_display
      EXPORTING
        is_layout       = gs_layout
      CHANGING
        it_outtab       = it_data
        it_fieldcatalog = gt_fieldcat.
  ENDMETHOD.

  METHOD build_fieldcat.
    DATA: ls_fieldcat TYPE lvc_s_fcat.

    ls_fieldcat-fieldname = 'BELNR'.
    ls_fieldcat-ref_field = 'BELNR'.
    ls_fieldcat-ref_table = 'RSEG'.
    ls_fieldcat-inttype   = 'C'.
    ls_fieldcat-scrtext_l = 'Item Doc'.
    APPEND ls_fieldcat TO gt_fieldcat.

    ls_fieldcat-fieldname = 'GJAHR'.
    ls_fieldcat-ref_field = 'GJAHR'.
    ls_fieldcat-ref_table = 'RSEG'.
    ls_fieldcat-inttype   = 'N'.
    ls_fieldcat-scrtext_l = 'Fisc Yr'.
    APPEND ls_fieldcat TO gt_fieldcat.

    ls_fieldcat-fieldname = 'BUKRS'.
    ls_fieldcat-ref_field = 'BUKRS'.
    ls_fieldcat-ref_table = 'RBP'.
    ls_fieldcat-inttype   = 'C'.
    ls_fieldcat-scrtext_l = 'Comp Code'.
    APPEND ls_fieldcat TO gt_fieldcat.

    ls_fieldcat-fieldname = 'BELNR_I'.
    ls_fieldcat-ref_field = 'BELNR'.
    ls_fieldcat-ref_table = 'RBP'.
    ls_fieldcat-inttype   = 'C'.
    ls_fieldcat-scrtext_l = 'Inv Doc'.
    APPEND ls_fieldcat TO gt_fieldcat.

    ls_fieldcat-fieldname = 'LIFNR'.
    ls_fieldcat-ref_field = 'LIFNR'.
    ls_fieldcat-ref_table = 'RBP'.
    ls_fieldcat-inttype   = 'C'.
    ls_fieldcat-scrtext_l = 'Vendor'.
    APPEND ls_fieldcat TO gt_fieldcat.

    ls_fieldcat-fieldname = 'WRBTR'.
    ls_fieldcat-ref_field = 'WRBTR'.
    ls_fieldcat-ref_table = 'RBP'.
    ls_fieldcat-inttype   = 'P'.
    ls_fieldcat-scrtext_l = 'Amount'.
    APPEND ls_fieldcat TO gt_fieldcat.
  ENDMETHOD.

  METHOD build_layout.
    gs_layout-zebra      = 'X'.
    gs_layout-cwidth_opt = 'X'.
    gs_layout-sel_mode   = 'A'.
  ENDMETHOD.

  METHOD show_log.
    DATA: lv_message TYPE string.

    LOOP AT it_log INTO lv_message.
      WRITE:/ lv_message.
    ENDLOOP.
  ENDMETHOD.
ENDCLASS.

*----------------------------------------------------------------------*
*       Data declarations
*----------------------------------------------------------------------*
DATA: go_miro_handler TYPE REF TO lcl_miro_reprocess,
      gt_invoices    TYPE lcl_miro_reprocess=>tt_invoice_data,
      gt_log         TYPE string_table.
DATA: s_belnr TYPE rseg-belnr,
      s_gjahr TYPE rbkp-gjahr.

*----------------------------------------------------------------------*
*       Selection Screen
*----------------------------------------------------------------------*
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
SELECT-OPTIONS: s_belnr FOR rbkp-belnr,
                s_gjahr FOR rbkp-gjahr.
SELECTION-SCREEN END OF BLOCK b1.

START-OF-SELECTION.
  PERFORM execute_report.

*&---------------------------------------------------------------------*
*&      Form  EXECUTE_REPORT
*&---------------------------------------------------------------------*
FORM execute_report.
  CREATE OBJECT go_miro_handler.
  
  gt_invoices = go_miro_handler->get_invoice_data( ).
  
  IF gt_invoices IS INITIAL.
    MESSAGE 'No invoices found for reprocessing' TYPE 'I'.
    RETURN.
  ENDIF.
  
  CALL SCREEN 100.
ENDFORM.

*&---------------------------------------------------------------------*
*& Module STATUS_0100 OUTPUT
*&---------------------------------------------------------------------*
MODULE status_0100 OUTPUT.
  SET PF-STATUS 'STATUS_100'.
  SET TITLEBAR 'TITLE_100'.
  
  go_miro_handler->display_invoices( gt_invoices ).
ENDMODULE.

*&---------------------------------------------------------------------*
*& Module USER_COMMAND_0100 INPUT
*&---------------------------------------------------------------------*
MODULE user_command_0100 INPUT.
  CASE sy-ucomm.
    WHEN 'REPROCESS'.
      PERFORM reprocess_selected.
    WHEN 'BACK' OR 'EXIT' OR 'CANCEL'.
      LEAVE TO SCREEN 0.
  ENDCASE.
ENDMODULE.

*&---------------------------------------------------------------------*
*& Form REPROCESS_SELECTED
*&---------------------------------------------------------------------*
FORM reprocess_selected.
  DATA: lt_selected TYPE lrel_t_ocus,
        ls_key      TYPE lrel_key_ocus,
        lt_rows     TYPE lvc_t_row,
        ls_row      TYPE lvc_s_row,
        lt_proc     TYPE lcl_miro_reprocess=>tt_invoice_data,
        ls_invoice  TYPE lcl_miro_reprocess=>ty_invoice_data.

  " Get selected rows
  CALL METHOD go_miro_handler->go_alv->get_selected_rows
    IMPORTING
      et_index_rows = lt_rows.

  IF lt_rows IS INITIAL.
    MESSAGE 'Please select invoices for reprocessing' TYPE 'E'.
    RETURN.
  ENDIF.

  " Collect selected invoices
  LOOP AT lt_rows INTO ls_row.
    READ TABLE gt_invoices INTO ls_invoice INDEX ls_row-index.
    IF sy-subrc = 0.
      APPEND ls_invoice TO lt_proc.
    ENDIF.
  ENDLOOP.

  " Process selected invoices
  go_miro_handler->process_selected_invoices(
    EXPORTING
      it_data = lt_proc
    IMPORTING
      et_log  = gt_log
  ).

  " Show processing log
  go_miro_handler->show_log( gt_log ).
  
  " Refresh data
  gt_invoices = go_miro_handler->get_invoice_data( ).
  go_miro_handler->display_invoices( gt_invoices ).
ENDFORM.