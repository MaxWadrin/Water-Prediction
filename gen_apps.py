with open('data/v2/Template_Application.txt', 'w') as f:
    for i in range(1, 161):
        node = f"Floor{i}_Inlet"
        if 1 <= i <= 20: t = "LobbyRetail"
        elif 21 <= i <= 60: t = "HotelFloor"
        elif 61 <= i <= 100: t = "OfficeFloor"
        elif 101 <= i <= 140: t = "ResidentialFloor"
        elif 141 <= i <= 150: t = "LuxuryHotel"
        elif 151 <= i <= 160: t = "ObsRestaurant"
        f.write(f"Apply {t} {node}\n")
