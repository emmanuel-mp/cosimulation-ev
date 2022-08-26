"""
Version O.1
Vincent CHEVRIER ENSEM
"""

import ctypes
import platform
import os
from PyQt5.QtWidgets import QApplication
from fmpy.gui.MainWindow import MainWindow
from fmpy import *
from fmpy.fmi2 import FMU2Slave
import shutil

class myFMU():
    def __init__(self,fmupath:str):
        """

        :param fmupath: path to FMU
        """
        # todo: separate fields according role (config, simul, etc
        self.__fmuP=fmupath
        self.__fmuInstance=None
        self.__model_description =  read_model_description(fmupath,validate=False)
        self.__vrs= {}
        for variable in self.__model_description.modelVariables:
            self.__vrs[variable.name] = variable.valueReference
        self.__unzipdir=None

    def info(self):
        dump(self.__fmuP)
        print("more info")
        for variable in self.__model_description.modelVariables:  # iterate over the variables
            # if variable.causality == 'parameter':                    # and print the names of all parameters
            print('%-25s %s %s' % (variable.causality, variable.name, variable.start))


    def gui(self):
        """ call fmpy gui"""
        import os
        import platform
        if os.name == 'nt' and int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)

        cline = []
        app = QApplication(cline)
        window = MainWindow()
        window.show()
        window.load(self.__fmuP)
        sys.exit(app.exec_())

    def init(self, start_time,varvalues):
        """ extract fmu, and do useful steps to make fmu simulable
        Parameters
        ----------
        start_time : initial time double.
        varvalues : a list of couple VarNAme (string) and its value
        """
        # extract the FMU

        self.__unzipdir= extract(self.__fmuP)

        # see https://github.com/CATIA-Systems/FMPy/blob/3841175f6c08710b723d3628379eb2e3a20a5acf/fmpy/fmi2.py#L489
        fmu = FMU2Slave(guid=self.__model_description.guid,
                        unzipDirectory=self.__unzipdir,
                        modelIdentifier=self.__model_description.coSimulation.modelIdentifier,
                        instanceName='instance1')
        self.__fmuInstance=fmu

        # initialize
        fmu.instantiate()
        fmu.setupExperiment(startTime=start_time)
        if varvalues:
            for v in varvalues:
                var, val = v
       #         print(self.get(var))
                self.set(var, val)
         #       print(self.get(var))
        fmu.enterInitializationMode()
        fmu.exitInitializationMode()


    def set(self, var, val):
        """
        set value to variable
        syntax: see below
        Parameters
        ----------
        variables : list of var string or a string
        val : dictionnary of varname (string) , value or a list of value OR a single value
        Returns
        -------
        None.
        """
        if isinstance(var,list) and isinstance(val,list):
            for v,value in zip(var,val):
                self.__fmuInstance.setReal([self.__vrs[v]], [value])
        elif isinstance(var,list) and isinstance(val,dict):
            for v in var:
                self.__fmuInstance.setReal([self.__vrs[v]], [val[v]])
        elif isinstance(var,str) and isinstance(val,dict):
            self.__fmuInstance.setReal([self.__vrs[var]], [val[var]])
        else:
            self.__fmuInstance.setReal([self.__vrs[var]], [val])
            
            
    def setB(self, var, val):
        """
        set value to variable
        syntax: see below
        Parameters
        ----------
        variables : list of var string or a string
        dico : dictionnary of varname (string) , value or a list of value OR a single value
        Returns
        -------
        None.
        """

        if isinstance(var,list) and isinstance(val,list):
            for v,value in var,val:
                self.__fmuInstance.setBoolean([self.__vrs[v]], [value])
        elif isinstance(var,list) and isinstance(val,dict):
            for v in var:
                self.__fmuInstance.setBoolean([self.__vrs[v]], [val[v]])
        elif isinstance(var,str) and isinstance(val,dict):
            self.__fmuInstance.setBoolean([self.__vrs[var]], [val[var]])
        else:
            self.__fmuInstance.setBoolean([self.__vrs[var]], [val])

    def getB(self, var, dico=None):
        '''
        get a value or a list of values
        :param var  (str) or list of str: variable(s) name(s)
        :param dico (dict): if any the dict in which put values
        :return:
        values requested
        '''
        if isinstance(var, str):
            val = self.__fmuInstance.getBoolean([self.__vrs[var]])[0]
            if dico:
                dico[var] = val
            return val
        else:
            res = []
            for v in var:
                value = self.__fmuInstance.getBoolean([self.__vrs[v]])[0]
                if dico:
                    dico[v] = value
                res.append(value)
            return res
    def get(self, var, dico=None):
        '''
        get a value or a list of values
        :param var  (str) or list of str: variable(s) name(s)
        :param dico (dict): if any the dict in which put values
        :return:
        values requested
        '''
        if isinstance(var,str):
            val =self.__fmuInstance.getReal([self.__vrs[var]])[0]
            if dico:
                dico[var]=val
            return val
        else:
            res=[]
            for v in var:
                value = self.__fmuInstance.getReal([self.__vrs[v]])[0]
                if dico:
                    dico[v] = value
                res.append(value)
            return res
    def terminate(self):
        """
        clean files, etc.
        :return:
        """
        self.__fmuInstance.terminate()
        self.__fmuInstance.freeInstance() #unload the shared library (apparently) -> no need to call freeLibrary

        shutil.rmtree(self.__unzipdir, ignore_errors=True)

    def doStep(self, time, step_size):
        '''
        basic to call dostep
        need to be improved
        :param time:
        :param step_size:
        :return:
        '''
        self.__fmuInstance.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)
