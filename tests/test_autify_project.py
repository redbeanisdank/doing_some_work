from autify_project import __version__
from unittest import TestCase
from unittest.mock import patch, MagicMock
from autify_project.main import get_url_data, download_url_contents, fetch
from os import getcwd, remove


def test_version():
    assert __version__ == '0.1.0'


class TestMain(TestCase):

    @patch("autify_project.main.requests")
    def test_get_url_data_success(self, mock_request):
        mock_request.get.return_value = MagicMock()
        mock_request.get.return_value.content = 'fake_content'
        title, contents = get_url_data("https://www.google.com")
        self.assertEqual(title, "www.google.com")
        self.assertEqual(contents, mock_request.get.return_value.content)

    @patch("autify_project.main.requests")
    def test_get_url_data_raises_exception_request_fail(self, mock_request):
        mock_request.get.side_effect = Exception('There was an exception.')
        with self.assertRaises(Exception) as context:
            title, contents = get_url_data("https://www.google.com")
            self.assertEqual(title, "www.google.com")
            self.assertTrue('There was an exception.' in context.exception)

    def test_download_url_contents_success(self):
        download_url_contents('www.fake.com', b'fake_google_content')
        with open(f'{getcwd()}/www.fake.com.html', 'r') as fake_html_file:
            self.assertEqual('fake_google_content', fake_html_file.read())
        remove(f'{getcwd()}/www.fake.com.html')

    def test_download_url_contents_raises_exception(self):
        url_contents = MagicMock()
        url_contents.decode.side_effect = Exception("There was a problem writing file.")
        with  self.assertRaises(Exception) as context:
            download_url_contents('www.fake.com', url_contents)
            self.assertTrue("There was a problem writing file." in context.exception)

    @patch("autify_project.main.requests")
    def test_fetch_success(self, mock_requests):
        fake = MagicMock()
        fake.content = b'content_fake_response'
        stuff = MagicMock()
        stuff.content = b'content_stuff_response'
        mock_requests.get.side_effect = (fake, stuff,)
        urls = ['https://www.fake.com', 'https://www.stuff.com']
        fetch(urls)
        for url in urls:
            url_suffix = url.split("//")[-1]
            company = url_suffix.split('.')[1]
            with open(f'{getcwd()}/{url_suffix}.html', 'r') as fake_html_file:
                self.assertEqual(f'content_{company}_response', fake_html_file.read())
                remove(f'{getcwd()}/{url_suffix}.html')

    @patch("autify_project.main.get_url_data")
    def test_fetch_fail(self, mock_get_url_data):
        mock_get_url_data.side_effect = Exception("fake exception")
        urls = ['https://www.fake.com', 'https://www.stuff.com']
        for url in urls:
            with  self.assertRaises(Exception) as context:
                fetch([url])
                self.assertTrue("fake exception" in context.exception)