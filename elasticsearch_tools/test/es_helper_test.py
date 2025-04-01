"""Unit tests for the ElasticsearchHelper class."""

import unittest
from unittest.mock import Mock, patch
import requests

from helper.elasticsearch_helper import ElasticsearchHelper

class TestElasticsearchHelper(unittest.TestCase):
    """Test suite for ElasticsearchHelper class functionality."""

    def setUp(self):
        self.cluster_url = "http://localhost:9200"
        self.username = "elastic"
        self.password = "password"
        self.helper = ElasticsearchHelper(self.cluster_url, self.username, self.password)

    def test_init(self):
        """Test helper initialization"""
        self.assertEqual(self.helper.base_url, self.cluster_url)
        self.assertEqual(self.helper.session.auth, (self.username, self.password))
        self.assertEqual(self.helper.session.headers['Content-Type'], 'application/json')
        self.assertEqual(self.helper.session.headers['Accept'], 'application/json')

    def test_real_cluster_connection(self):
        """Test connecting to a real ES cluster"""
        try:
            real_cluster_url = "http://10.100.140.222:9200"
            real_username = "elastic"
            real_password = "hubble123456"

            helper = ElasticsearchHelper(real_cluster_url, real_username, real_password)
            health = helper.cluster_health()
            
            # Basic health check assertions
            self.assertIn('status', health)
            self.assertIn('cluster_name', health)
            self.assertIn('number_of_nodes', health)
            
            # Get cluster info
            info = helper.cluster_info()
            self.assertIn('version', info)
            self.assertIn('cluster_name', info)
            
        except requests.RequestException as e:
            self.fail(f"Could not connect to real cluster: {str(e)}")

    @patch('requests.Session')
    def test_make_request(self, mock_session):
        """Test _make_request method"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_session.return_value.request.return_value = mock_response

        helper = ElasticsearchHelper(self.cluster_url, self.username, self.password)
        result = helper._make_request('GET', '/_test')
        
        self.assertEqual(result, {"status": "ok"})
        mock_session.return_value.request.assert_called_once()

    @patch('requests.Session')
    def test_cluster_health(self, mock_session):
        """Test cluster_health method"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "green"}
        mock_session.return_value.request.return_value = mock_response

        helper = ElasticsearchHelper(self.cluster_url, self.username, self.password)
        result = helper.cluster_health()
        
        self.assertEqual(result, {"status": "green"})
        mock_session.return_value.request.assert_called_with(
            'GET', 
            'http://localhost:9200/_cluster/health'
        )

    @patch('requests.Session')
    def test_cluster_info(self, mock_session):
        """Test cluster_info method"""
        mock_response = Mock()
        mock_response.json.return_value = {"version": {"number": "7.10.0"}}
        mock_session.return_value.request.return_value = mock_response

        helper = ElasticsearchHelper(self.cluster_url, self.username, self.password)
        result = helper.cluster_info()
        
        self.assertEqual(result, {"version": {"number": "7.10.0"}})
        mock_session.return_value.request.assert_called_with(
            'GET',
            'http://localhost:9200/'
        )

    @patch('requests.Session')
    def test_search(self, mock_session):
        """Test search method"""
        mock_response = Mock()
        mock_response.json.return_value = {"hits": {"total": 0, "hits": []}}
        mock_session.return_value.request.return_value = mock_response

        helper = ElasticsearchHelper(self.cluster_url, self.username, self.password)
        query = {"query": {"match_all": {}}}
        result = helper.search("test-index", query)
        
        self.assertEqual(result, {"hits": {"total": 0, "hits": []}})
        mock_session.return_value.request.assert_called_with(
            'POST',
            'http://localhost:9200/test-index/_search',
            json=query
        )

    @patch('requests.Session')
    def test_request_error(self, mock_session):
        """Test error handling"""
        mock_session.return_value.request.side_effect = requests.RequestException("Connection error")

        helper = ElasticsearchHelper(self.cluster_url, self.username, self.password)
        
        with self.assertRaises(requests.RequestException):
            helper._make_request('GET', '/_test')
