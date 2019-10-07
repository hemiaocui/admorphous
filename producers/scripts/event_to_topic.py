"""
Converts csv file to a stream of JSON, sends to Kafka topic.
Input arguments: script, input csv path, topic name, bootstrap servers
"""
# Import packages
import sys
import csv
import json
from time import sleep
from datetime import datetime
from datetime import timedelta
from kafka import KafkaProducer
import display_to_topic as display

# Shell script input arguments
#args = sys.argv

# There should be four or more input arguments:
# script, input csv path, topic name, bootstrap servers
"""
if len(args) >= 4:
    input_file_path = args[1]
    topic_name = args[2]
    bootstrap_server_list = args[3:]
else:
    raise Exception('Need at least four input arguments.')
"""
bootstrap_server_list = ['localhost:9092']
events_file_path = '../data/processed/events.csv'
display_file_path = '../data/processed/display_ad.csv'
events_topic_name = 'events'


def send_events(bootstrap_server_list,
                events_file_path,
                display_file_path,
                topic_name,
                sleep_time,
                dump_size):
    """

    :param bootstrap_server_list:
    :return:
    """
    # Set up Kafka Producer
    producer = KafkaProducer(bootstrap_servers=bootstrap_server_list,
                             value_serializer=lambda x:
                             json.dumps(x).encode('utf-8'))

    start_line, start_display_id = 1, 1
    line_number, line_display_id = display.send_mapping(bootstrap_server_list,
                                                        display_file_path,
                                                        start_line,
                                                        start_display_id,
                                                        dump_size)

    # Send JSON stream to topic
    with open(events_file_path, 'r', encoding='utf-8') as file:
        # Csv reader iterator
        file_reader = csv.DictReader(file)

        for i, row in enumerate(file_reader):

            if i % dump_size == 0:
                line_number, line_display_id = display.send_mapping(bootstrap_server_list, display_file_path,
                                                                    line_number,
                                                                    line_display_id, dump_size)
                #input("Press Enter to continue...")

            if i == 5000:
                break

            row['event_time'] = (datetime.now() - timedelta(seconds=2)).strftime('%Y-%m-%d %H:%M:%S')
            row['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            print(row)

            producer.send(topic_name, value=row)
            sleep(sleep_time)


send_events(bootstrap_server_list, events_file_path, display_file_path, events_topic_name, 0.5, 10)