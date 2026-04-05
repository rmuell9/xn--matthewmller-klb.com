import os
import datetime
import conversion
from xml.etree.ElementTree import Element, SubElement, tostring


def generate_rss_feed(content_dir, dest_path, site_url, site_title, 
                     site_description):
    rss_root = Element("rss", version="2.0")
    channel = SubElement(rss_root, "channel")

    SubElement(channel, "title").text = site_title
    SubElement(channel, "link").text = site_url
    SubElement(channel, "description").text = site_description
    SubElement(channel, "language").text = "en-us"

    index_path = os.path.join(content_dir, 'index.md')
    linked_posts = set()
    try:
        with open(index_path, 'r') as f:
            index_content = f.read()
            import re
            links = re.findall(r'\[.*?\]\((.*?)\)', index_content)
            for link in links:
                if not link.startswith(('http://', 'https://', 'mailto:')):
                    if link.endswith('.html'):
                        link = link[:-5]
                    if link.startswith('/'):
                        link = link[1:]
                    linked_posts.add(link)
    except Exception as e:
        print(f"Error reading index.md: {e}")

    posts = []
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)

                if file_path == index_path:
                    continue

                if file_path.endswith('index.md'):
                    rel_path = os.path.relpath(file_path, content_dir)
                    rel_dir = os.path.dirname(rel_path)
                    if rel_dir and rel_dir not in linked_posts:
                        continue
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    title = conversion.extract_title(content)
                    mtime = os.path.getmtime(file_path)
                    pub_date = datetime.datetime.fromtimestamp(mtime)
                    rel_path = os.path.relpath(file_path, content_dir)
                    url_path = rel_path[:-3] + '.html'  # .md -> .html
                    if url_path.endswith('/index.html'):
                        url_path = url_path[:-10]  # Remove /index.html
                    elif url_path == 'index.html':
                        url_path = ''
                    url = f"{site_url}/{url_path}".replace('\\', '/')
                    posts.append({
                        'title': title,
                        'url': url,
                        'pub_date': pub_date,
                        'content': content,
                        'rel_path': rel_path
                    })
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    posts.sort(key=lambda x: x['pub_date'], reverse=True)

    for post in posts[:20]:  # Limit to 20 most recent
        item = SubElement(channel, "item")
        SubElement(item, "title").text = post['title']
        SubElement(item, "link").text = post['url']
        SubElement(item, "pubDate").text = post['pub_date'].strftime(
            '%a, %d %b %Y %H:%M:%S GMT')

        lines = post['content'].split('\n')
        description = ""
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#### '):
                description = line[5:]  # Remove the #### prefix
                break

        guid = SubElement(item, "guid", isPermaLink="false")
        guid_path = post['rel_path']
        if guid_path.endswith('/index.md'):
            guid_path = guid_path[:-9] + '/'
        elif guid_path == 'index.md':
            guid_path = '/'
        guid.text = guid_path
        SubElement(item, "description").text = description or post['title']

    rss_string = tostring(rss_root, encoding='unicode')
    with open(dest_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(rss_string)
