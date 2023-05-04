import sys
import os
import shutil
from PyQt5 import QtWidgets, QtCore
import subprocess


# PING 

#Lista de direcciones IP de los hosts a los que se les va a hacer ping
HOSTS = ["192.168.1.6", "192.168.1.7", "192.168.1.5"]

class ExecuteBlurring:
    def __init__(self) -> None:
        pass

    #Obtener hosts disponibles
    def getHosts(self):
        # #Testing
        # hosts = [1,1,1]
        # num_hosts_available = sum(1 for value in hosts if value)
        # return num_hosts_available, hosts

        #Inicializar una lista que indique si los hosts están disponibles o no
        available_hosts = [0,0,0]

        #Iterar por cada host y hacer ping
        for i in range(len(HOSTS)):
            host = HOSTS[i]
            ping_output = subprocess.run(["ping", "-c", "1", "-W", "1", "-i", "0.2", host], capture_output=True)
            if ping_output.returncode == 0: #Si el resultado del ping es 0, significa que el host está disponible
                available_hosts[i] = 1
            else: #Si el resultado del ping es diferente de 0, significa que el host no está disponible
                available_hosts[i] = 0

        #Contar cuántos hosts están disponibles
        num_hosts_available = sum(1 for value in available_hosts if value)
        return num_hosts_available, available_hosts
    
    #Obtener la distribucion de los procesos
    def getWeights(self,nMasks):
        n, hostsAvailable = self.getHosts()
        nMasks = int(nMasks)
        n = int(n)
        nMasksItu = (nMasks // n) * hostsAvailable[2] #Dividir las máscaras entre los hosts disponibles y asignarlas proporcionalmente
        nMasksReus = (nMasks // n) * hostsAvailable[1]
        nMasksBoba = nMasks - nMasksItu - nMasksReus #Las máscaras que sobren se asignan al tercer host disponible
        return [nMasksBoba, nMasksReus, nMasksItu]

    #Actualizar el writefile, archivo que contendra la distribucion de procesos
    def writefile(self, nMasks):
        masksAssignment = self.getWeights(nMasks)
        with open("machinefile", "w") as file:
            for i in range(len(masksAssignment)):
                slots = masksAssignment[i] # Slots asignados
                if slots != 0:
                    # Escribir en el archivo un nuevo host con el formato: ub0 slots=14 max_slots=14
                    file.write(f'ub{i} slots={slots} max_slots={slots}\n')
                    print(f'ub{i} slots={slots} max_slots={slots}')

    # Comando para ejecutar con el writefile actualizado
    def execute(self,nMasks):
        self.writefile(nMasks) #Actualizar writefile



# GUI
class DragDropWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Se establece que el widget puede aceptar elementos que se arrastren y suelten.
        self.setAcceptDrops(True)
        # Se define el estilo del widget.
        self.setStyleSheet("background-color: white; border: 2px dashed black;")
        # Se agrega un QLabel que indica al usuario que arrastre y suelte el archivo en el widget.
        self.label = QtWidgets.QLabel("Arrastra aquí el archivo que quieres copiar", self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        # Se agrega un QVBoxLayout al widget para ubicar el QLabel en el centro del widget.
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    # Este método se llama cuando un elemento se arrastra y entra en el widget.
    # Se verifica si se está arrastrando una URL (archivo) y se acepta la acción propuesta.
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # Este método se llama cuando un elemento se suelta dentro del widget.
    # Se obtiene la ruta del archivo y se actualiza el texto del QLabel con la ruta.
    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.label.setText(file_path)
        self.file_path = file_path

# Se define la clase MainWindow que hereda de QMainWindow.
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Se establece el título y el tamaño fijo de la ventana principal.
        self.setWindowTitle("Copiar archivo")
        self.setFixedSize(500, 250)
        # Se define un QWidget que será el widget central de la ventana principal.
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        # Se agrega un QVBoxLayout al widget central para ubicar los elementos en orden vertical.
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)
        # Se agrega el widget DragDropWidget al QVBoxLayout para que el usuario pueda seleccionar el archivo a copiar.
        self.drag_drop_widget = DragDropWidget(self)
        main_layout.addWidget(self.drag_drop_widget)
        
        # Se agrega un QSpinBox al QVBoxLayout para que el usuario pueda ingresar el número de máscaras a aplicar al archivo.
        self.input_widget = QtWidgets.QWidget()
        input_layout = QtWidgets.QHBoxLayout()
        self.input_widget.setLayout(input_layout)
        self.input_label = QtWidgets.QLabel("Mascaras: ")
        input_layout.addWidget(self.input_label)
        self.input_number = QtWidgets.QSpinBox()
        input_layout.addWidget(self.input_number)
        main_layout.addWidget(self.input_widget)
        
        # Se agrega un QHBoxLayout al QVBoxLayout para ubicar los botones de copiar y limpiar.
        button_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(button_layout)
        # Se define un QPushButton para iniciar el proceso de copiado y se conecta a un método de la clase.
        copy_button = QtWidgets.QPushButton("Iniciar procesamiento")
        copy_button.clicked.connect(self.copy_file)
        button_layout.addWidget(copy_button)
        clear_button = QtWidgets.QPushButton("Limpiar")
        clear_button.clicked.connect(self.clear)
        button_layout.addWidget(clear_button)

def copy_file(self):
    # Verifica que exista el widget para arrastrar y soltar archivos
    if hasattr(self, "drag_drop_widget"):
        # Obtiene la ruta del archivo arrastrado y soltado
        file_path = self.drag_drop_widget.file_path
        # Establece la ruta de destino como la carpeta del archivo actual y el nombre del archivo arrastrado
        destination_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(file_path))
        # Verifica que haya un archivo seleccionado
        if file_path:
            try:
                # Copia el archivo a la ruta de destino con el comando de shell 'cp'
                command = "sudo cp "+file_path+" "+destination_path
                os.system(command)
                # Muestra una ventana de diálogo indicando que se copió correctamente el archivo
                QtWidgets.QMessageBox.information(
                    self,
                    "Copiado",
                    f"Se ha copiado correctamente el archivo {file_path} en la ruta {destination_path}."
                )
                # Obtiene el número de máscaras seleccionado y lo imprime en la consola
                print("Mascaras seleccionadas: ",self.input_number.text())
                # Crea un objeto de la clase ExecuteBlurring y ejecuta el método execute con el número de máscaras como argumento
                exec = ExecuteBlurring()
                exec.execute(self.input_number.text())
            # Si ocurre una excepción durante la copia del archivo, muestra una ventana de diálogo indicando el error
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al copiar el archivo. {str(e)}"
                )
        # Si no se ha seleccionado un archivo, muestra una ventana de diálogo de advertencia
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Atención",
                "Selecciona un archivo para copiar."
            )

def clear(self):
    # Si existe el widget para arrastrar y soltar archivos, establece el texto de la etiqueta a su valor inicial y elimina la ruta del archivo seleccionado
    if hasattr(self, "drag_drop_widget"):
        self.drag_drop_widget.label.setText("Arrastra aquí el archivo que quieres copiar")
        self.drag_drop_widget.file_path = ""
    # Si existe el widget para editar la ruta de destino, establece su texto a una cadena vacía
    if hasattr(self, "path_edit"):
        self.path_edit.setText("")


if __name__ == "__main__":
    # Crea una aplicación de PyQt5
    app = QtWidgets.QApplication(sys.argv)
    # Crea una ventana principal de la aplicación
    main_window = MainWindow()
    # Muestra la ventana principal
    main_window.show()
    # Inicia la aplicación y espera a que el usuario cierre la ventana
    sys.exit(app.exec_())
