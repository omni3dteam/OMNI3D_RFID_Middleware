
filament_material_dict = {
    0: "None",
    1: "PLA",
    2: "ABS",
    3: "PETG",
    4: "TPU",
    5: "Nylon",
    6: "ASA",
    7: "PC (Polycarbonate)",
    8: "HIPS",
    9: "PVA",
    10: "Wood",
    11: "Metal",
    12: "Flexible",
    13: "Carbon Fiber",
    14: "PET",
    15: "PEI (Ultem)",
    16: "PEEK",
    17: "POM (Delrin)",
    18: "TPE",
    19: "PP (Polypropylene)",
    20: "PMMA (Acrylic)",
    21: "Other",
}

filament_color_dict = {
    0: "None",
    1: "White",
    2: "Black",
    3: "Red",
    4: "Green",
    5: "Blue",
    6: "Yellow",
    7: "Orange",
    8: "Purple",
    9: "Pink",
    10: "Brown",
    11: "Gray",
    12: "Silver",
    13: "Gold",
    14: "Transparent",
    15: "Cyan",
    16: "Magenta",
    17: "Lime",
    18: "Teal",
    19: "Turquoise",
    20: "Violet",
    21: "Beige",
}

def GetMaterial(number):
    return filament_material_dict.get(number, "Unknown")

def GetColour(number):
    return filament_color_dict.get(number, "Unknown")