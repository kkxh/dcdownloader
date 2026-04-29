# Parser Adapter Guide

DCDownloader is a small framework for adapting a target image site quickly. A Parser extracts metadata and image URLs; the Scheduler handles HTTP requests, concurrency, retries, downloading, and folder organization.

## Output Model

The Scheduler writes files in one of two layouts:

```text
OUTPUT_PATH/
  collection_name/
    section_name/
      image_name.ext
```

or, when `chapter_mode = False`:

```text
OUTPUT_PATH/
  collection_name/
    image_name.ext
```

Use `chapter_mode = True` when the target site has a section/chapter/album layer. Use `chapter_mode = False` when the target page is already a flat list of image pages.

## Parser Contract

A Parser should subclass `dcdownloader.parser.BaseParser.BaseParser` and implement three async methods.

```python
from dcdownloader.parser.BaseParser import BaseParser


class TargetSiteParser(BaseParser):
    request_header = {
        "user-agent": "Mozilla/5.0 ...",
    }

    async def parse_info(self, data):
        return {
            "name": "collection_name",
        }

    async def parse_chapter(self, data):
        return (
            {
                "section_name": "https://example.test/section/1",
            },
        )

    async def parse_image_list(self, data):
        return {
            "001": "https://example.test/images/001.jpg",
            "002": "https://example.test/images/002.jpg",
        }
```

### `parse_info(data)`

Return collection metadata parsed from the target URL response.

Required keys:

- `name`: folder name for the downloaded collection.

### `parse_chapter(data)`

Return section URLs or image-page URLs parsed from the target URL response.

For sectioned targets:

```python
return (
    {
        "section_name": "section_url",
    },
    "optional_next_section_page_url",
)
```

For flat targets:

```python
chapter_mode = False

return (
    (
        "image_page_url_1",
        "image_page_url_2",
    ),
    "optional_next_page_url",
)
```

The second tuple item is optional. Omit it when there is no pagination.

### `parse_image_list(data)`

Return the image URLs found on a section or image page.

```python
return {
    "file_stem": "image_url",
}
```

Do not include the filename extension in `file_stem` unless the target naming really needs it. The Scheduler can infer image type from downloaded bytes, or use `filename_extension` when the Parser sets it.

## Optional Parser Attributes And Hooks

- `request_header`: HTTP headers used by the Scheduler.
- `filename_extension`: fixed extension such as `"jpg"` or `"png"` when byte sniffing is not reliable.
- `chapter_mode`: set to `False` for flat image-page targets.
- `parse_downloaded_data(data)`: optionally transform image bytes before saving.
- `on_file_saved(save_path, name)`: optional synchronous hook called after a file is written.

## Adaptation Checklist

1. Identify the target collection title and implement `parse_info`.
2. Decide whether the site is sectioned or flat and set `chapter_mode`.
3. Implement `parse_chapter` for section/page discovery, including pagination if needed.
4. Implement `parse_image_list` for final image URL extraction.
5. Run with `--fetch-only` first to verify URL extraction without downloading images.
6. Run the test suite and add a fixture-backed parser test for any tricky parsing behavior.
