import tkinter as tk
from tkinter import ttk
import serial

class SerialMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Monitor")

        # Créer une variable de type chaîne pour stocker le port COM sélectionné
        self.selected_port = tk.StringVar()

        # Créer une liste des ports COM disponibles
        self.available_ports = self.get_available_ports()
        print (self.available_ports)
        # Créer le menu déroulant pour sélectionner le port COM
        self.port_label = tk.Label(root, text="Sélectionnez le port COM:")
        self.port_selector = ttk.Combobox(root, textvariable=self.selected_port, values=self.available_ports)
        try:
            self.port_selector.set(self.available_ports[0])  # Définir le premier port comme valeur par défaut
        except:
            print ("no port com available")
        
        # Créer le bouton de connexion
        self.connect_button = tk.Button(root, text="Connecter", command=self.connect_serial)

        # Créer la zone de texte pour afficher les données du port COM
        self.text_output = tk.Text(root, wrap="word", height=10, width=40)
        self.text_output.config(state=tk.DISABLED)  # Désactiver l'édition de la zone de texte

        # Placer les widgets à l'aide du gestionnaire de grille
        self.port_label.grid(row=0, column=0, padx=10, pady=10)
        self.port_selector.grid(row=0, column=1, padx=10, pady=10)
        self.connect_button.grid(row=0, column=2, padx=10, pady=10)
        self.text_output.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Créer l'entrée texte pour saisir les commandes hexadécimales
        self.command_entry = tk.Entry(root, width=20)
        self.send_button = tk.Button(root, text="Envoyer", command=self.send_command)

        # Placer l'entrée texte et le bouton dans la grille
        self.command_entry.grid(row=2, column=0, padx=10, pady=10)
        self.send_button.grid(row=2, column=1, padx=10, pady=10)

        # Créer la liste d'entrées prédéfinies
        self.predefined_commands = ["f0a50000", "f0a51018", "f0a51019", "f0a5ffff"]

        # Créer la liste déroulante pour les commandes prédéfinies
        self.command_combobox = ttk.Combobox(root, values=self.predefined_commands)
        self.command_combobox.set("Sélectionnez une commande")  # Texte initial

        # Créer le bouton pour envoyer la commande sélectionnée
        self.send_predefined_button = tk.Button(root, text="Envoyer la commande sélectionnée", command=self.send_predefined_command)

        # Placer les widgets dans la grille
        self.command_combobox.grid(row=3, column=0, padx=10, pady=10)
        self.send_predefined_button.grid(row=3, column=1, padx=10, pady=10)

    def send_predefined_command(self):
        """Envoyer la commande prédéfinie sélectionnée sur le port COM."""
        if hasattr(self, 'ser') and self.ser.is_open:
            command_str = self.command_combobox.get()
            try:
                # Convertir la chaîne hexadécimale en bytes
                command_bytes = bytes.fromhex(command_str)

                # Envoyer la commande sur le port série
                self.ser.write(command_bytes)

                # Afficher la commande envoyée dans la zone de texte
                self.text_output.config(state=tk.NORMAL)
                self.text_output.insert(tk.END, f"Commande envoyée: {command_str}\n")
                self.text_output.config(state=tk.DISABLED)
            except ValueError:
                messagebox.showerror("Erreur de commande", "La commande n'est pas une chaîne hexadécimale valide.")
        else:
            messagebox.showerror("Erreur de port COM", "Aucun port COM ouvert")

    def send_command(self):
        """Envoyer la commande hexadécimale saisie sur le port COM."""
        if hasattr(self, 'ser') and self.ser.is_open:
            command_str = self.command_entry.get()
            try:
                # Convertir la chaîne hexadécimale en bytes
                command_bytes = bytes.fromhex(command_str)

                # Envoyer la commande sur le port série
                self.ser.write(command_bytes)

                # Effacer l'entrée après l'envoi
                self.command_entry.delete(0, 'end')

                # Afficher la commande envoyée dans la zone de texte
                self.text_output.config(state=tk.NORMAL)
                self.text_output.insert(tk.END, f"Commande envoyée: {command_str}\n")
                self.text_output.config(state=tk.DISABLED)
            except ValueError:
                messagebox.showerror("Erreur de commande", "La commande n'est pas une chaîne hexadécimale valide.")
        else:
            messagebox.showerror("Erreur de port COM", "Aucun port COM ouvert")

    def get_available_ports(self):
        """Retourne une liste des ports COM disponibles."""
        ports = ["COM{}".format(i + 1) for i in range(256)]
        available_ports = []
        for port in ports:
            try:
                ser = serial.Serial(port)
                ser.close()
                available_ports.append(port)
            except (OSError, serial.SerialException):
                pass
        return available_ports

    def connect_serial(self):
        """Établit la connexion série avec le port sélectionné et commence à lire les données."""
        selected_port = self.selected_port.get()
        baudrate = 9600  # Vous pouvez ajuster la vitesse de communication selon vos besoins

        try:
            # Ouvrir la connexion série
            self.ser = serial.Serial(selected_port, baudrate, timeout=1)

            # Effacer le contenu précédent de la zone de texte
            self.text_output.config(state=tk.NORMAL)
            self.text_output.delete(1.0, tk.END)
            self.text_output.config(state=tk.DISABLED)

            # Démarrer la lecture des données en arrière-plan
            self.root.after(100, self.read_serial)
        except serial.SerialException as e:
            # Afficher une boîte de dialogue d'erreur si la connexion échoue
            tk.messagebox.showerror("Erreur de connexion", str(e))

    def read_serial(self):
        """Lire les données du port série et les afficher dans la zone de texte."""
        if hasattr(self, 'ser') and self.ser.is_open:
            data = self.ser.readline().decode('utf-8').strip()
            if data:
                self.text_output.config(state=tk.NORMAL)
                self.text_output.insert(tk.END, f"{data}\n")
                self.text_output.config(state=tk.DISABLED)
        # Continuer la lecture en arrière-plan
        self.root.after(100, self.read_serial)

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.mainloop()
