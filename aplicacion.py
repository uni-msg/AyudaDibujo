import cv2
import numpy as np
#Empleado para una interfaz grafica
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# ------------------------------
# Clase principal de la aplicación
# ------------------------------
class ContourApp:
    def __init__(self, root):
        #Variables necesarias para la generacion de la interfaz
        self.root = root
        self.root.title(" Sketch Tool ")
        self.root.geometry("1100x600")
        self.root.configure(bg="#202020")

        # Variables para las imagenes
        self.img_original = None
        self.img_alterada = None
        self.historial = [] #Ampliacion para control de errores
        self.indice_historial = -1 #Indica en que parte del historial estoy
        
        # Paneles de interface
        self.panel_alterada = None
        self.panel_imagen = None
        self.panel_aux = None

        # Interfaz grafica, mas sencilla para los usuarios
        self.crear_interfaz()

    def crear_interfaz(self):
        # ------------------------------- Botones principales a la izquierda -----------------------------
        frame_controles = tk.Frame(self.root, bg="#303030", padx=10, pady=10)
        frame_controles.pack(side="left", fill="y")
        
        #colocamos en los controles el boton para cargar una imagen, invoca a cargar imagen
        btn_cargar = tk.Button(frame_controles, text=" Cargar Imagen ", command=self.cargar_imagen, width=20)
        btn_cargar.pack(pady=10)
        
        # ---------------------------------------- FUNCIONALIDADES --------------------------------------------- #
        #Extraer la paleta de colores de la imagen original
        btn_paleta = tk.Button(frame_controles, text=" Extraer Paleta ", command=self.extraer_paleta_colores, width=20)
        btn_paleta.pack(pady=10)
        
        #Trabajaremos con una zona de Interes
        btn_roi = tk.Button(frame_controles, text=" Seleccionar Región ", command=self.seleccionar_region_interes, width=20)
        btn_roi.pack(pady=10)
        
        #Alteramos los valores HSV
        btn_cambia_hsv = tk.Button(frame_controles, text=" Modificar HSV ", command=self.cambios_hsv, width=20)
        btn_cambia_hsv.pack(pady=10)
        
        #Alterar algun color con un rango especifico
        btn_colores_alt = tk.Button(frame_controles, text=" Alterar colores ", command=self.rango_colores, width=20)
        btn_colores_alt.pack(pady=10)
        
        #Alterar algun color con un rango especifico
        btn_boceto = tk.Button(frame_controles, text=" Boceto figura geometrica ", command=self.dibujar_formas, width=20)
        btn_boceto.pack(pady=10)
        
        #Test
        btn_test = tk.Button(frame_controles, text=" Area Total ", command=self.cerrar_contornos, width=20)
        btn_test.pack(pady=10)
        
        #Sacar controno
        btn_contorno = tk.Button(frame_controles, text=" Contorno ", command=self.extraer_contornos, width=20)
        btn_contorno.pack(pady=10)
        
        #Combinar imagenes
        btn_combinar_img = tk.Button(frame_controles, text=" Combinar imagenes ", command=self.combinar_imagen, width=20)
        btn_combinar_img.pack(pady=10)
        
        # ---------------------------------------- CAMBIOS SOBRE LAS IMAGENES --------------------------------------------- #
        #Salir de la aplicacion
        btn_salir = tk.Button(frame_controles, text=" Salir", command=self.root.quit, width=20)
        btn_salir.pack(side="bottom", pady=10)
        
        #Toma la imagen alterada y la guarda como original
        btn_establecer_org = tk.Button(frame_controles, text=" Establecer imagen ", command=self.establecer_imagen_original, width=20)
        btn_establecer_org.pack(side="bottom", pady=10)
        
        #Quita el roi y cualquier filtro aplicado
        btn_limpiar = tk.Button(frame_controles, text=" Limpiar cambios ", command=self.limpiar_cambios, width=20)
        btn_limpiar.pack(side="bottom", pady=10)
        
        #colocamos en los controles el boton para guardar una imagen, invoca a almanecar umagen
        btn_almacenar_alt = tk.Button(frame_controles, text=" Almacenar Imagen ", command=self.almacenar_imagen, width=20)
        btn_almacenar_alt.pack(side="bottom",pady=10)
        
        # ------------------------- Panles de las imagenes ----------------------------------
        # === CONTENEDOR PRINCIPAL DE IMÁGENES ===
        frame_imagenes = tk.Frame(self.root, bg="#202020")
        frame_imagenes.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        # === SUBFRAME SUPERIOR (PALETA DE COLORES + BOTONES HISTORIAL) ===
        frame_superior = tk.Frame(frame_imagenes, bg="#202020")
        frame_superior.pack(side="top", fill="x", pady=10)

        # Contenedor horizontal para el panel auxiliar y los botones
        frame_aux_botones = tk.Frame(frame_superior, bg="#202020")
        frame_aux_botones.pack(fill="x", padx=10, pady=5)

        # Panel auxiliar (que crece cuando se le añaden elementos)
        self.panel_aux = tk.Label(frame_aux_botones, bg="#202020")
        self.panel_aux.pack(side="left", fill="x", expand=True)

        # Botones comprimidos al lado derecho
        btn_rehacer = tk.Button(frame_aux_botones, text=" Adelante =>", command=self.rehacer)
        btn_rehacer.pack(side="right", padx=5)
        
        btn_deshacer = tk.Button(frame_aux_botones, text="<= Atrás ", command=self.deshacer)
        btn_deshacer.pack(side="right", padx=5)

        # === SUBFRAME INFERIOR (IMÁGENES ALTERADA Y ORIGINAL) ===
        frame_inferior = tk.Frame(frame_imagenes, bg="#202020")
        frame_inferior.pack(side="top", expand=True, fill="both")

        # Imagen alterada (debe ocupar casi todo el espacio disponible)
        self.panel_alterada = tk.Label(frame_inferior, bg="#484848")
        self.panel_alterada.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        # Imagen original (más compacta, fija a la derecha)
        self.panel_imagen = tk.Label(frame_inferior, bg="#202020")
        self.panel_imagen.pack(side="right", fill="y", padx=5, pady=5)

    #Altera el puntero y el array de los datos añadiendo datos al historial
    def guardar_en_historial(self):
        limit = 5
        if self.img_alterada is None:
            return
        
        if self.indice_historial < len(self.historial) - 1: #Cortamos el historial ya que se ha modificado
            self.historial = self.historial[:self.indice_historial + 1]

        self.historial.append(self.img_alterada.copy())
        if len(self.historial) > limit: #Metemos nuevos y sacamos el primero si se llena el historial
            self.historial.pop(0)
        self.indice_historial = len(self.historial) - 1
        
    #Retrocedemos cambios
    def deshacer(self):
        if self.indice_historial > 0:
            self.indice_historial -= 1
            self.img_alterada = self.historial[self.indice_historial].copy()
            self.mostrar_imagen(self.img_alterada, self.panel_alterada)
        else:
            messagebox.showinfo("Historial", "No hay más estados anteriores.")
    
    #Rehacer los cambios
    def rehacer(self):
        if self.indice_historial < len(self.historial) - 1:
            self.indice_historial += 1
            self.img_alterada = self.historial[self.indice_historial].copy()
            self.mostrar_imagen(self.img_alterada, self.panel_alterada)
        else:
            messagebox.showinfo("Historial", "No hay más estados siguientes.")

    #Toma de la imagen a eleccion, se guardara en las variables de la clase
    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not ruta:
            return

        #Guardamos la imagen original para usarse para las herramientas
        self.img_original = cv2.imread(ruta)
        self.img_alterada = self.img_original.copy()
        if self.img_original is None:
            #Mensaje de error
            messagebox.showerror("Error", "No se pudo cargar la imagen.")
            return
        
        #Mostramos la image que se guardo en el cuadro original y en el panel de trabajo
        self.mostrar_imagen(self.img_original,self.panel_imagen, (300,250))
        self.mostrar_imagen(self.img_alterada,self.panel_alterada)
        
    #Convierte la imagen de CV2 a Tinker
    def mostrar_imagen(self, img_cv, panel=None, size=(600, 500)):
        #Lo convierte a rgb
        if len(img_cv.shape) == 2:
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        
        img_pil = Image.fromarray(img_rgb)
        img_pil = img_pil.resize(size) #cambia al tamaño buscado
        img_tk = ImageTk.PhotoImage(img_pil)
        
        #Panel donde guardarlo
        if panel is None:
            panel = self.panel_alterada
            
        panel.img_tk = img_tk
        panel.configure(image=img_tk)
    
    #Guarda la imagen pasada donde decida el usuario
    def guardar_imagen(self, imagen=None, titulo="Guardar imagen"):
        # Si no se pasa una imagen muestra un error
        if imagen is None:
            messagebox.showinfo("Aviso", "No hay imagen procesada para guardar.")
            return

        # Diálogo para elegir dónde guardar
        ruta_guardar = filedialog.asksaveasfilename( defaultextension=".png",  
                                                    filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
                                                    title=titulo)
        if not ruta_guardar:
            messagebox.showinfo("Aviso", "No es una dirección valida.")
            return

        # Guarda la imagen indicada
        cv2.imwrite(ruta_guardar, imagen)
        messagebox.showinfo("Éxito", f"Imagen guardada correctamente en:\n{ruta_guardar}")
    
    #Guarda la imagen pasada donde decida el usuario
    def almacenar_imagen(self):
        # Si no se pasa una imagen muestra un error
        self.guardar_imagen(self.img_alterada,"Imagen de trabajo guardada")
        
    #Establecer la imagen altera como imagen original
    def establecer_imagen_original(self):
        self.img_original = self.img_alterada
        self.mostrar_imagen(self.img_original,self.panel_imagen, (300,250))
    
    def limpiar_cambios(self):
        self.img_alterada = self.img_original
        self.mostrar_imagen(self.img_alterada,self.panel_alterada)
        self.mostrar_imagen(self.img_original,self.panel_imagen, (300,250))
    
    # --- FUNCIONALIDADES IMAGENES
    #Estrae la paleta de colores usando el K-mean tomando grupos de colores segun la K
    def extraer_paleta_colores(self, k=7):
        if self.img_original is None:
            messagebox.showinfo("Aviso", "Primero carga una imagen.")
            return

        # Convertir la imagen a RGB
        img_rgb = cv2.cvtColor( self.img_alterada, cv2.COLOR_BGR2RGB)
        pixeles = img_rgb.reshape((-1, 3)) #pasa de matriz a un vector (x,x,x) para usar k mean
        pixeles = np.float32(pixeles)

        # Definimos que o hace 50 iteraciones buscando algun color o si no difiere los colores mas de 1 se detenga
        criterio = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 1.0)
        # Saca los k colores centrales segun el criteria con la lista de pixeles de la imagen
        _ , _ , colores = cv2.kmeans(pixeles, k, None, criterio, 10, cv2.KMEANS_RANDOM_CENTERS )
        colores = np.uint8(colores) #se paso a float pero CV necesita entero
        colores = sorted(colores, key=lambda c: np.mean(c)) 
        
        # CREAMOS LA IMAGEN PARA LA SALIDA
        ancho_bloque = 150
        alto_bloque = 100
        paleta = np.zeros((alto_bloque, ancho_bloque * k, 3), dtype=np.uint8) #imagen (ponemos todo a 0 para ir formandola)
        texto_colores = ""

        #Foreach de los colores
        for i, color in enumerate(colores): 
            #Pintamos un bloque
            inicio = i * ancho_bloque
            fin = (i + 1) * ancho_bloque
            paleta[:, inicio:fin] = color

            # Colocamos los datos de cada color
            r, g, b = color
            hex_code = "#{:02X}{:02X}{:02X}".format(r, g, b)
            texto_colores += f"Color {i+1}: RGB({r}, {g}, {b}) | {hex_code}\n"
            text_color = (255, 255, 255) if np.mean(color) < 128 else (0, 0, 0)
            
            cv2.putText(paleta, f"RGB({r},{g},{b})", (inicio + 10, alto_bloque - 50),cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 1, cv2.LINE_AA)
            cv2.putText(paleta, hex_code, (inicio + 10, alto_bloque - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, 1, cv2.LINE_AA)

        # Mostrar paleta en el panel auxiliar
        self.mostrar_imagen(cv2.cvtColor(paleta, cv2.COLOR_RGB2BGR), self.panel_aux, size=(ancho_bloque * k, 100))

        # Guardar la imagen de los colores si lo desea el usuario
        if messagebox.askyesno("Guardar Paleta", "¿Deseas guardar la paleta como imagen?"):
            self.guardar_imagen(cv2.cvtColor(paleta, cv2.COLOR_RGB2BGR), "Guardar paleta de colores")

        # Pantalla con los datos de los colores
        top = tk.Toplevel(self.root)
        top.title("Paleta de Colores (RGB / HEX)")
        top.configure(bg="#202020")
        top.lift() #Dejamos la pantalla encima de todas
        
        # Texto a meter en la pantalal
        text_box = tk.Text(top, width=50, height=10, bg="#2a2a2a", fg="white", font=("Consolas", 11))
        text_box.insert("1.0", texto_colores)
        text_box.pack(padx=10, pady=10)

    #Extraemos la parte que queremos de la imagen 
    def seleccionar_region_interes(self):
        if self.img_original is None:
            messagebox.showinfo("Aviso", "Primero carga una imagen.")
            return

        img = self.img_original.copy()
        alto, ancho = img.shape[:2]
        max_ancho, max_alto = 900, 700  # límites de pantalla
        escala = min(max_ancho / ancho, max_alto / alto, 1.0)
        if escala < 1.0:
            img = cv2.resize(img, (int(ancho * escala), int(alto * escala)))

        img_original = img.copy()
        ventana = "Selecciona ROI - Presiona ESC para cancelar"
        cv2.namedWindow(ventana, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(ventana, img)

        color = (0, 0, 255)
        grosor = 2
        ancho_min = 50
        roi_listo = [False]  # bandera para saber si ya se hizo el ROI
        coords = {}

        def region(event, x, y, flags, param):
            nonlocal img
            if event == cv2.EVENT_LBUTTONDOWN:
                coords["x1"], coords["y1"] = x, y

            elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
                img = img_original.copy()
                cv2.rectangle(img, (coords["x1"], coords["y1"]), (x, y), color, grosor)
                cv2.imshow(ventana, img)

            elif event == cv2.EVENT_LBUTTONUP:
                if abs(x - coords["x1"]) > ancho_min and abs(y - coords["y1"]) > 0:
                    x1, x2 = min(x, coords["x1"]), max(x, coords["x1"])
                    y1, y2 = min(y, coords["y1"]), max(y, coords["y1"])
                    
                    roi = img_original[y1:y2, x1:x2]
                    roi_listo[0] = True
                    self.img_alterada = roi
                    cv2.destroyWindow(ventana)

                    # Maracamos la zona que tenemos como ROI
                    x1, y1, x2, y2 = coords["x1"], coords["y1"], x, y
                    if escala < 1.0: #se tiene que ajustar a la escala
                        x1 = int(x1 / escala)
                        y1 = int(y1 / escala)
                        x2 = int(x2 / escala)
                        y2 = int(y2 / escala)
                    imagen_original_roi = cv2.rectangle(self.img_original.copy(), (x1, y1), (x2, y2), (0, 255, 0), 4)
                    
                    # Mostrar ambas imágenes
                    self.mostrar_imagen(imagen_original_roi, self.panel_imagen, (300,250))
                    self.mostrar_imagen(self.img_alterada, self.panel_alterada)

        cv2.setMouseCallback(ventana, region)
        # Esperar hasta que se seleccione o se presione ESC
        while True:
            key = cv2.waitKey(1) & 0xFF
            if roi_listo[0]:
                break
            if key == 27:  # ESC
                cv2.destroyWindow(ventana)
                return

    #Alterar el brillo, saturacion y tono 
    def cambios_hsv(self):
        if self.img_alterada is None:
            messagebox.showinfo("Aviso", "Primero selecciona una región de imagen.")
            return

        img_base = self.img_alterada.copy()

        # --- Escalado para que no se salga de pantalla ---
        alto, ancho = img_base.shape[:2]
        max_ancho, max_alto = 900, 700
        escala = min(max_ancho / ancho, max_alto / alto, 1.0)
        if escala < 1.0:
            img_display = cv2.resize(img_base, None, fx=escala, fy=escala)
        else:
            img_display = img_base.copy()

        # Convertimos a HSV y tomamos valores iniciales promedio
        hsv = cv2.cvtColor(img_display, cv2.COLOR_BGR2HSV)
        h_chan, s_chan, v_chan = cv2.split(hsv)
        tono_ini = int(np.mean(h_chan))
        sat_ini = int(np.mean(s_chan))
        bri_ini = int(np.mean(v_chan))

        ventana = 'Ajuste de HSV'
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(ventana, 1100, 500)

        def actualizar(_=None):
            try:
                tono = cv2.getTrackbarPos('Tono', ventana)
                sat = cv2.getTrackbarPos('Saturacion', ventana)
                bri = cv2.getTrackbarPos('Brillo', ventana)
            except cv2.error:
                return  #Por si se llama antes de que se hayan formados

            # Ajustamos los canales según el desplazamiento relativo
            h_mod = np.clip(h_chan.astype(int) + (tono - tono_ini), 0, 180).astype(np.uint8)
            s_mod = np.clip(s_chan.astype(int) + (sat - sat_ini), 0, 255).astype(np.uint8)
            v_mod = np.clip(v_chan.astype(int) + (bri - bri_ini), 0, 255).astype(np.uint8)

            hsv_mod = cv2.merge((h_mod, s_mod, v_mod))
            img_mod = cv2.cvtColor(hsv_mod, cv2.COLOR_HSV2BGR)

            # Combinamos original y modificada lado a lado
            comparativa = np.hstack((img_display, img_mod))
            cv2.putText(comparativa, "ENTER = Guardar cambios  |  ESC = Cancelar",
                        (50, comparativa.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(ventana, comparativa)

        # Barras para alterar los valores
        cv2.createTrackbar('Tono', ventana, tono_ini, 180, actualizar)
        cv2.createTrackbar('Saturacion', ventana, sat_ini, 255, actualizar)
        cv2.createTrackbar('Brillo', ventana, bri_ini, 255, actualizar)

        # Mostrar primera imagen
        actualizar()

        # Esperamos la salida
        key = cv2.waitKey(0) & 0xFF
        if key in (13, 10):  # Guarda los cambios
            tono_f = cv2.getTrackbarPos('Tono', ventana)
            sat_f = cv2.getTrackbarPos('Saturacion', ventana)
            bri_f = cv2.getTrackbarPos('Brillo', ventana)

            # Guardamos los cambios sin escala
            hsv_full = cv2.cvtColor(img_base, cv2.COLOR_BGR2HSV)
            h_full, s_full, v_full = cv2.split(hsv_full)

            h_full = np.clip(h_full.astype(int) + (tono_f - tono_ini), 0, 180).astype(np.uint8)
            s_full = np.clip(s_full.astype(int) + (sat_f - sat_ini), 0, 255).astype(np.uint8)
            v_full = np.clip(v_full.astype(int) + (bri_f - bri_ini), 0, 255).astype(np.uint8)

            hsv_full_mod = cv2.merge((h_full, s_full, v_full))
            img_full_mod = cv2.cvtColor(hsv_full_mod, cv2.COLOR_HSV2BGR)

            # Guardar y actualizar interfaz
            self.img_alterada = img_full_mod.copy()
            self.mostrar_imagen(self.img_alterada, self.panel_alterada)
            self.guardar_en_historial() #Historial 
        else:
            messagebox.showinfo("Aviso", "Cambios cancelados.")

        cv2.destroyWindow(ventana)

    #Recorre el rango de colores dentro de la imagen
    def rango_colores(self):
        if self.img_alterada is None:
            messagebox.showinfo("Aviso", "Primero selecciona una región de imagen.")
            return
        
        intervalo = 1
        img = self.img_alterada.copy()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        ventana = "Alterar colores"
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)

        mask = None
        res = None

        def actualizar(_=None):
            nonlocal mask, res, intervalo
            try:
                matiz = cv2.getTrackbarPos('Matiz', ventana)
                intervalo = cv2.getTrackbarPos('Intervalo', ventana)
            except cv2.error:
                return

            matiz_inferior = np.array([max(0, matiz - intervalo), 0, 0])
            matiz_superior = np.array([min(180, matiz + intervalo), 255, 255])
            mask = cv2.inRange(hsv, matiz_inferior, matiz_superior)
            res = cv2.bitwise_and(img, img, mask=mask)

            comparativa = np.hstack((img, res))
            cv2.putText(comparativa, "ENTER = Editar color  |  ESC = Cancelar",
                        (40, comparativa.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(ventana, comparativa)

        cv2.namedWindow(ventana)
        cv2.createTrackbar('Matiz', ventana, 0, 179, actualizar)
        cv2.createTrackbar('Intervalo', ventana, 1, 10, actualizar)
        actualizar()

        key = cv2.waitKey(0) & 0xFF
        if key not in (13, 10):  # no ENTER
            messagebox.showinfo("Aviso", "Cambios cancelados.")
            cv2.destroyWindow(ventana)
            return

        cv2.destroyWindow(ventana)

        # EDITAMOS EL COLOR
        ventana2 = "Editar color seleccionado"
        cv2.namedWindow(ventana2, cv2.WINDOW_NORMAL)
        img_mod = None

        # Valores promedio iniciales del área seleccionada
        pixeles_mask = img[mask > 0]
        if pixeles_mask.size == 0:
            messagebox.showinfo("Aviso", "No hay píxeles seleccionados.")
            return

        b_ini, g_ini, r_ini = [int(np.mean(pixeles_mask[:, i])) for i in range(3)]
        b, g, r = b_ini, g_ini, r_ini

        def actualizar_color(_=None):
            nonlocal b, g, r, img_mod
            try:
                b = cv2.getTrackbarPos('Azul', ventana2)
                g = cv2.getTrackbarPos('Verde', ventana2)
                r = cv2.getTrackbarPos('Rojo', ventana2)
            except cv2.error:
                return

            img_mod = img.copy() #copiamos la imagen original
            img_mod[mask > 0] = (b, g, r) #en la mascara del color seleccionamos cambialos al color dado

            comparativa = np.hstack((img, img_mod))
            cv2.putText(comparativa, "ENTER = Guardar  |  ESC = Cancelar", (40, comparativa.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(ventana2, comparativa)

        cv2.createTrackbar('Rojo', ventana2, r_ini, 255, actualizar_color)
        cv2.createTrackbar('Verde', ventana2, g_ini, 255, actualizar_color)
        cv2.createTrackbar('Azul', ventana2, b_ini, 255, actualizar_color)

        actualizar_color()

        key = cv2.waitKey(0) & 0xFF
        if key in (13, 10):  # ENTER
            self.img_alterada = img_mod.copy()
            self.mostrar_imagen(self.img_alterada, self.panel_alterada)
            self.guardar_en_historial() #Historial 
        else:
            messagebox.showinfo("Aviso", "Edición de color cancelada.")

        cv2.destroyWindow(ventana2)

    #Sacaremos el contorno en blanco y negro del elemento
    def extraer_contornos(self):
        if self.img_alterada is None:
            messagebox.showinfo("Aviso", "Primero selecciona una región de imagen.")
            return

        img_original = self.img_alterada.copy()
        img_byn = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)

        ventana = 'Contornos - ENTER para guardar / ESC para cancelar'
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
        contornos = None

        def actualizar(_=None):
            nonlocal contornos
            try:
                umbral = cv2.getTrackbarPos('Umbral', ventana)
            except cv2.error:
                return  # En caso de que el trackbar no esté aún creado

            # Umbralizado y detección de contornos
            _, img_umbral = cv2.threshold(img_byn, umbral, 255, cv2.THRESH_BINARY_INV)
            contornos, _ = cv2.findContours(img_umbral, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

            img_contornos = img_original.copy()
            cv2.drawContours(img_contornos, contornos, -1, (0, 255, 0), 2)

            # Guardar los resultados actuales
            contornos = cv2.cvtColor(cv2.bitwise_not(img_umbral), cv2.COLOR_GRAY2BGR)

            # Mostrar comparativa lado a lado
            comparativa = np.hstack((img_contornos, contornos))
            cv2.putText(comparativa, "ENTER = Guardar cambios  |  ESC = Cancelar", (50, comparativa.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(ventana, comparativa)

        # Crear la barra de umbral y mostrar la imagen inicial
        cv2.createTrackbar('Umbral', ventana, 100, 255, actualizar)
        actualizar()

        # Esperar acción del usuario
        key = cv2.waitKey(0) & 0xFF
        if key in (13, 10):  # ENTER → guardar
            if contornos is not None:
                self.img_alterada = contornos
                self.mostrar_imagen(self.img_alterada, self.panel_alterada)
                self.guardar_en_historial() #Historial 
        else:
            messagebox.showinfo("Aviso", "Cambios cancelados.")
        cv2.destroyWindow(ventana)

    #Combinar imagenes ya sea suma o resta de la imagen alterada con la que se de 
    def combinar_imagen(self):
        if self.img_alterada is None:
            messagebox.showinfo("Aviso", "Primero selecciona una región de imagen.")
            return
        
        #Sacamos la nueva imagen
        ruta = filedialog.askopenfilename(title="Selecciona una imagen para combinar", filetypes=[("Archivos de imagen", "*.jpg *.png *.jpeg *.bmp *.webp")])
        if not ruta:
            return
        img2 = cv2.imread(ruta)
        if img2 is None:
            messagebox.showerror("Error", "No se pudo cargar la imagen seleccionada.")
            return
        
        img1 = self.img_alterada.copy()
        alto, ancho = img1.shape[:2]
        img2 = cv2.resize(img2, (ancho, alto)) #lo escala para que se integren
        
        #Parametros para como hacer los cambios
        op = messagebox.askquestion("Operación", "¿Deseas SUMAR las imágenes?\n(Pulsa 'No' para RESTAR)")
        dir = messagebox.askquestion("Dirección", "¿Aplicar operación como: \nAlterada ± Imagen Nueva?\n(Pulsa 'No' para Imagen Nueva ± Alterada)")

        if dir == "no":
            img1, img2 = img2, img1
        resultado = cv2.add(img1, img2) if op == "no" else cv2.subtract(img1, img2)
        
        ventana = "Cambios imagen"
        comparativa = np.hstack((self.img_alterada.copy(), resultado))
        escala = min(1000 / comparativa.shape[1], 700 / comparativa.shape[0], 1.0)
        if escala < 1.0:
            comparativa = cv2.resize(comparativa, None, fx=escala, fy=escala)
        cv2.putText(comparativa, "ENTER = Guardar cambios  |  ESC = Cancelar", (50, comparativa.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow(ventana, comparativa)
        
        key = cv2.waitKey(0) & 0xFF
        if key in (13, 10):  # ENTER → guardar
            self.img_alterada = resultado
            self.mostrar_imagen(self.img_alterada, self.panel_alterada)
            self.guardar_en_historial() #Historial 
        else:
            messagebox.showinfo("Aviso", "Cambios cancelados.")
        cv2.destroyWindow(ventana)
            
    # --- FUNCIONALIDADES EN PROCESO
    #Busca tener el area total del dibujo
    def cerrar_contornos(self):
        if self.img_alterada is None:
            messagebox.showinfo("Aviso", "Primero selecciona una región de imagen.")
            return

        img = self.img_alterada.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ventana = "Cerrar contornos (Máscara sólida)"
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)

        def actualizar(_=None):
            try:
                umbral = cv2.getTrackbarPos('Umbral', ventana)
                nivel = cv2.getTrackbarPos('Nivel', ventana)
            except cv2.error:
                return

            k = max(1, nivel)
            kernel = np.ones((k, k), np.uint8)
            _, binaria = cv2.threshold(gray, umbral, 255, cv2.THRESH_BINARY)
            cerrada = cv2.morphologyEx(binaria, cv2.MORPH_CLOSE, kernel, iterations=2)
            contornos, _ = cv2.findContours(cerrada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mascara = np.ones_like(gray)
            cv2.drawContours(mascara, contornos, -1, 255, thickness=cv2.FILLED)

            mascara_bgr = cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)

            comparativa = np.hstack((img, mascara_bgr))
            texto = f"ENTER=Guardar | ESC=Cancelar | Umbral={umbral} | Kernel={nivel}"
            cv2.putText(comparativa, texto, (40, comparativa.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(ventana, comparativa)

            actualizar.ultima = mascara_bgr

        # Crear sliders
        cv2.createTrackbar('Umbral', ventana, 127, 255, actualizar)
        cv2.createTrackbar('Nivel', ventana, 3, 25, actualizar)
        actualizar()

        # Esperar acción del usuario
        key = cv2.waitKey(0) & 0xFF
        if key in (13, 10):  # ENTER
            if hasattr(actualizar, "ultima") and actualizar.ultima is not None:
                self.img_alterada = actualizar.ultima.copy()
                self.mostrar_imagen(self.img_alterada, self.panel_alterada)
                self.guardar_en_historial() #Historial 
        else:
            messagebox.showinfo("Aviso", "Cambios cancelados.")

        cv2.destroyWindow(ventana)

    #Segun el controno dibuja figuras geometricas que le formen (Usamos Douglas-Peucker)
    def dibujar_formas(self):
        if self.img_alterada is None:
            messagebox.showinfo("Aviso", "Primero selecciona una región de imagen.")
            return

        img = self.img_alterada.copy()
        img_byn = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ventana = "Detectar formas geométricas (Boceto)"
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)

        def actualizar(_=None):
            try:
                umbral = cv2.getTrackbarPos('Umbral', ventana)
                nivel = cv2.getTrackbarPos('Nivel', ventana)
                aprox_slider = cv2.getTrackbarPos('Aproximacion', ventana)
            except cv2.error:
                return

            aprox_factor = max(0.5, aprox_slider) / 100.0
            _, thresh = cv2.threshold(img_byn, umbral, 255, cv2.THRESH_BINARY_INV)

            # Morfología para cerrar agujeros
            k = max(1, nivel)
            kernel = np.ones((k, k), np.uint8)
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
            opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)
            procesada = opened

            contornos, _ = cv2.findContours(procesada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            img_formas = img.copy()

            counts = {"Triangulo":0, "Cuadrado":0, "Rectangulo":0, "Pentagono":0, "Circulo":0, "Poligono":0}
            for c in contornos:
                area = cv2.contourArea(c)
                if area < 100:
                    continue

                perimetro = cv2.arcLength(c, True)
                epsilon = aprox_factor * perimetro
                aprox = cv2.approxPolyDP(c, epsilon, True)
                vertices = len(aprox)
                color = (0, 255, 0)

                if vertices > 8:
                    (x_c, y_c), radio = cv2.minEnclosingCircle(c)
                    centro = (int(x_c), int(y_c))
                    radio = int(radio)
                    cv2.circle(img_formas, centro, radio, color, 2)
                    counts["Circulo"] += 1
                else:
                    pts = aprox.reshape((-1, 1, 2))
                    cv2.polylines(img_formas, [pts], True, color, 2)
                    if vertices == 3:
                        counts["Triangulo"] += 1
                    elif vertices == 4:
                        x, y, w, h = cv2.boundingRect(aprox)
                        ratio = w / float(h) if h > 0 else 0
                        if 0.95 <= ratio <= 1.05:
                            counts["Cuadrado"] += 1
                        else:
                            counts["Rectangulo"] += 1
                    elif vertices == 5:
                        counts["Pentagono"] += 1
                    else:
                        counts["Poligono"] += 1

            procesada_color = cv2.cvtColor(procesada, cv2.COLOR_GRAY2BGR)
            comparativa = np.hstack((procesada_color, img_formas))

            texto = f"ENTER=Guardar | ESC=Cancelar | Aproxf={aprox_factor:.3f} | Umbral={umbral} | Kernel={k}"
            cv2.putText(comparativa, texto, (20, comparativa.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)

            resumen = ", ".join([f"{k}:{v}" for k,v in counts.items() if v>0])
            if resumen:
                cv2.putText(comparativa, resumen, (20, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1, cv2.LINE_AA)

            cv2.imshow(ventana, comparativa)
            actualizar.ultimo = img_formas

        cv2.createTrackbar('Umbral', ventana, 100, 255, actualizar)
        cv2.createTrackbar('Nivel', ventana, 3, 25, actualizar)
        cv2.createTrackbar('Aproximacion', ventana, 2, 30, actualizar)
        actualizar()

        key = cv2.waitKey(0) & 0xFF
        if key in (13, 10):
            if hasattr(actualizar, "ultimo") and actualizar.ultimo is not None:
                self.img_alterada = actualizar.ultimo.copy()
                self.mostrar_imagen(self.img_alterada, self.panel_alterada)
                self.guardar_en_historial() #Historial 
        else:
            messagebox.showinfo("Aviso", "Cambios cancelados.")

        try:
            cv2.destroyWindow(ventana)
        except cv2.error:
            pass

        
# ------------------------------
# Ejecutar aplicación
# ------------------------------
if __name__ == "__main__":
    #Prepara el contorno
    root = tk.Tk()
    #Lo lanza
    app = ContourApp(root)
    root.mainloop()
    #Quita las vetanas auxiliares
    cv2.destroyAllWindows()
