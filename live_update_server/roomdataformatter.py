from live_update_server.roomdataparser import RoomDataParser

class RoomDataFormatter():
    """ Consumes a known shape of Room data and produces json expected on the client side """

    @staticmethod
    def build_rooms_json(parsed_sheet_data):
        assert isinstance(parsed_sheet_data, RoomDataParser)
        room_data = parsed_sheet_data.get_parsed_rooms()
        json_room_data = {}
        for room_id in room_data:
            attrs = room_data[room_id]
            info = {}
            info['roomName'] = attrs['roomName']
            info['status'] = "occupied" if RoomDataFormatter._room_taken(attrs) else "available"
            info['occupier'] = RoomDataFormatter._get_occupier(attrs)
            info['occupierCrsid'] = attrs['crsid']
            info['roomPrice'] = RoomDataFormatter._get_weekly_rent(attrs)
            info['contractType'] = attrs['license']
            info['roomType'] = attrs['roomType']
            info['fullCost'] = RoomDataFormatter._get_full_cost_string(attrs)
            info['floor'] = attrs['floor']
            info['notes'] = attrs['notes']
            info['lastUpdated'] = attrs['lastUpdated'] if 'lastUpdated' in attrs else 0.0
            json_room_data[room_id] = info
        return json_room_data

    @staticmethod
    def _room_taken(room_attrs):
        if room_attrs['surname'].strip() == "" and room_attrs['name'].strip() == "":
            return False
        return True
    
    @staticmethod
    def _get_occupier(room_attrs):
        return room_attrs['name'] + " " + room_attrs['surname']
    
    @staticmethod
    def _get_weekly_rent(room_attrs):
        return room_attrs['weeklyRent']

    @staticmethod
    def _get_contract_type(room_attrs):
        return room_attrs['license']

    @staticmethod
    def _get_full_cost_string(room_attrs):
        contract = RoomDataFormatter._get_contract_type(room_attrs)
        if 'term' in contract.lower():
            return "30 weeks: &pound;{0:.2f}".format(float(RoomDataFormatter._get_weekly_rent(room_attrs).strip())*30)
        else: 
            #calculate both easter and yearly cost
			#note on calculation: during the holidays, so for about 25 days each holiday, you pay 80% of the cost
            s = "30 week: ~&pound;{0:.2f}".format(float(RoomDataFormatter._get_weekly_rent(room_attrs).strip())*30)
            s += "\nEaster (80% vac rate): ~&pound;{0:.2f}".format(round(float(RoomDataFormatter._get_weekly_rent(room_attrs).strip())*(30 + 0.8 * 3.5), 2))
            s += "\nYear (80% vac cost): ~&pound;{0:.2f}".format(round(float(RoomDataFormatter._get_weekly_rent(room_attrs).strip()) * ( 30 + 0.8*7), 2))
            return s