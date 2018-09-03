import random
import unittest
from unittest.mock import Mock, MagicMock, PropertyMock

import botutils


class TestBotutils(unittest.TestCase):
    def setUp(self):
        self.message = MagicMock()
        self.prop = PropertyMock()

    def test_is_channel_valid_empty_config(self):
        self.prop.return_value = 'can be anything'
        type(self.message.channel).name = self.prop

        ret_val = botutils.is_channel_valid({}, 'anything', self.message)
        self.assertTrue(ret_val)
        self.prop.assert_not_called()

    def test_is_channel_valid_valid_config(self):
        self.prop.return_value = 'valid channel name'
        type(self.message.channel).name = self.prop

        ret_val = botutils.is_channel_valid({'attribute': ['valid channel name']}, 'attribute', self.message)
        self.assertTrue(ret_val)
        self.prop.assert_called_once_with()

    # Helper
    def has_prefix_helper(self, config_prefix, actual_prefix, expected):
        self.prop.return_value = f'{actual_prefix}foo bar it'
        type(self.message).content = self.prop

        ret_val = botutils.has_prefix({'prefix': config_prefix}, self.message)
        self.assertEqual(ret_val, expected)
        self.prop.assert_called_once_with()

    def test_has_prefix_valid_len_one(self):
        self.has_prefix_helper('!', '!', True)

    def test_has_prefix_valid_len_random(self):
        prefix = '!' * random.randint(0, 100)
        self.has_prefix_helper(prefix, prefix, True)

    def test_has_prefix_valid_invalid(self):
        self.has_prefix_helper('a', 'b', False)

    # Helper
    def get_content_without_prefix_helper(self, prefix, message, expected):
        self.prop.return_value = message
        type(self.message).content = self.prop

        ret_val = botutils.get_content_without_prefix({'prefix': prefix}, self.message)
        self.assertEqual(ret_val, expected)
        self.prop.assert_called_once_with()

    def test_get_content_without_prefix_prefix_len_one(self):
        self.get_content_without_prefix_helper('!', '!one two three', 'one two three')

    def test_get_content_without_prefix_prefix_len_random(self):
        prefix = '!' * random.randint(0, 100)
        self.get_content_without_prefix_helper(prefix, f'{prefix}one two three', 'one two three')
