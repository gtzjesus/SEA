import json
import subprocess
import xml.etree.ElementTree as ET

import pymongo
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from bson.json_util import loads

import XmlReport
import ScanResult
import RunController

db_path = os.path.dirname(os.path.abspath(__file__)) + "/"

class Database(object):
    def __init__(self):
        pass

    def getTool(self, toolName):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        toolConfiguration = db.tools.find_one({"tool_name": toolName})

        return toolConfiguration

    def getToolNames(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        # pymongo uses a Cursor object as a return value for the find() method
        toolNameCursor = db.tools.find({}, {"tool_name": "1", "_id": "0"})

        # get all distinct tool_name(s)
        toolNameList = toolNameCursor.distinct("tool_name")
        toolNameList.insert(0, '')

        return toolNameList


    def getRun(self, runName):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        runConfiguration = db.runs.find_one({"run_name": runName})

        return runConfiguration

    def loadTools(self, ui):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']
        db.tools.delete_many({})

        global db_path
        json_file = os.path.join(db_path, 'database/tools.json')
        with open(json_file, "r") as file:
            for line in file:
                record = loads(line)
                # insert document (record) from json database
                db.tools.insert_one(record)
        file.close()

        tools = db.tools.find()

        ui.toolsTable.setRowCount(0)
        i = 0
        keys = ["tool_name", "tool_description"]

        for item in tools:
            # print(item)
            ui.toolsTable.insertRow(i)
            for x in range(2):
                ui.toolsTable.setItem(i, x, QtWidgets.QTableWidgetItem(item[keys[x]]))

    def loadRuns(self, ui):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']
        db.runs.delete_many({})

        global db_path
        json_file = os.path.join(db_path, 'database/runs.json')
        with open(json_file, "r") as file:
            for line in file:
                record = loads(line)
                # insert document (record) from json database
                db.runs.insert_one(record)
        file.close()

        runs = db.runs.find()

        ui.runsTable.setRowCount(0)
        i = 0
        keys = ["run_name", "run_description", "result_with_timestamp"]

        # Clear XML dropdowns in order to avoid duplicates.
        ui.run0_dropdown.clear()
        ui.run0_dropdown.addItem("")
        ui.run1_dropdown.clear()
        ui.run1_dropdown.addItem("")

        for item in runs:
            # Add runs to the XML Report dropdowns
            ui.run0_dropdown.addItem(item[keys[0]])
            ui.run1_dropdown.addItem(item[keys[0]])
            # Add runs to the Runs table
            ui.runsTable.insertRow(i)
            for x in range(3):
                ui.runsTable.setItem(i, x, QtWidgets.QTableWidgetItem(item[keys[x]]))

    def deleteRun(self, deleteRunWindow, mainUi):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        runName = str(mainUi.runsTable.currentItem().text())

        db.runs.delete_one({"run_name": runName})

        # Export db to runs.json file
        subprocess.call(
            "mongoexport --db=SEA --collection=runs --out=database/runs.json",
            shell=True)

        self.loadRuns(mainUi)
        deleteRunWindow.hide()

    def loadToolSpecification(self, ui, row):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']
        db.tools.delete_many({})

        toolName = ui.toolsTable.item(row, 0).text()

        global db_path
        json_file = os.path.join(db_path, 'database/tools.json')
        with open(json_file, "r") as file:
            for line in file:
                record = loads(line)
                # insert document (record) from json database
                db.tools.insert_one(record)
        file.close()

        toolSpecification = db.tools.find_one({"tool_name": toolName})

        # Tool Specification
        ui.toolName_lineEdit.setText(toolSpecification["tool_name"])
        ui.toolDescription_textEdit.setText(toolSpecification["tool_description"])
        ui.toolPath_lineEdit.setText(toolSpecification["tool_path"])
        ui.optionArgument_lineEdit.setText(toolSpecification["tool_option_and_argument"])
        ui.outputSpecification_lineEdit.setText(toolSpecification["tool_output_specification"])

        # Tool Dependency
        ui.dependentData_comboBox.setCurrentText(toolSpecification["tool_dependent_data"])
        ui.operator_comboBox.setCurrentText(toolSpecification["tool_operator"])
        ui.value_lineEdit.setText(toolSpecification["tool_value"])
        ui.dependencyExpression_lineEdit.setText(toolSpecification["tool_dependency_expression"])


    def addNewTool(self, ui, addToolWindow, mainUi):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        toolName = ui.addTool_toolName_lineEdit.text()
        toolDescription = ui.addTool_toolDescription_textEdit.toPlainText()
        toolPath = ui.toolPath_lineEdit.text()
        toolOptionArgument = ui.addTool_optionArgument_lineEdit.text()
        toolOutputSpecification = ui.addTool_outputSpecification_lineEdit.text()
        toolDependentData = ui.dependentData_comboBox.currentText()
        toolOperator = ui.operator_comboBox.currentText()
        toolValue = ui.value_lineEdit.text()
        toolDependencyExpression = ui.dependencyExpression_lineEdit.text()

        newTool = f'{{"tool_name":"{toolName}","tool_description":"{toolDescription}","tool_path":"{toolPath}","tool_option_and_argument":"{toolOptionArgument}","tool_output_specification":"{toolOutputSpecification}","tool_dependent_data":"{toolDependentData}","tool_operator":"{toolOperator}","tool_value":"{toolValue}","tool_dependency_expression":"{toolDependencyExpression}"}}'

        print(newTool)
        record = loads(newTool)
        db.tools.insert_one(record)
        # Export db to tools.json file
        subprocess.call(
            "mongoexport --db=SEA --collection=tools --out=database/tools.json",
            shell=True)
        self.loadTools(mainUi)


        ui.addTool_toolName_lineEdit.setText('')
        ui.addTool_toolDescription_textEdit.setText('')
        ui.toolPath_lineEdit.setText('')
        ui.addTool_optionArgument_lineEdit.setText('')
        ui.addTool_outputSpecification_lineEdit.setText('')
        ui.dependentData_comboBox.setCurrentText('')
        ui.operator_comboBox.setCurrentText('')
        ui.value_lineEdit.setText('')
        ui.dependencyExpression_lineEdit.setText('')

        addToolWindow.hide()

    def deleteTool(self, deleteToolWindow, mainUi):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        toolName = str(mainUi.toolsTable.currentItem().text())

        db.tools.delete_one({"tool_name": toolName})

        # Export db to tools.json file
        subprocess.call(
            "mongoexport --db=SEA --collection=tools --out=database/tools.json",
            shell=True)

        self.loadTools(mainUi)
        deleteToolWindow.hide()

    def searchTool(self, searchToolSpecifications, mainui):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        toolcol = db["Tool Name"]

        for x in toolcol.find({}, {"_id": 0, "tool_name": 1, "tool_path": 1}):
            print(x)

    def updateTool(self, ui, row):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        toolToUpdate = ui.toolsTable.item(row, 0).text()

        toolName = ui.toolName_lineEdit.text()
        toolDescription = ui.toolDescription_textEdit.toPlainText()
        toolPath = ui.toolPath_lineEdit.text()
        toolOptionArgument = ui.optionArgument_lineEdit.text()
        toolOutputSpecification = ui.outputSpecification_lineEdit.text()

        # Tool Dependency
        toolDependentData = ui.dependentData_comboBox.currentText()
        toolOperator = ui.operator_comboBox.currentText()
        toolValue = ui.value_lineEdit.text()
        toolDependencyExpression = ui.dependencyExpression_lineEdit.text()

        filter = { 'tool_name': toolToUpdate }

        newValues = {
            "$set": {
                'tool_name': toolName,
                'tool_description': toolDescription,
                'tool_path': toolPath,
                'tool_option_and_argument': toolOptionArgument,
                'tool_output_specification': toolOutputSpecification,
                'tool_dependent_data': toolDependentData,
                'tool_operator': toolOperator,
                'tool_value': toolValue,
                'tool_dependency_expression': toolDependencyExpression
            }
        }

        db.tools.update_one(filter, newValues)
        # Export db to tools.json file
        subprocess.call(
            "mongoexport --db=SEA --collection=tools --out=database/tools.json",
            shell=True)
        self.loadTools(ui)

    def browseToolPath(self, ui):
        # Open File Explorer
        file = QFileDialog.getOpenFileName()
        filePath = file[0]
        ui.toolPath_lineEdit.setText(filePath)


    def loadRunConfiguration(self, ui, row):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']
        db.runs.delete_many({})

        runName = ui.runsTable.item(row, 0).text()


        global db_path
        json_file = os.path.join(db_path, 'database/runs.json')
        with open(json_file, "r") as file:
            for line in file:
                record = loads(line)
                # insert document (record) from json database
                db.runs.insert_one(record)
        file.close()

        runConfiguration = db.runs.find_one({"run_name": runName})

        ui.runName_lineEdit.setText(runConfiguration["run_name"])
        ui.runDescription_lineEdit.setText(runConfiguration["run_description"])


        whitelist = runConfiguration["whitelist"]
        if isinstance(whitelist, list):
            whitelist_str = ", "
            whitelist_str = whitelist_str.join(runConfiguration["whitelist"])
            ui.whitelist_lineEdit.setText(whitelist_str)
        else:
            ui.whitelist_lineEdit.setText(whitelist)

        blacklist = runConfiguration["blacklist"]
        if isinstance(blacklist, list):
            blacklist_str = ", "
            blacklist_str = blacklist_str.join(runConfiguration["blacklist"])
            ui.blacklist_lineEdit.setText(blacklist_str)
        else:
            ui.blacklist_lineEdit.setText(blacklist)

        ui.scanType_lineEdit.setText(runConfiguration["scan_type"])

    def loadScanResults(self, ui, row):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']
        db.runs.delete_many({})

        runName = ui.runsTable.item(row, 0).text()

        global db_path
        json_file = os.path.join(db_path, 'database/scans.json')
        with open(json_file, "r") as file:
            for line in file:
                record = loads(line)
                # insert document (record) from json database
                db.runs.insert_one(record)
        file.close()

        scanResultCollection = db.scans.find_one({"run_name": runName}, sort=[("end_time", pymongo.DESCENDING)])

        if (scanResultCollection is None):
            for i in range(7):  # clear table
                ui.scans_tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(None))
            ui.scanOutputData_textEdit.clear()  # clear scan output data area

        else: # populate table
            startTime = scanResultCollection.get("start_time")
            endTime = scanResultCollection.get("end_time")
            ips = scanResultCollection.get("scanned_ips")
            successOrFailure = scanResultCollection.get("success_or_failure")
            formatted_outputString = scanResultCollection.get("formatted_output")

            # format ip list
            ips = ips.replace('[', '')
            ips = ips.replace(']', '')
            ips = ips.replace('\'', '')
            ips = ips.replace(' ', ',')

            # complete info array
            infoArray = [startTime, endTime, ips, successOrFailure]

            ui.scans_tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("Finished."))
            i = 3

            for x in range(4):
                ui.scans_tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(infoArray[x]))
                i = i + 1

            # populate scan output data area
            ui.scanOutputData_textEdit.clear()  # reset
            ui.scanOutputData_textEdit.insertPlainText(formatted_outputString)  # write

    def readRunConfigFile(self, ui):

        # Open File Explorer
        file = QFileDialog.getOpenFileName()
        filePath = file[0]
        ui.runConfigFile_lineEdit.setText(filePath)

        with open(filePath) as json_file:
            runConfig = json.load(json_file)

        jsonString = json.dumps(runConfig)
        ui.runConfigFromFile_textEdit.setText(jsonString)

        ui.saveConfigurationFromFile_pushButton.setEnabled(True)

    def createNewRun(self, newRunWindow, ui, mainUi):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        # only if method was called from Update Run
        if ui == mainUi:
            runName = ui.runName_lineEdit.text()
            runDescription = ui.runDescription_lineEdit.toPlainText()
            blackList = ui.blacklist_lineEdit.toPlainText()
            whiteList = ui.whitelist_lineEdit.toPlainText()
            scanType = ui.scanType_lineEdit.text()

            oldRunName = str(mainUi.runsTable.currentItem().text())
            db.runs.delete_one({"run_name": oldRunName})
            # Export db to runs.json file
            subprocess.call(
                "mongoexport --db=SEA --collection=runs --out=database/runs.json",
                shell=True)
            self.loadRuns(mainUi)

        else:
            runName = ui.runName_lineEdit.text()
            runDescription = ui.runDescription_lineEdit.toPlainText()
            blackList = ui.blacklist_lineEdit.text()
            whiteList = ui.whitelist_lineEdit.text()
            scanType = ui.scanType_lineEdit.text()

        newRun = f'{{"run_name":"{runName}","run_description":"{runDescription}","blacklist":"{blackList}","whitelist":"{whiteList}","scan_type":"{scanType}", "result_with_timestamp":"No Result Yet."}}'

        record = loads(newRun)
        db.runs.insert_one(record)
        # Export db to tools.json file
        subprocess.call(
            "mongoexport --db=SEA --collection=runs --out=database/runs.json",
            shell=True)
        self.loadRuns(mainUi)

        ui.runName_lineEdit.setText('')
        ui.runDescription_lineEdit.setText('')
        ui.blacklist_lineEdit.setText('')
        ui.whitelist_lineEdit.setText('')
        ui.scanType_lineEdit.setText('')

        newRunWindow.hide()

    def createNewScan(self, scan_result):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        scan_name = scan_result.scan_name
        run_name = scan_result.run_name
        start = scan_result.start_time
        end = scan_result.end_time
        scannedIp = scan_result.ip_list
        successOrFailure = scan_result.exec_status
        formatted_result = json.dumps(scan_result.formatted_output)

        newScan = f'{{"run_name":"{run_name}","scan_name":"{scan_name}","start_time":"{start}","end_time":"{end}","scanned_ips":"{scannedIp}","success_or_failure":"{successOrFailure}","formatted_output":{formatted_result}}}'

        record = loads(newScan)
        db.scans.insert_one(record)
        # export db to scans.json file
        subprocess.call(
            "mongoexport --db=SEA --collection=scans --out=database/scans.json",
            shell=True
        )

    def createNewRunFromJson(self, newRunWindow, ui, mainUi):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        runStr = ui.runConfigFromFile_textEdit.toPlainText()
        runDict = json.loads(runStr)

        runName = runDict["run_name"]
        runDescription = runDict["run_description"]
        blackList = runDict["blacklist"]
        whiteList = runDict["whitelist"]
        scanType = runDict["scan_type"]

        newRun = f'{{"run_name":"{runName}","run_description":"{runDescription}","blacklist":"{blackList}","whitelist":"{whiteList}","scan_type":"{scanType}", "result_with_timestamp":"No Result Yet."}}'

        record = loads(newRun)
        db.runs.insert_one(record)
        # Export db to tools.json file
        subprocess.call(
            "mongoexport --db=SEA --collection=runs --out=database/runs.json",
            shell=True)
        self.loadRuns(mainUi)

        newRunWindow.hide()


    def showEditScanTypesWindow(self, editScanTypesWindow, editScanTypesUi, callerUi):
        toolNameList = self.getToolNames()

        # Remove all current options from dropdown to avoid repeats
        editScanTypesUi.scanType_comboBox.clear()

        # Add tool names as options for the dropdown
        editScanTypesUi.scanType_comboBox.addItems(toolNameList)

        # Define current selection to empty
        editScanTypesUi.scanType_comboBox.setCurrentText('')

        # Remove all previous rows from table
        for i in range(editScanTypesUi.tableWidget.rowCount()):
            editScanTypesUi.tableWidget.removeRow(0)

        # Populate table with previously selected scan types from caller (May be empty)
        previousScans = callerUi.scanType_lineEdit.text().split(", ")
        if previousScans[0] != "":
            editScanTypesUi.tableWidget.setRowCount(len(previousScans))
            rowCount = 0
            for item in previousScans:
                editScanTypesUi.tableWidget.setItem(rowCount, 0, QtWidgets.QTableWidgetItem(item))
                rowCount += 1

        # Enable save button if table is not empty
        rowCount = 0
        rowCount = editScanTypesUi.tableWidget.rowCount()
        if rowCount > 0:
            editScanTypesUi.saveScanType_pushButton.setEnabled(True)

        editScanTypesWindow.show()

    def addToEditScanTypesWindow(self, editScanTypesUi):
        input = editScanTypesUi.scanType_comboBox.currentText()
        if input != "":
            rowCount = editScanTypesUi.tableWidget.rowCount()
            editScanTypesUi.tableWidget.insertRow(rowCount)
            editScanTypesUi.tableWidget.setItem(rowCount, 0, QtWidgets.QTableWidgetItem(input))
            #   If a scan type is added, enable save button
            editScanTypesUi.saveScanType_pushButton.setEnabled(True)

    def removeFromEditScanTypesWindow(self, editScanTypesUi, currentRow):
        rowCount = editScanTypesUi.tableWidget.rowCount()
        # remove row
        editScanTypesUi.tableWidget.removeRow(currentRow)
        rowCount -= 1

        # Disable remove button after deletion
        editScanTypesUi.scanType_remove_pushButton.clicked.connect(lambda: editScanTypesUi.scanType_remove_pushButton.setEnabled(False))

        # Disable save button if table is empty
        if rowCount == 0:
            editScanTypesUi.saveScanType_pushButton.setEnabled(False)

    def saveScanTypes(self, editScanTypesWindow, editScanTypesUi, mainUi, newRunUi):
        scanTypesToString = ""

        # Retrieve entire table and append to scanTypesToString
        for i in range(editScanTypesUi.tableWidget.rowCount()):
            scanTypesToString += editScanTypesUi.tableWidget.item(i, 0).text() + ", "
        # remove the extra ", "
        scanTypesToString = scanTypesToString[:-1]
        scanTypesToString = scanTypesToString[:-1]

        # set the callers scanType_lineEdit to the toString
        mainUi.scanType_lineEdit.setText(scanTypesToString)
        newRunUi.scanType_lineEdit.setText(scanTypesToString)

        editScanTypesWindow.hide()

    def generate_xml_report(self, ui):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        report_name = ui.report_name_text.text()
        report_description = ui.report_description_text.toPlainText()

        run_name = ui.run0_dropdown.currentText()

        run_name2 = ui.run1_dropdown.currentText()
        scan_name = ui.scan_dropdown.currentText()

        if scan_name == "":
            scan_result = db.scans.find_one({"run_name": run_name})
        else:
            scan_result = db.scans.find_one({"run_name": run_name2, "scan_name": scan_name})

        content = scan_result["scan_result"]

        # Create XmlReport instance
        xml_report =  XmlReport.Xml_Report(report_name, report_description, content)

        # Convert XmlReport instance into xml document
        root = ET.Element("XML_REPORT")
        name = ET.Element("Name")
        name.text = xml_report.name
        description = ET.Element("Description")
        description.text = xml_report.desc

        result_tree = ET.fromstring(xml_report.content)

        # content = ET.Element("Results")
        # content.text = xml_report.content

        root.append(name)
        root.append(description)
        root.append(result_tree)
        # root.append(content)

        tree = ET.ElementTree(root)

        file_name = "reports/" + report_name + ".xml"
        with open(file_name, "wb") as files :
            tree.write(files)

        ui.report_name_text.clear()
        ui.report_description_text.clear()
        ui.run0_dropdown.setCurrentText('')
        ui.run1_dropdown.setCurrentText('')
        ui.scan_dropdown.setCurrentText('')
        return

    def load_scans(self, ui):
        client = pymongo.MongoClient("localhost", 27017)
        db = client['SEA']

        ui.scan_dropdown.clear()

        run_name = ui.run1_dropdown.currentText()
        runConfiguration = db.runs.find_one({"run_name": run_name})

        if runConfiguration is not None:
            scan_name = runConfiguration["scan_type"]

            ui.scan_dropdown.addItem(scan_name)

    def clear_xml_inputs(self, ui):

        ui.report_name_text.clear()
        ui.report_description_text.clear()
        ui.run0_dropdown.setCurrentText('')
        ui.run1_dropdown.setCurrentText('')
        ui.scan_dropdown.setCurrentText('')

