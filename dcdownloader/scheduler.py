import asyncio
import logging
from contextlib import asynccontextmanager

import aiofiles
import aiohttp
import filetype

from dcdownloader import base_logger, utils
# for test
from dcdownloader.parser.SimpleParser import SimpleParser
from dcdownloader.utils import retry
from .aiohttp_proxy_connector import ProxyConnector
logger = base_logger.getLogger(__name__)
                                                                                                   
class Scheduler(object):
    download_total_number = 0
    download_complete_number = 0

    def __init__(self, url, output_path='.', name='Scheduler', max_connection_num=10, max_retry_num=5,
                    proxy=None, header=None, save_manifest_file=False, parser=None,
                    fetch_only=False, verify_ssl=True):
        
        # usable config:
        # name: Scheduler instance name
        # url: url of target image collection
        # downloader_max_connection_num: max connection number for downloading
        # downloader_max_retry_num: max retry number for downloading
        # proxy: proxy setting (e.g: http://127.0.0.1:1081)
        # header: http request header
        # save_manifest_file: (not complete)
        self.url = url
        self.output_path = output_path
        self.name = name
        self.max_connection_num = max_connection_num
        self.max_retry_num = max_retry_num
        self.proxy = proxy
        self.header = None
        self.save_manifest_file = False
        self.fetch_only = fetch_only
        self.verify_ssl = verify_ssl

        self.sema = asyncio.Semaphore(self.max_connection_num)

        self.parser = parser or SimpleParser()

        if getattr(self.parser, 'request_header', None):
            self.header = self.parser.request_header

        self.aiohttp_session = None

    @asynccontextmanager
    async def _request_session(self):
        timeout = aiohttp.ClientTimeout(total=30)
        connector = ProxyConnector(proxy=self.proxy, verify_ssl=self.verify_ssl)
        async with aiohttp.ClientSession(
            connector=connector,
            headers=self.header,
            timeout=timeout,
        ) as session:
            self.aiohttp_session = session
            try:
                yield session
            finally:
                self.aiohttp_session = None

    def run(self):
        logger.info('Using parser %s ..', type(self.parser).__name__)
        logger.info('Fetch information')
        info = self._get_info(self.url)

        if not info:
            logger.error('No collection information found.')
            return
        else:
            logger.info('Collection name: %s', info.get('name'))
        
        logger.info('Fetch chapter list')
        clist = self._get_chapter_list(base_url=self.url)

        if not clist:
            logger.error('No chapter list found')
            return
        else:
            logger.info('Chapter number: %d', len(clist))
        
        logger.info('Fetch image url list')
        img_list = self._get_image_url_list(clist)
        logger.info('Total image number: %s', self.total_image_num)
        logger.info('Start download images')
        self._start_download(img_list, info['name'])
        logger.info('Download comlpleted')
    
    def _get_info(self, base_url):
        info = {}

        logger.debug('Fetching target information')
        @retry(max_num=self.max_retry_num, 
            on_retry=lambda err, args, retry_num: logger.warning('Failed to get info %s (%s), retrying.', args[0][0],str(err)), 
            on_fail=lambda err, args, retry_num: logger.error('Failed to get info %s (%s)', args[0][0],str(err)),
            on_fail_exit=True) 
        async def fetch(url):
            #async with aiohttp.ClientSession(connector=ProxyConnector(proxy='http://192.168.28.1:8888')) as sess:
            async with self._request_session() as session:
                async with session.get(url, ssl=self.verify_ssl) as resp:
                    nonlocal info
                    ret_data = await resp.text()
                    info = await self.parser.parse_info(ret_data)
        
        asyncio.run(fetch(base_url))

        return info


    def _get_chapter_list(self, base_url):
        logger.debug('Starting fetch chapter list')
        chapter_list = {}

        # chapter_list = {
        #     'chapter_name': 'url'
        # }

        # @retry(stop=stop_after_attempt(self.max_retry_num))
        # @retry(max_num=self.max_retry_num)
        @retry(max_num=self.max_retry_num, 
            on_retry=lambda err, args, retry_num: logger.warning('Failed to fetch chapter list %s (%s), retrying.', args[0][0],str(err)), 
            on_fail=lambda err, args, retry_num: logger.error('Failed to fetch chapter list %s (%s)', args[0][0],str(err)),
            on_fail_exit=True) 
        async def runner():
            async with self._request_session() as session:
                await fetch(session, base_url)

        async def fetch(session, url, page=1):
            async with self.sema:
                async with session.get(url, ssl=self.verify_ssl) as ret:

                    ret_data = await ret.text()
                    parsed_data = await self.parser.parse_chapter(ret_data)

                    if self.parser.chapter_mode:
                        chapter_list.update( parsed_data[0] )
                    else:
                        for i in parsed_data[0]:
                            chapter_list.setdefault('{}-{}'.format(page,parsed_data[0].index(i)), i)

                    if len(parsed_data) > 1 and not parsed_data[1] == None:
                        page += 1
                        await fetch(session, parsed_data[1], page)
        
        asyncio.run(runner())

        return chapter_list
        
    
    def _get_image_url_list(self, chapter_list):

        image_url_list = {}
        
        # image_url_list = {
        #     'chapter_name': {
        #         'file_name': 'url'
        #     }
        #     # ...
        # }

        #@retry(max_num=self.max_retry_num, 
        #    on_retry=lambda err, args, num: logger.warning('Failed to fetch chapter list (%s=>%s)', args[0][0], args[0][1]))
        total_image_num = 0
        @retry(max_num=self.max_retry_num, 
            on_retry=lambda err, args, retry_num: logger.warning('Failed to fetch image list "%s" (%s), retrying.', str(args[0]), str(err)), 
            on_fail=lambda err, args, retry_num: logger.error('Failed to fetch image list "%s" (%s)', str(args[0]), str(err)),
            on_fail_exit=True)
        async def runner():
            async with self._request_session() as session:
                future_list = []

                for k, v in chapter_list.items():
                    future_list.append(fetch(session, k, v))

                await asyncio.gather(*future_list)

        async def fetch(session, chapter_name, chapter_url):
            nonlocal total_image_num
            async with self.sema:
                async with session.get(chapter_url, ssl=self.verify_ssl) as resp:
                    image_list = await self.parser.parse_image_list(await resp.text())
                    total_image_num += len(image_list)
                    image_url_list.update({chapter_name: image_list})
        
        asyncio.run(runner())
        self.total_image_num = total_image_num
        return image_url_list
    
    def _start_download(self, image_url_list, collection_name):
        # 解藕希望

        # @retry(stop=stop_after_attempt(self.max_retry_num), after=after_log(logger, logging.DEBUG))
        #@retry(max_num=self.max_retry_num, on_retry=self._downloader_on_retry)
        @retry(max_num=self.max_retry_num, 
            on_retry=lambda err, args, retry_num: logger.warning('Failed to update downloading status (%s), retrying.', str(err)), 
            on_fail=lambda err, args, retry_num: logger.error('Failed to update downloading status (%s)', str(err)) )
        async def update_count(save_path, name):
            logger.info('Download complete: %s', self._generate_download_info(name, save_path))
            self.download_complete_number += 1
            on_file_saved = getattr(self.parser, 'on_file_saved', None)
            if on_file_saved:
                on_file_saved(save_path=save_path, name=name)
        
        # @retry(stop=stop_after_attempt(self.max_retry_num), after=after_log(logger, logging.DEBUG))
        # @retry(max_num=self.max_retry_num, on_retry=self._downloader_on_retry)
        @retry(max_num=self.max_retry_num, 
            on_retry=lambda err, args, retry_num: logger.warning('Failed to save file "%s" (%s), retrying.', args[1]['save_path'],str(err)), 
            on_fail=lambda err, args, retry_num: logger.error('Failed to save file "%s" (%s)', args[1]['save_path'],str(err))) 
        async def save_file(binary, save_path, name): 
            logger.debug('Saving file %s', self._generate_download_info(name, save_path))
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(binary)
                await update_count(save_path=save_path, name=name)
        

        @retry(max_num=self.max_retry_num, 
            on_retry=lambda err, args, retry_num: logger.warning('Failed to request url "%s" (%s), retrying.', args[1]['image_url'], str(err)), 
            on_fail=lambda err, args, retry_num: logger.error('Failed to request target "%s" (%s)', args[1]['image_url'], str(err)) )
        async def runner():
            async with self._request_session() as session:
                future_list = []

                for k, v in image_url_list.items():
                    for name, url in v.items():
                        # path = '_temp/' + collection_name +  k + '/'+ name
                        if 'chapter_mode' in dir(self.parser) and not self.parser.chapter_mode:
                            path = '/'.join([self.output_path, collection_name, name])
                        else:
                            path = '/'.join([self.output_path, collection_name, k, name])

                        future_list.append(download(session, image_url=url, save_path=path, name=name))

                await asyncio.gather(*future_list)

        async def download(session, image_url, save_path, name):
            async with self.sema:
                logger.info('Start download: %s', self._generate_download_info(name, save_path))
                utils.mkdir('/'.join(save_path.split('/')[:-1]))
                #async with aiohttp.ClientSession(headers=self.header) as session:

                if self.fetch_only:
                    logger.warning('Fetch only mode is on, all downloading process will not run')
                    return
                
                async with session.get(image_url, ssl=self.verify_ssl) as resp:
                    resp_data = await resp.content.read()
                    resp_data = await self.parser.parse_downloaded_data(resp_data)

                    filename_extension = getattr(self.parser, 'filename_extension', None)
                    if not filename_extension:
                        guessed_filetype = filetype.guess(resp_data)
                        filename_extension = guessed_filetype.extension if guessed_filetype else None
                    
                    if filename_extension:
                        save_path += '.' + filename_extension
                    else:
                        logger.warning('unknown filetype')
                    
                    # return (resp_data, save_file)
                    await save_file(binary=resp_data, save_path=save_path, name=name)
            
        asyncio.run(runner())
    

    def _generate_download_info(self, name, path):
        return name + ' => '+ path


    def _downloader_on_retry(self, err, args, retry_num):
        logger.warning('Download fail (%s) %s, retry number: %s', str(err), 
            self._generate_download_info(args[1]['name'], args[1]['save_path']), retry_num)

    def _close_request_session(self):
        if self.aiohttp_session and not self.aiohttp_session.closed:
            asyncio.run(self.aiohttp_session.close())

    def __del__(self):
        pass
    
    def _call_parser_hook(self, hook_name):
        pass
