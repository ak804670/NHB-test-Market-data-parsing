import csv
import sys
from datetime import datetime
from statistics import median


def process_capture_data(filename):
    with open(filename, "r") as file:
        csv_reader = csv.DictReader(file)

        # Initialize variables
        timestamps = []
        packet_timestamps = []
        order_ids = set()
        maker_order_ids = set()
        taker_order_ids = set()
        lost_updates = 0
        match_done_times = []

        for row in csv_reader:
            msg_type = row["MsgType"]
            timestamp = int(row["Timestamp"])
            packet_timestamp = int(row["PacketTimestamp"])

            # Check for strictly increasing timestamps
            if timestamps and timestamp <= timestamps[-1]:
                print("Timestamp discrepancy - non-increasing order:", row)

            # Check for strictly increasing packet timestamps
            if packet_timestamps and packet_timestamp <= packet_timestamps[-1]:
                print("Packet timestamp discrepancy - non-increasing order:", row)

            timestamps.append(timestamp)
            packet_timestamps.append(packet_timestamp)

            if msg_type == "DONE":
                order_id = row["OrderId"]

                # Check if the corresponding Order ID exists
                if order_id not in order_ids:
                    print("DONE message discrepancy - non-existing Order ID:", row)
                else:
                    order_ids.remove(order_id)

            elif msg_type == "MATCH":
                maker_order_id = row["MakerOrderId"]
                taker_order_id = row["TakerOrderId"]

                # Check if the corresponding Maker and Taker Order IDs exist
                if maker_order_id not in maker_order_ids:
                    print(
                        "MATCH message discrepancy - non-existing Maker Order ID:", row
                    )
                if taker_order_id not in taker_order_ids:
                    print(
                        "MATCH message discrepancy - non-existing Taker Order ID:", row
                    )

            order_ids.add(row["OrderId"])
            maker_order_ids.add(row["MakerOrderId"])
            taker_order_ids.add(row["TakerOrderId"])

            # Calculate the time between MATCH and DONE messages
            if msg_type == "MATCH":
                match_done_times.append(
                    int(row["Timestamp"]) - int(row["PacketTimestamp"])
                )

        # Calculate the required summary data
        file_size = file.tell()
        num_updates = len(timestamps)
        start_timestamp = datetime.fromtimestamp(timestamps[0] / 1e9)
        end_timestamp = datetime.fromtimestamp(timestamps[-1] / 1e9)
        start_packet_timestamp = datetime.fromtimestamp(packet_timestamps[0] / 1e9)
        end_packet_timestamp = datetime.fromtimestamp(packet_timestamps[-1] / 1e9)
        num_lost_updates = len(order_ids)
        median_update_time = median(
            [timestamps[i] - timestamps[i - 1] for i in range(1, num_updates)]
        )
        median_match_done_time = median(match_done_times)

        # Output the summary data
        print("File size: {:.2f} KB".format(file_size / 1024))
        print("Number of updates:", num_updates)
        print("Start timestamp:", start_timestamp)
        print("End timestamp:", end_timestamp)
        print("Start packet timestamp:", start_packet_timestamp)
        print("End packet timestamp:", end_packet_timestamp)
        print("Number of lost updates:", num_lost_updates)
        print(
            "Median time between updates: {:.2f} seconds".format(
                median_update_time / 1e9
            )
        )
        print(
            "Median time between MATCH trades and DONE messages: {:.2f} seconds".format(
                median_match_done_time / 1e9
            )
        )


if __name__ == "__main__":
    capture_file = sys.argv[1]
    process_capture_data(capture_file)
