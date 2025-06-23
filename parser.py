def procesar_obj():
    input_file = "models/UNI_rep.obj"
    output_file = "models/UNI_rep.obj"

    with open(input_file, "r") as f:
        lines = f.readlines()

    nuevo_lines = []
    en_panel = False
    caras_guardadas = False

    for line in lines:
        if line.startswith("o "):
            # Comenzó un nuevo objeto, verificar si es panel
            en_panel = line[2:].startswith("Paneles_")
            caras_guardadas = False
            nuevo_lines.append(line)
            continue

        if en_panel:
            if line.startswith("f "):
                if not caras_guardadas:
                    nuevo_lines.append(line)
                    caras_guardadas = True
                # Si ya guardamos una cara, saltamos las demás
                continue
            else:
                # Cualquier línea que no sea 'f' la copiamos normalmente
                nuevo_lines.append(line)
        else:
            # No estamos en panel, copiamos todo
            nuevo_lines.append(line)

    with open(output_file, "w") as f:
        f.writelines(nuevo_lines)

    print(f"Proceso terminado. Archivo guardado como {output_file}")

if __name__ == "__main__":
    procesar_obj()
