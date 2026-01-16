import os

base_path = "c:/Users/Administrator/Documents/Project/Water Prediction/data/v2"

def write_file(filename, content):
    path = os.path.join(base_path, filename)
    with open(path, 'w') as f:
        f.write(content)

# ---------------------------------------------------------
# 1. Floor_Templates.txt
# ---------------------------------------------------------
templates_content = ""

# Lobby/Retail (Floors 1-20)
templates_content += "Template LobbyRetail\n"
templates_content += "Node Riser\n"
templates_content += "Node RestroomM\n"
templates_content += "Node RestroomF\n"
templates_content += "Node Retail1\n"
templates_content += "Node Retail2\n"
templates_content += "Edge Riser RestroomM\n"
templates_content += "Edge Riser RestroomF\n"
templates_content += "Edge Riser Retail1\n"
templates_content += "Edge Riser Retail2\n"
templates_content += "EndTemplate\n\n"

# Hotel (Floors 21-60) - 20 baths
templates_content += "Template HotelFloor\n"
templates_content += "Node Riser\n"
for i in range(1, 21):
    templates_content += f"Node Bath{i}\n"
    templates_content += f"Edge Riser Bath{i}\n"
templates_content += "EndTemplate\n\n"

# Office (Floors 61-100)
templates_content += "Template OfficeFloor\n"
templates_content += "Node Riser\n"
templates_content += "Node Kitchen\n"
templates_content += "Node RestroomBlock\n"
templates_content += "Edge Riser Kitchen\n"
templates_content += "Edge Riser RestroomBlock\n"
templates_content += "EndTemplate\n\n"

# Residential (Floors 101-140) - 8 apts
templates_content += "Template ResidentialFloor\n"
templates_content += "Node Riser\n"
for i in range(1, 9):
    templates_content += f"Node Apt{i}\n"
    templates_content += f"Edge Riser Apt{i}\n"
templates_content += "EndTemplate\n\n"

# Luxury Hotel (Floors 141-150) - 10 suites (assuming larger)
templates_content += "Template LuxuryHotel\n"
templates_content += "Node Riser\n"
for i in range(1, 11):
    templates_content += f"Node Suite{i}\n"
    templates_content += f"Edge Riser Suite{i}\n"
templates_content += "EndTemplate\n\n"

# Observation (Floors 151-160)
templates_content += "Template ObsRestaurant\n"
templates_content += "Node Riser\n"
templates_content += "Node Kitchen\n"
templates_content += "Node PublicRestroom\n"
templates_content += "Edge Riser Kitchen\n"
templates_content += "Edge Riser PublicRestroom\n"
templates_content += "EndTemplate\n"

write_file("Floor_Templates.txt", templates_content)

# ---------------------------------------------------------
# 2. Template_Application.txt
# ---------------------------------------------------------
app_content = ""
for i in range(1, 161):
    floor_node = f"Floor{i}_Inlet"
    if 1 <= i <= 20:
        app_content += f"Apply LobbyRetail {floor_node}\n"
    elif 21 <= i <= 60:
        app_content += f"Apply HotelFloor {floor_node}\n"
    elif 61 <= i <= 100:
        app_content += f"Apply OfficeFloor {floor_node}\n"
    elif 101 <= i <= 140:
        app_content += f"Apply ResidentialFloor {floor_node}\n"
    elif 141 <= i <= 150:
        app_content += f"Apply LuxuryHotel {floor_node}\n"
    elif 151 <= i <= 160:
        app_content += f"Apply ObsRestaurant {floor_node}\n"

write_file("Template_Application.txt", app_content)

# ---------------------------------------------------------
# 3. WaterSystem.txt
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

# Distribution (Downfeed from tanks to zones)
# Zone A: 1-40 (Fed by BreakTank1)
# Zone B: 41-80 (Fed by BreakTank2)
# Zone C: 81-120 (Fed by BreakTank3)
# Zone D: 121-160 (Fed by RoofTank)

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
# 4. Demand_Profiles.txt
# ---------------------------------------------------------
demand_content = ""
# Just generating some demands for the units
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

# ---------------------------------------------------------
# 5. Sensors.txt
# ---------------------------------------------------------
sensor_content = ""
sensor_content += "Sensor MunicipalMain Flow\n"
sensor_content += "Sensor BasementSump Level\n"
sensor_content += "Sensor BreakTank1 Level\n"
sensor_content += "Sensor BreakTank2 Level\n"
sensor_content += "Sensor BreakTank3 Level\n"
sensor_content += "Sensor RoofTank Level\n"

# Pump flows
sensor_content += "Sensor PumpA Flow\n"
sensor_content += "Sensor PumpB Flow\n"
sensor_content += "Sensor PumpC Flow\n"
sensor_content += "Sensor PumpD Flow\n"

# Riser flows
sensor_content += "Sensor ZoneA_Riser Flow\n"
sensor_content += "Sensor ZoneB_Riser Flow\n"
sensor_content += "Sensor ZoneC_Riser Flow\n"
sensor_content += "Sensor ZoneD_Riser Flow\n"

# Critical floor pressures (Top and Bottom of zones)
sensor_content += "Sensor Floor1_Inlet Pressure\n"
sensor_content += "Sensor Floor40_Inlet Pressure\n"
sensor_content += "Sensor Floor41_Inlet Pressure\n"
sensor_content += "Sensor Floor80_Inlet Pressure\n"
sensor_content += "Sensor Floor81_Inlet Pressure\n"
sensor_content += "Sensor Floor120_Inlet Pressure\n"
sensor_content += "Sensor Floor121_Inlet Pressure\n"
sensor_content += "Sensor Floor160_Inlet Pressure\n"

write_file("Sensors.txt", sensor_content)
