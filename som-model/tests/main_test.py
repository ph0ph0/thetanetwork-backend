import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import main


class TestMain(unittest.TestCase):

    @patch('main.process_data_with_model')
    @patch('main.pika.BlockingConnection')
    @patch('main.pika.URLParameters')
    def test_callback(self, mock_url_parameters, mock_blocking_connection, mock_process_data_with_model):
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_properties = MagicMock()
        test_body = json.dumps({'key': 'value'}).encode('utf-8')

        # Set a specific return value for the mock
        mock_process_data_with_model.return_value = {'processed_key': 'processed_value'}

        main.callback(mock_channel, mock_method, mock_properties, test_body)

        mock_process_data_with_model.assert_called_once_with({'key': 'value'})
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)
        # Additional assertions can be added here to check if add_to_valuation_queue is called correctly

    @patch('main.pika.BlockingConnection')
    @patch('main.pika.URLParameters')
    @patch('main.os.environ.get')
    def test_main(self, mock_environ_get, mock_url_parameters, mock_blocking_connection):
        mock_environ_get.return_value = 'amqp://test'
        mock_url_parameters.return_value = 'amqp://test'
        mock_connection = MagicMock()
        mock_blocking_connection.return_value = mock_connection
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel

        with patch('builtins.print'):
            with self.assertRaises(KeyboardInterrupt):
                mock_channel.start_consuming.side_effect = KeyboardInterrupt
                main.main()

        mock_url_parameters.assert_called_once_with('amqp://test')
        mock_blocking_connection.ass
