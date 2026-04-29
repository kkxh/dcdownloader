from abc import ABCMeta, abstractmethod

class BaseParser(metaclass=ABCMeta):

    # Optional fixed filename extension for downloaded images.
    filename_extension = None

    # Optional HTTP headers used when fetching the target site.
    request_header = None

    # Set to False when the target page has no section/chapter layer and
    # parse_chapter returns a flat list of page URLs.
    chapter_mode = True

    @abstractmethod
    async def parse_info(self, data):
        """Parse collection metadata from the target page.

            Args:
                data: Text returned from requesting the target URL.
            
            Returns:
                {
                    'name': 'collection name'
                }
        """
    

    @abstractmethod
    async def parse_chapter(self, data):
        """Parse section/page URLs from the target page.

            Args:
                data: Text returned from requesting the target URL.

            Returns: 
                When self.chapter_mode is True (default):
                (
                    {
                        'section_name': 'section_url'
                    },
                    'url_of_next_section_page(optional)'
                )

                When self.chapter_mode is False:
                (
                    (<url1>, <url2>, <url3>, ...),
                    'url_of_next_page(optional)'
                )
        """
    
    @abstractmethod
    async def parse_image_list(self, data):
        """Parse image URLs from a section/page response.

            Args:
                data: Text returned from requesting a section/page URL.
            
            Returns:
                {
                    'file_stem': 'image_url'
                }
        """
    
    async def parse_downloaded_data(self, data):
        """Optionally transform downloaded image bytes before saving.

            Args:
                data: Bytes returned from requesting an image URL.
            
            Returns:
                Bytes to write to disk.
        """
        return data
