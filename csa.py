import pandas as pd

import numpy as np

FILENAME = "data/connections.csv"


def to_minutes(str_time):
    if "inf" in str_time:
        return np.inf
    else:
        [hours, minutes] = [int(e) for e in str_time.split(":")]
        return 60 * hours + minutes


def to_time_str(minutes):
    if minutes == np.inf:
        return "inf"
    else:
        return f"{str(minutes // 60).zfill(2)}:{str(minutes % 60).zfill(2)}"


class Connection:
    def __init__(self, origin, destination, departure_time, arrival_time):
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time

    def __str__(self):
        return f"({self.origin},{self.departure_time}) -> ({self.destination},{self.arrival_time})"


class Network:

    def __init__(self):
        self.stations = []
        self.connections = []

    def set_stations(self, df):
        self.stations = np.unique(np.concatenate([df['departure_station'].values, df['arrival_station'].values]))

    def set_connections(self, df, departure_time_minutes):
        df_crop = df[df['departure_time_minutes'] >= departure_time_minutes]
        for row in df_crop.iterrows():
            self.connections.append(Connection(row[1]['departure_station'],
                                               row[1]['arrival_station'],
                                               row[1]['departure_time_minutes'],
                                               row[1]['arrival_time_minutes']))

        self.connections.sort(key=lambda x: x.departure_time)


def csa(filename, origin, destination, departure_time):
    df = pd.read_csv(filename)
    df['departure_time_minutes'] = df['departure_time'].apply(lambda x: to_minutes(x))
    df['arrival_time_minutes'] = df['arrival_time'].apply(lambda x: to_minutes(x))

    network = Network()
    network.set_stations(df)
    network.set_connections(df, departure_time)
    arrival_time_stations = dict(zip(network.stations, np.inf * np.ones(len(network.stations))))
    previous_station = dict(zip(network.stations, [None for _ in network.stations]))

    if (origin not in network.stations) or (destination not in network.stations):
        print("origin or destination not in network...")
        return -1
    else:
        arrival_time_stations[origin] = departure_time
        for connection in network.connections:
            if ((arrival_time_stations[connection.origin] != np.inf) and
                    (arrival_time_stations[connection.destination] > connection.arrival_time)):
                arrival_time_stations[connection.destination] = connection.arrival_time
                previous_station[connection.destination] = connection.origin

        current_station = destination
        if arrival_time_stations[destination] == np.inf:
            print(f"No path found from {origin} to {destination}..")
            return "inf"
        else:
            res = to_time_str(arrival_time_stations[destination])
            path = []
            while current_station is not None:
                path.insert(0, current_station)
                current_station = previous_station[current_station]
            print(f"Solution found: from {origin} at {to_time_str(departure_time)} to {destination} at {res} ", )
            print("solution path: ", path)
            return res


origins = ["A", "B", "C", "E", "G"]
destinations = ["D", "F", "H", "J", "I"]
departure_times = ["06:00", "07:30", "08:15", "09:00", "10:00"]
expected_arrival_times = ["08:01", "08:47", "inf", "10:34", "inf"]

test_cases_df = pd.DataFrame({
    'origin': origins,
    'destination': destinations,
    'departure_time': [to_minutes(str_time) for str_time in departure_times],
    'expected_arrival_time': expected_arrival_times
})

for i in range(len(test_cases_df)):
    test_case = test_cases_df.iloc[i]
    res = csa(FILENAME, test_case.origin, test_case.destination, test_case.departure_time)
    if res == test_case.expected_arrival_time:
        print("Good solution found !")
    else:
        print(f"Wrong arrival time: expected: {test_case.expected_arrival_time}  actual: {res}")
