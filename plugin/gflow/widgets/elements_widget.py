from functools import partial

from PyQt5.QtWidgets import QGridLayout, QPushButton, QVBoxLayout, QWidget
from qgis.core import Qgis

from gflow.core.elements import ELEMENTS


class ElementsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.element_buttons = {}
        for element in ELEMENTS:
            if element in ("Aquifer", "Domain"):
                continue
            button = QPushButton(element)
            button.clicked.connect(partial(self.gflow_element, element_type=element))
            button.setEnabled(False)
            self.element_buttons[element] = button

        elements_layout = QVBoxLayout()
        elements_grid = QGridLayout()
        n_row = -(len(self.element_buttons) // -2)  # Ceiling division
        for i, button in enumerate(self.element_buttons.values()):
            if i < n_row:
                elements_grid.addWidget(button, i, 0)
            else:
                elements_grid.addWidget(button, i % n_row, 1)
        elements_layout.addLayout(elements_grid)
        elements_layout.addStretch()
        self.setLayout(elements_layout)

    def enable_element_buttons(self) -> None:
        """
        Enables or disables the element buttons.

        Parameters
        ----------
        state: bool
            True to enable, False to disable

        """
        for button in self.element_buttons.values():
            button.setEnabled(True)

    def gflow_element(self, element_type: str) -> None:
        """
        Create a new GFLOW element input layer.

        Parameters
        ----------
        element_type: str
            Name of the element type.

        """
        klass = ELEMENTS[element_type]
        names = self.parent.selection_names()

        # Get the crs. If not a CRS in meters, abort.
        try:
            crs = self.parent.crs
        except ValueError:
            return

        try:
            element = klass.dialog(self.parent.path, crs, self.parent.iface, names)
        except ValueError as e:
            msg = str(e)
            self.parent.message_bar.pushMessage("Error", msg, level=Qgis.Critical)
            return

        if element is None:  # dialog cancelled
            return
        # Write to geopackage
        element.write()
        # Add to QGIS and dataset tree
        self.parent.add_element(element)
