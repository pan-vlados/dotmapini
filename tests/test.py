import unittest
import configparser
from typing import Dict
from pathlib import Path
from tempfile import NamedTemporaryFile
from collections import deque, namedtuple


from src.dotmapini import Config, DigitInSectionNameError


class TestConfig(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.path: Path = Path(__file__).absolute().parent
        cls.parser = configparser.ConfigParser()
        test_data: Dict[str, Dict[str, str]] = {  # TODO: random/mock
            'APP': {'debug': 'False'}, 
            'DB': {'name': 'postgres'}, 
            'DB.settings': {'host': 'localhost', 'database': 'test', 'user': 'username', 'password': 'password'},
            'server': {'host': '127.0.0.1', 'port': '8080'},
            'server.site': {'name': 'test_site'},
            'server.site.urls': {'base': 'https://test.web.com'},
            'DEFAULT': {'section': 'option'}  # TODO: test no defaults in all dicts, except it interpoltae anywhere
            }
        cls.parser.read_dict(test_data)
        with NamedTemporaryFile(
            mode='w+', dir=cls.path, suffix='.ini', delete=False
            ) as cls.tmpfile:
            cls.parser.write(cls.tmpfile)
            cls.tmpfile.close()
            del cls.parser

    def setUp(self):
        self.config = Config(  # TODO: random/mock
            {  # type: ignore
                'DEFAULT': Config({'section': 'option'}), 
                'APP': Config({'debug': False, 'section': 'option'}),  # type: ignore 
                'DB': Config(
                    {  # type: ignore
                        'name': 'postgres', 
                        'section': 'option', 
                        'settings': Config({'host': 'localhost', 'database': 'test', 'user': 'username', 'password': 'password', 'section': 'option'})
                        }
                    ), 
                'server': Config(
                    {  # type: ignore
                        'host': '127.0.0.1', 'port': 8080, 'section': 'option', 'site': Config({'name': 'test_site', 'section': 'option', 'urls': Config({'base': 'https://test.web.com', 'section': 'option'})})  # type: ignore
                        }
                    )
                }
            )

    def test_load(self):
        config = Config.load(self.tmpfile.name)

    def test_load_with_arguments(self):
        config = Config.load(
            path=self.tmpfile.name, 
            allow_no_value=True, 
            interpolation=configparser.BasicInterpolation()
            )
        configparser.ConfigParser()

    def test_loaded_consistent_data(self):
        self.assertEqual(self.config, Config.load(self.tmpfile.name))

    def test_delitem(self):
        self.assertIn('APP', self.config)
        del self.config.APP
        self.assertNotIn('APP', self.config)
    
    def test_getitem(self):
        self.assertEqual('127.0.0.1', self.config.server.host)

    def test_setitem(self):
        hello_world = 'hello world!'
        self.config.hello_world = hello_world
        self.assertEqual(hello_world, self.config.hello_world)

    def test_raises_digit_in_section_not_allowed(self):
        test_data = (  # TODO: random/mock
            {'incorrect.digit.1.attribute': {'option': 'value'}},
            {'2': {'option': 'value'}}, {'section.3': {'option': 'value'}},
            {'4.section': {'option': 'value'}}
            )
        for i, test_dict in enumerate(test_data):
            with self.subTest(i):
                praser = configparser.ConfigParser()
                praser.read_dict(test_dict)
                self.assertRaises(DigitInSectionNameError, Config, praser)

    def test_parse_value_return(self):
        def get_SextionProxy(key, value) -> configparser.SectionProxy:
            parser = configparser.ConfigParser()
            parser.read_dict({'section': {key: value}})
            return next(value for _, value in parser['section'].items())  # type: ignore

        ReturnData = namedtuple(typename='ReturnType', field_names=('input', 'output'))
        test_data = (  # TODO: random/mock
            ReturnData('false', False),
            ReturnData('fAlsE', False),
            ReturnData('True', True),
            ReturnData('123', 123),
            ReturnData('some string', 'some string'),
            ReturnData('1.23', 1.23),
            ReturnData(get_SextionProxy('section', 'false'), False),
            ReturnData(get_SextionProxy('section', '441'), 441),
            ReturnData("[{'key': ({'value', 'value2'}, [True, 1.2, 3])}]", [{'key': ({'value', 'value2'}, [True, 1.2, 3])}]),
            ReturnData(
                "[{'Jhon': {'roles': ('PUBLIC', 'DEBUG')}, 'Peter': {'roles': None}}]",
                [{'Jhon': {'roles': ('PUBLIC', 'DEBUG')}, 'Peter': {'roles': None}}]
                )

        )

        for i, data in enumerate(test_data, start=1):
            parser = configparser.ConfigParser()
            section = 'test'
            option = f'test{i}'
            parser.read_dict(dictionary={section: {option: data.input}})
            with self.subTest(i):
                self.assertEqual(
                    Config._parse_value(
                        remaining_attributes=deque(),
                        key=option,
                        value=parser[section][option],
                        dict_=parser[section]
                    ),
                    data.output
                )
                
    @classmethod
    def tearDownClass(cls):
        Path(cls.tmpfile.name).unlink()