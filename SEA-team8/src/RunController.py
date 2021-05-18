import os
import subprocess
import sys
import threading
import xml.etree.ElementTree as ET

from PyQt5 import QtWidgets
import RunConfig
import ToolConfig
import ScanResult
import DB


class RunController(object):
    nmapProcess = None
    nmapProcessId = 0
    nmapEvent = None


    def performRun(self, database, mainUi):

        runName = mainUi.runsTable.item(mainUi.runsTable.currentRow(), 0).text()

        db = DB.Database()
        runConfiguration = db.getRun(runName)
        numOfScans = 1

        if (runConfiguration["scan_type"].find(',') < 0):
            toolName = runConfiguration["scan_type"]
        else:
            listOfScans = runConfiguration["scan_type"].split(', ')
            numOfScans = len(listOfScans)
            toolName = listOfScans[0]

        #run = database.getRun(runName)
        run = RunConfig.Run_Config()
        run.load_from_db(runName, database)

        # tool = database.getTool(toolName)
        tool = ToolConfig.Tool_Config()
        tool.load_from_db(toolName, database)

        tool_name = tool.get_name()
        # Remove "," from the options and arguments
        # tool_opt_and_arg = tool["tool_option_and_argument"].translate({ord(','): None})
        tool_opt_and_arg = tool.get_opt_and_arg().translate({ord(','): None})

        #whitelist = run["whitelist"]
        whitelist = run.get_target().get_whitelist()
        whitelistNoCommas = whitelist.translate({ord(','): None})

        # nmap -T4 -A -p 1-100 -oX result.xml -oN - 45.33.32.156
        # nmap -T4 -A -p 1-100 -oX - 45.33.32.156
        # tool_name + tool_option_and_argument (without commas) + whitelist
        runCommand = f'{tool_name} {tool_opt_and_arg} {whitelistNoCommas}'
        print(runCommand)

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future = executor.submit(self.nmapThreadFunction, runCommand)
        #     return_value = future.result()
        global nmapEvent

        event = threading.Event()
        nmapEvent = event
        nmapThread = threading.Thread(target=self.nmapThreadFunction, args=(runCommand, mainUi, tool, toolName, runName, db))
        nmapThread.start()

        mainUi.scans_tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("Now Running..."))
        mainUi.scans_tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(toolName))
        mainUi.scans_tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem("1"))

        print("nmap thread started")


    def updateScanTable(self, scan_result, mainUi):
        print('here update scan table')
        #infoArray = [startTime, endTime, scannedIp, successOrFailure]
        infoArray = scan_result.get_results()

        mainUi.scans_tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("Finished."))
        i = 3

        for x in range(4):
            mainUi.scans_tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(infoArray[x]))
            i = i + 1


    def nmapThreadFunction(self, command, mainUi, tool, toolName, runName, db):
        child_process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE)
        global nmapProcess
        global nmapProcessId

        nmapProcess = child_process
        nmapProcessId = child_process.pid

        child_process.wait()

        global nmapEvent
        print(nmapEvent.isSet())

        if not nmapEvent.is_set():
            subprocess_return = child_process.stdout.read()
            print(subprocess_return)

            xmlTree = ET.ElementTree(ET.fromstring(subprocess_return))

            # Store in database
            scan_result = self.newScanObj(toolName, runName, xmlTree, subprocess_return, db, tool)
            # update GUI
            self.updateScanTable(scan_result, mainUi)
            self.updateOutputDataSpecification(xmlTree, tool, mainUi)



    def newScanObj(self, scan_name, run_name, subprocessXml, subprocessString, db, tool):
        print("here create new scan result obj and add to db")
        # Read Start Time, End Time, Scanned IPs, Success/Failure from XML file produced by nmap
        root = subprocessXml.getroot()

        startTime = root.get('startstr')
        endTime = root.find('runstats').find('finished').get('timestr')
        scannedIp = root.find('hosthint').find('address').get('addr')
        successOrFailure = root.find('runstats').find('finished').get('exit')

        # create scan result object using 'root' results
        scan_result = ScanResult.Scan_Result(scan_name, run_name, startTime, endTime, scannedIp, successOrFailure, subprocessString)

        outputData = tool.get_output_spec()

        # add formatted output to scan result object
        formatted_outputData = self.parseXml(root, outputData)
        scan_result.set_formatted_output(formatted_outputData)

        db.createNewScan(scan_result)  # update database

        return scan_result


    def updateOutputDataSpecification(self, xmlTree, tool, mainUi):
        print('here output data specification')
        #outputData = tool["tool_output_specification"]
        outputData = tool.get_output_spec()


        root = xmlTree.getroot()

        outputElement = root.find('host').find(outputData)
        outputString = ET.tostring(outputElement, encoding="unicode")
        formatted_outputString = self.parseXml(root, outputData)
        print(outputString)

        mainUi.scanOutputData_textEdit.insertPlainText(formatted_outputString)


    def parseXml(self, root, outputData):
        outputStr = ""
        outputElement = root.find('host').find(outputData)
        for elem in outputElement:
            outputStr += str(elem.tag) + ": " + str(elem.attrib)
            outputStr += '\n'
            for subelem in elem:
                outputStr += str(subelem.tag) + ":" + '\n'
                key_list = list(subelem.attrib.keys())
                val_list = list(subelem.attrib.values())
                for i in range(len(subelem.attrib)):
                    outputStr += "    " + str(key_list[i]) + ": " + str(val_list[i])
                    outputStr += '\n'

        return outputStr

    def terminateNmap(self, mainUi):
        global nmapEvent

        nmapEvent.set()

        mainUi.scans_tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("Aborted."))

    def pauseNmap(self, mainUi):
        global nmapProcess
        # global nmapProcessId

        # print(nmapProcessId)
        # os.kill(int(nmapProcessId), signal.SIGSTOP)

        print(nmapProcess)
        print(nmapProcess.poll())

        mainUi.scans_tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("Paused."))
