*&---------------------------------------------------------------------*
*& Report ZMARC_EDITABLE_ALV
*&---------------------------------------------------------------------*
*& Editable ALV Report for MARC Table
*&---------------------------------------------------------------------*
REPORT zmarc_editable_alv.

TABLES: marc.

DATA: gt_marc TYPE TABLE OF marc,
      gs_marc TYPE marc.

DATA: go_container TYPE REF TO cl_gui_custom_container,
      go_alv       TYPE REF TO cl_gui_alv_grid.

DATA: gt_fieldcat TYPE lvc_t_fcat,
      gs_fieldcat TYPE lvc_s_fcat,
      gs_layout   TYPE lvc_s_layo.

SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
SELECT-OPTIONS: s_matnr FOR marc-matnr,
                s_werks FOR marc-werks.
SELECTION-SCREEN END OF BLOCK b1.

START-OF-SELECTION.
  PERFORM get_data.
  CALL SCREEN 100.

END-OF-SELECTION.

*&---------------------------------------------------------------------*
*& Form GET_DATA
*&---------------------------------------------------------------------*
FORM get_data.
  SELECT * FROM marc
    INTO TABLE gt_marc
    WHERE matnr IN s_matnr
      AND werks IN s_werks.

  IF sy-subrc <> 0.
    MESSAGE 'No data found' TYPE 'I'.
    LEAVE LIST-PROCESSING.
  ENDIF.
ENDFORM.

*&---------------------------------------------------------------------*
*& Module STATUS_0100 OUTPUT
*&---------------------------------------------------------------------*
MODULE status_0100 OUTPUT.
  SET PF-STATUS 'STATUS_100'.
  SET TITLEBAR 'TITLE_100'.

  IF go_container IS INITIAL.
    PERFORM display_alv.
  ENDIF.
ENDMODULE.

*&---------------------------------------------------------------------*
*& Module USER_COMMAND_0100 INPUT
*&---------------------------------------------------------------------*
MODULE user_command_0100 INPUT.
  CASE sy-ucomm.
    WHEN 'BACK' OR 'EXIT' OR 'CANCEL'.
      LEAVE TO SCREEN 0.
    WHEN 'SAVE'.
      PERFORM save_data.
  ENDCASE.
ENDMODULE.

*&---------------------------------------------------------------------*
*& Form DISPLAY_ALV
*&---------------------------------------------------------------------*
FORM display_alv.
  CREATE OBJECT go_container
    EXPORTING
      container_name = 'CONTAINER'.

  CREATE OBJECT go_alv
    EXPORTING
      i_parent = go_container.

  PERFORM build_fieldcat.
  PERFORM build_layout.

  CALL METHOD go_alv->set_table_for_first_display
    EXPORTING
      is_layout       = gs_layout
    CHANGING
      it_outtab       = gt_marc
      it_fieldcatalog = gt_fieldcat.

  CALL METHOD go_alv->register_edit_event
    EXPORTING
      i_event_id = cl_gui_alv_grid=>mc_evt_modified.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form BUILD_FIELDCAT
*&---------------------------------------------------------------------*
FORM build_fieldcat.
  CALL FUNCTION 'LVC_FIELDCATALOG_MERGE'
    EXPORTING
      i_structure_name = 'MARC'
    CHANGING
      ct_fieldcat      = gt_fieldcat.

  LOOP AT gt_fieldcat INTO gs_fieldcat.
    gs_fieldcat-edit = 'X'.
    MODIFY gt_fieldcat FROM gs_fieldcat.
  ENDLOOP.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form BUILD_LAYOUT
*&---------------------------------------------------------------------*
FORM build_layout.
  gs_layout-zebra      = 'X'.
  gs_layout-cwidth_opt = 'X'.
  gs_layout-sel_mode   = 'A'.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form SAVE_DATA
*&---------------------------------------------------------------------*
FORM save_data.
  DATA: lv_answer TYPE c.

  CALL FUNCTION 'POPUP_TO_CONFIRM'
    EXPORTING
      titlebar              = 'Confirm Save'
      text_question         = 'Do you want to save the changes?'
      text_button_1         = 'Yes'
      text_button_2         = 'No'
      default_button        = '2'
      display_cancel_button = ''
    IMPORTING
      answer                = lv_answer.

  IF lv_answer = '1'.
    CALL METHOD go_alv->check_changed_data.

    UPDATE marc FROM TABLE gt_marc.
    IF sy-subrc = 0.
      COMMIT WORK.
      MESSAGE 'Data saved successfully' TYPE 'S'.
    ELSE.
      ROLLBACK WORK.
      MESSAGE 'Error saving data' TYPE 'E'.
    ENDIF.
  ENDIF.
ENDFORM.
