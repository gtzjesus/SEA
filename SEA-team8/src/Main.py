from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import DB
import RunController
from views import SEA
from views.AddTool import Ui_AddToolWindow
from views.CreateNewRun import Ui_NewRun
from views.DeleteTool import Ui_DeleteToolWindow
from views.DeleteRunRecord import Ui_DeleteRunWindow
from views.XmlDownload import Ui_Form
from views.EditScanTypes import Ui_EditScanTypes

# INITIALIZE UI
def init_ui():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = SEA.Ui_MainWindow()
    ui.setupUi(main_window)
    addToolWindow, addToolUi = init_add_tool()
    deleteToolWindow, deleteToolUi = init_delete_tool()
    newRunWindow, newRunUi = init_new_run()
    deleteRunWindow, deleteRunUi = init_delete_run()
    editScanTypesWindow, editScanTypesUi = init_edit_scan_type()
    GenerateXMLWindow, generateXmlUi = init_download_xml_report()



    # Start a 1 millisecond timer to trigger database load
    QTimer.singleShot(1, lambda: database.loadRuns(ui))
    QTimer.singleShot(1, lambda: database.loadTools(ui))

    # SEA UI #
    #   Tools Tab
    #     Tool List
    #       Trigger Add Tool window
    ui.addTool_pushButton.clicked.connect(lambda: addToolWindow.show())
    #       Trigger Delete Tool window
    ui.deleteTool_pushButton.clicked.connect(lambda: deleteToolWindow.show())
    #       Enable Delete Tool button based on tool selection
    ui.toolsTable.cellClicked.connect(lambda: ui.deleteTool_pushButton.setEnabled(True))
    #       Enable Update Tool button based on tool selection
    ui.toolsTable.cellClicked.connect(lambda: ui.saveConfiguration_pushButton.setEnabled(True))
    #       Enable Cancel Update Tool button based on tool selection
    ui.toolsTable.cellClicked.connect(lambda: ui.cancelConfiguration_pushButton_4.setEnabled(True))
    #     Detailed View
    #       Populate values based on tool selection
    ui.toolsTable.cellClicked.connect(lambda: database.loadToolSpecification(ui, ui.toolsTable.currentRow()))
    #       Browse tool path
    ui.browseToolPath_pushButton.clicked.connect(lambda: database.browseToolPath(ui))
    #       Save Tool button
    ui.saveConfiguration_pushButton.clicked.connect(lambda: database.updateTool(ui, ui.toolsTable.currentRow()))
    #
    #
    #   Runs Tab
    #     Run Control
    #       Play Run
    ui.play_pushButton.clicked.connect(lambda: runController.performRun(database, ui))
    #       Stop Run
    ui.stop_pushButton.clicked.connect(lambda: runController.terminateNmap(ui))
    #       Set Detailed View values on run selection
    ui.runsTable.cellClicked.connect(lambda: database.loadScanResults(ui, ui.runsTable.currentRow()))
    #       Set Run Configuration values on run selection
    ui.runsTable.cellClicked.connect(lambda: database.loadRunConfiguration(ui, ui.runsTable.currentRow()))
    #       Trigger New Run window
    ui.newRun_pushButton.clicked.connect(lambda: newRunWindow.show())
    #       Trigger Delete Run window
    ui.deleteRun_pushButton.clicked.connect(lambda: deleteRunWindow.show())
    #       Enable Play Run button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.play_pushButton.setEnabled(True))
    #       Enable Pause Run button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.pause_pushButton.setEnabled(True))
    #       Enable Stop Run button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.stop_pushButton.setEnabled(True))
    #       Enable Delete Run button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.deleteRun_pushButton.setEnabled(True))
    #       Enable Play Run 2 button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.play_pushButton_2.setEnabled(True))
    #       Enable Pause Run 2 button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.pause_pushButton_2.setEnabled(True))
    #       Enable Stop Run 2 button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.stop_pushButton_2.setEnabled(True))
    #       Enable Update Run button based on run selection
    #ui.runsTable.cellClicked.connect(lambda: ui.saveConfiguration_pushButton_5(True))
    #       Enable Cancel Update Run button based on run selection
    #ui.runsTable.cellClicked.connect(lambda: ui.cancelConfiguration_pushButton_5.setEnabled(True))
    #       Enable Edit Scan Type button based on run selection
    ui.runsTable.cellClicked.connect(lambda: ui.editScanType_pushButton.setEnabled(True))
    #     Update Run
    ui.saveConfiguration_pushButton_5.clicked.connect(lambda: database.createNewRun(newRunWindow, ui, ui))
    #     XML Report
    #       Dropdowns
    ui.run1_dropdown.currentTextChanged.connect(lambda: database.load_scans(ui))
    ui.cancel.clicked.connect(lambda: database.clear_xml_inputs(ui))
    ui.generate.clicked.connect(lambda: database.generate_xml_report(ui))

    #     Detailed View
    #     Configuration of Selected Run
    ui.play_pushButton_2.clicked.connect(lambda: runController.performRun(database, ui)) # performs run, but should it perform scan?
    ui.stop_pushButton_2.clicked.connect(lambda: runController.terminateNmap(ui))
    ui.editScanType_pushButton.clicked.connect(lambda: database.showEditScanTypesWindow(editScanTypesWindow, editScanTypesUi, ui))


    # NEW RUN UI #
    #   Enable Save button based on a new Run Name entered
    newRunUi.runName_lineEdit.textEdited.connect(lambda: newRunUi.saveConfiguration_pushButton.setEnabled(True))
    #   Add New Run when Save button is clicked
    newRunUi.saveConfiguration_pushButton.clicked.connect(lambda: database.createNewRun(newRunWindow, newRunUi, ui))
    newRunUi.saveConfigurationFromFile_pushButton.clicked.connect(lambda: database.createNewRunFromJson(newRunWindow, newRunUi, ui))
    #   Hide Window on Cancel
    newRunUi.cancelConfigurationFromFile_pushButton.clicked.connect(lambda: newRunWindow.hide())
    newRunUi.cancelConfiguration_pushButton_5.clicked.connect(lambda: newRunWindow.hide())
    #   Browse file directory for Run Configuration file
    newRunUi.runConfigFile_browse_pushButton.clicked.connect(lambda: database.readRunConfigFile(newRunUi))
    #   Open Edit Dialog
    newRunUi.editScanType_pushButton.clicked.connect(lambda: database.showEditScanTypesWindow(editScanTypesWindow, editScanTypesUi, newRunUi))

    # EDIT SCAN TYPES UI #
    #   If a scan type is selected, enable remove button
    editScanTypesUi.tableWidget.cellClicked.connect(lambda: editScanTypesUi.scanType_remove_pushButton.setEnabled(True))
    #   Add button
    editScanTypesUi.scanType_add_pushButton.clicked.connect(lambda: database.addToEditScanTypesWindow(editScanTypesUi))
    #   Remove button
    editScanTypesUi.scanType_remove_pushButton.clicked.connect(lambda: database.removeFromEditScanTypesWindow(editScanTypesUi, editScanTypesUi.tableWidget.currentRow()))
    #   Save button
    #     Save Scan Type (Note this will not write to the database).
    editScanTypesUi.saveScanType_pushButton.clicked.connect(lambda: database.saveScanTypes(editScanTypesWindow, editScanTypesUi, ui, newRunUi))
    #   Cancel Button: Hides UI
    editScanTypesUi.cancelScanType_pushButton.clicked.connect(lambda: editScanTypesWindow.hide())

    # DELETE RUN UI #
    #   Cancel and close Delete Run window
    deleteRunUi.cancel_pushButton.clicked.connect(lambda: deleteRunWindow.hide())
    #   Delete run
    deleteRunUi.confirm_pushButton.clicked.connect(lambda: database.deleteRun(deleteRunWindow, ui))

    # ADD TOOL UI #
    #   Browse tool path
    addToolUi.addTool_browseToolPath_pushButton.clicked.connect(lambda: database.browseToolPath(addToolUi))
    #   Cancel and close Add Tool window
    addToolUi.addTool_cancel_pushButton.clicked.connect(lambda: addToolWindow.hide())
    #   Add new tool
    addToolUi.addTool_save_pushButton.clicked.connect(lambda: database.addNewTool(addToolUi, addToolWindow, ui))

    # DELETE TOOL UI #
    #   Cancel and close Delete Tool window
    deleteToolUi.cancel_pushButton.clicked.connect(lambda: deleteToolWindow.hide())
    #   Delete tool
    deleteToolUi.confirm_pushButton.clicked.connect(lambda: database.deleteTool(deleteToolWindow, ui))

    # Display main SEA window (Leave down here or the code breaks)
    main_window.show()
    sys.exit(app.exec_())

def init_add_tool():
    AddToolWindow = QtWidgets.QMainWindow()
    ui = Ui_AddToolWindow()
    ui.setupUi(AddToolWindow)

    return AddToolWindow, ui

def init_delete_tool():
    DeleteToolWindow = QtWidgets.QWidget()
    ui = Ui_DeleteToolWindow()
    ui.setupUi(DeleteToolWindow)

    return DeleteToolWindow, ui

def init_new_run():
    NewRunWindow = QtWidgets.QMainWindow()
    ui = Ui_NewRun()
    ui.setupUi(NewRunWindow)
    return NewRunWindow, ui

def init_delete_run():
    DeleteRunWindow = QtWidgets.QWidget()
    ui = Ui_DeleteRunWindow()
    ui.setupUi(DeleteRunWindow)

    return DeleteRunWindow, ui

def init_edit_scan_type():
    EditScanTypesWindow = QtWidgets.QDialog()
    ui = Ui_EditScanTypes()
    ui.setupUi(EditScanTypesWindow)

    return EditScanTypesWindow,ui
    EditScanTypesWindow.show()

def init_download_xml_report():
    GenerateXMLWindow = QtWidgets.QDialog()
    ui = Ui_Form()
    ui.setupUi(GenerateXMLWindow)
    return GenerateXMLWindow, ui

if __name__ == "__main__":
    database = DB.Database()
    runController = RunController.RunController()

    init_ui()
