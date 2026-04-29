from test.bootstrap import dcdownloader
from dcdownloader.scheduler import Scheduler
from dcdownloader.parser.SimpleParser import SimpleParser
from test.testserver.server import book
import copy
import pytest


pytestmark = pytest.mark.usefixtures('test_server')

class TransformParser(SimpleParser):
    filename_extension = 'txt'

    async def parse_downloaded_data(self, data):
        return b'transformed image bytes'


class TestScheduler(object):
    
    test_server_url = 'http://localhost:32321'
    s = Scheduler(test_server_url, output_path='/tmp')

    def test___get_chapter_list(self):
        correct_result = {}
        for k in book.keys():
            correct_result.setdefault(k, '/' + k)

        result = self.s._get_chapter_list(self.test_server_url)
        
        assert result == correct_result

    def test__get_image_url_list(self):
        
        target_url_list = {}
        for k in book.keys():
            target_url_list.setdefault(k, self.test_server_url +'/' + k)

        result = self.s._get_image_url_list(target_url_list)

        assert result == book

    def test__start_download(self):
        test_data = copy.deepcopy(book)
        for (a, b) in test_data.items():
            for (c, d) in test_data[a].items():
                test_data[a][c] = self.test_server_url + test_data[a][c]
        
        self.s._start_download(test_data, 'test')

    def test__start_download_applies_parser_download_transform(self, tmp_path):
        scheduler = Scheduler(
            self.test_server_url,
            output_path=str(tmp_path),
            parser=TransformParser(),
        )
        scheduler._start_download(
            {'section': {'image': self.test_server_url + '/static/test.png'}},
            'collection',
        )

        saved_file = tmp_path / 'collection' / 'section' / 'image.txt'
        assert saved_file.read_bytes() == b'transformed image bytes'

    def test__get_info(self):
        info = self.s._get_info(self.test_server_url)

        assert info['name'] == 'test_collection'
