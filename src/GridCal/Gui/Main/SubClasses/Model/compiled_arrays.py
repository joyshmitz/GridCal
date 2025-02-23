# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
import numpy as np
from PySide6 import QtCore
from matplotlib import pyplot as plt

from GridCal.Gui.pandas_model import PandasModel
from GridCal.Gui.Main.SubClasses.Server.server import ServerMain
import GridCal.Gui.gui_functions as gf

from GridCalEngine.enumerations import EngineType, BranchImpedanceMode
from GridCalEngine.Compilers.circuit_to_data import compile_numerical_circuit_at


class CompiledArraysMain(ServerMain):
    """
    Diagrams Main
    """

    def __init__(self, parent=None):
        """

        @param parent:
        """

        # create main window
        ServerMain.__init__(self, parent=parent)

        # array modes
        self.ui.arrayModeComboBox.addItem('real')
        self.ui.arrayModeComboBox.addItem('imag')
        self.ui.arrayModeComboBox.addItem('abs')
        self.ui.arrayModeComboBox.addItem('complex')

        # Buttons
        self.ui.compute_simulation_data_pushButton.clicked.connect(self.update_islands_to_display)
        self.ui.plotArraysButton.clicked.connect(self.plot_simulation_objects_data)
        self.ui.copyArraysButton.clicked.connect(self.copy_simulation_objects_data)
        self.ui.copyArraysToNumpyButton.clicked.connect(self.copy_simulation_objects_data_to_numpy)

        # tree clicks
        self.ui.simulationDataStructuresTreeView.clicked.connect(self.view_simulation_objects_data)

    def view_simulation_objects_data(self, index):
        """
        Simulation data structure clicked
        """

        tree_mdl = self.ui.simulationDataStructuresTreeView.model()
        item = tree_mdl.itemFromIndex(index)
        path = gf.get_tree_item_path(item)

        if len(path) == 2:
            group_name = path[0]
            elm_type = path[1]

            island_idx = self.ui.simulation_data_island_comboBox.currentIndex()

            if island_idx > -1 and self.circuit.valid_for_simulation():
                # elm_type = self.ui.simulationDataStructuresTreeView.selectedIndexes()[0].data(role=QtCore.Qt.ItemDataRole.DisplayRole)

                df = self.calculation_inputs_to_display[island_idx].get_structure(elm_type)

                mdl = PandasModel(df)

                self.ui.simulationDataStructureTableView.setModel(mdl)

            else:
                self.ui.simulationDataStructureTableView.setModel(None)
        else:
            self.ui.simulationDataStructureTableView.setModel(None)

    def copy_simulation_objects_data(self):
        """
        Copy the arrays of the compiled arrays view to the clipboard
        """
        mdl = self.ui.simulationDataStructureTableView.model()
        mode = self.ui.arrayModeComboBox.currentText()
        mdl.copy_to_clipboard(mode=mode)

    def copy_simulation_objects_data_to_numpy(self):
        """
        Copy the arrays of the compiled arrays view to the clipboard
        """
        mdl = self.ui.simulationDataStructureTableView.model()
        mode = 'numpy'
        mdl.copy_to_clipboard(mode=mode)

    def plot_simulation_objects_data(self):
        """
        Plot the arrays of the compiled arrays view
        """
        mdl = self.ui.simulationDataStructureTableView.model()
        data = mdl.data_c

        # declare figure
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        if mdl.is_2d():
            ax1.spy(data)

        else:
            if mdl.is_complex():
                ax1.scatter(data.real, data.imag)
                ax1.set_xlabel('Real')
                ax1.set_ylabel('Imag')
            else:
                arr = np.arange(data.shape[0])
                ax1.scatter(arr, data)
                ax1.set_xlabel('Position')
                ax1.set_ylabel('Value')

        fig.tight_layout()
        plt.show()

    def recompile_circuits_for_display(self):
        """
        Recompile the circuits available to display
        :return:
        """
        if self.circuit is not None:

            engine = self.get_preferred_engine()

            if engine == EngineType.GridCal:

                if self.ui.apply_impedance_tolerances_checkBox.isChecked():
                    branch_impedance_tolerance_mode = BranchImpedanceMode.Upper
                else:
                    branch_impedance_tolerance_mode = BranchImpedanceMode.Specified

                numerical_circuit = compile_numerical_circuit_at(
                    circuit=self.circuit,
                    t_idx=None,
                    branch_tolerance_mode=branch_impedance_tolerance_mode,
                    use_stored_guess=self.ui.use_voltage_guess_checkBox.isChecked(),
                    control_taps_phase=self.ui.control_tap_phase_checkBox.isChecked(),
                    control_taps_modules=self.ui.control_tap_modules_checkBox.isChecked(),
                    control_remote_voltage=self.ui.control_remote_voltage_checkBox.isChecked(),
                )
                calculation_inputs = numerical_circuit.split_into_islands()
                self.calculation_inputs_to_display = calculation_inputs

            elif engine == EngineType.Bentayga:
                import GridCalEngine.Compilers.circuit_to_bentayga as ben
                self.calculation_inputs_to_display = ben.get_snapshots_from_bentayga(self.circuit)

            elif engine == EngineType.NewtonPA:
                import GridCalEngine.Compilers.circuit_to_newton_pa as ne
                self.calculation_inputs_to_display = ne.get_snapshots_from_newtonpa(self.circuit)

            else:
                # fallback to gridcal
                numerical_circuit = compile_numerical_circuit_at(circuit=self.circuit, t_idx=None)
                calculation_inputs = numerical_circuit.split_into_islands()
                self.calculation_inputs_to_display = calculation_inputs

            return True
        else:
            self.calculation_inputs_to_display = None
            return False

    def update_islands_to_display(self):
        """
        Compile the circuit and allow the display of the calculation objects
        :return:
        """
        self.recompile_circuits_for_display()
        self.ui.simulation_data_island_comboBox.clear()
        lst = ['Island ' + str(i) for i, circuit in enumerate(self.calculation_inputs_to_display)]
        self.ui.simulation_data_island_comboBox.addItems(lst)
        if len(self.calculation_inputs_to_display) > 0:
            self.ui.simulation_data_island_comboBox.setCurrentIndex(0)
