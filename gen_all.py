import os

cwd = os.getcwd()
data_dir = os.path.join(cwd, 'data', 'v2')
print(f"Target dir: {data_dir}")

if not os.path.exists(data_dir):
    print("Creating directory...")
    os.makedirs(data_dir)

def write_file(filename, content):
    path = os.path.join(data_dir, filename)
    print(f"Writing to {path}")
    with open(path, 'w') as f:
        f.write(content)

# ---------------------------------------------------------
# Template_Application.txt
# ---------------------------------------------------------
app_content = ""
for i in range(1, 161):
    floor_node = f"Floor{i}_Inlet"
    if 1 <= i <= 20: t = "LobbyRetail"
    elif 21 <= i <= 60: t = "HotelFloor"
    elif 61 <= i <= 100: t = "OfficeFloor"
    elif 101 <= i <= 140: t = "ResidentialFloor"
    elif 141 <= i <= 150: t = "LuxuryHotel"
    elif 151 <= i <= 160: t = "ObsRestaurant"
    app_content += f"Apply {t} {floor_node}\n"

write_file("Template_Application.txt", app_content)

# ---------------------------------------------------------
# WaterSystem.txt
# ---------------------------------------------------------
sys_content = ""
sys_content += "Source MunicipalMain\n"
sys_content += "Tank BasementSump\n"
sys_content += "Pipe MunicipalMain BasementSump\n"

# Break Tanks
sys_content += "Tank BreakTank1\n" # Floor 40
sys_content += "Tank BreakTank2\n" # Floor 80
sys_content += "Tank BreakTank3\n" # Floor 120
sys_content += "Tank RoofTank\n"   # Floor 160

# Pumps (Upward flow)
sys_content += "Pump PumpA BasementSump BreakTank1\n"
sys_content += "Pump PumpB BreakTank1 BreakTank2\n"
sys_content += "Pump PumpC BreakTank2 BreakTank3\n"
sys_content += "Pump PumpD BreakTank3 RoofTank\n"

# Risers
sys_content += "Pipe BreakTank1 ZoneA_Riser\n"
sys_content += "Pipe BreakTank2 ZoneB_Riser\n"
sys_content += "Pipe BreakTank3 ZoneC_Riser\n"
sys_content += "Pipe RoofTank ZoneD_Riser\n"

# Connect Floors
for i in range(1, 161):
    floor_node = f"Floor{i}_Inlet"
    if 1 <= i <= 40:
        sys_content += f"Pipe ZoneA_Riser {floor_node}\n"
    elif 41 <= i <= 80:
        sys_content += f"Pipe ZoneB_Riser {floor_node}\n"
    elif 81 <= i <= 120:
        sys_content += f"Pipe ZoneC_Riser {floor_node}\n"
    elif 121 <= i <= 160:
        sys_content += f"Pipe ZoneD_Riser {floor_node}\n"

write_file("WaterSystem.txt", sys_content)

# ---------------------------------------------------------
# Demand_Profiles.txt
# ---------------------------------------------------------
demand_content = ""
for i in range(1, 161):
    floor_node = f"Floor{i}_Inlet"
    if 1 <= i <= 20: # Lobby
        demand_content += f"Demand {floor_node}.RestroomM 50\n"
        demand_content += f"Demand {floor_node}.RestroomF 50\n"
    elif 21 <= i <= 60: # Hotel
        for j in range(1, 21):
            demand_content += f"Demand {floor_node}.Bath{j} 100\n"
    elif 61 <= i <= 100: # Office
        demand_content += f"Demand {floor_node}.Kitchen 80\n"
        demand_content += f"Demand {floor_node}.RestroomBlock 200\n"
    elif 101 <= i <= 140: # Residential
        for j in range(1, 9):
            demand_content += f"Demand {floor_node}.Apt{j} 150\n"
    elif 141 <= i <= 150: # Luxury
        for j in range(1, 11):
            demand_content += f"Demand {floor_node}.Suite{j} 250\n"
    elif 151 <= i <= 160: # Obs
        demand_content += f"Demand {floor_node}.Kitchen 300\n"
        demand_content += f"Demand {floor_node}.PublicRestroom 100\n"

write_file("Demand_Profiles.txt", demand_content)
