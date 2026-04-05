import os
import re
import sys
import shutil
import conversion
import rss
from htmlnode import HTMLNode


def main():
    try:
        basepath = sys.argv[1]
    except:
        basepath = "/"
    def public(copy):
        dest = "docs/"
        if os.path.exists(dest) and os.path.exists(copy):
            for thing in os.listdir(dest):
                target = dest + thing
                if os.path.isfile(target):
                    if thing != "CNAME":
                        os.remove(target)
                elif os.path.isdir(target):
                    shutil.rmtree(target)
            if os.listdir(copy) is not None:
                dir_to_public(copy, dest)

    def dir_to_public(dir, dest):
        for thing in os.listdir(dir):
            target = dir + thing
            if os.path.isfile(target):
                shutil.copy(target, dest)
            if os.path.isdir(target):
                os.mkdir(dest + thing)
                dir_to_public(target + "/", dest + thing + "/")

    def generate_page(from_path, template_path, dest_path, basepath):
        md_content = open(from_path).read()
        template_content = open(template_path).read()
        html_string = conversion.markdown_to_html_node(md_content).to_html()
        title = conversion.extract_title(md_content)
        dir_path = os.path.dirname(from_path)
        path_parts = dir_path.split('/')[1:]  # Remove 'content' prefix
        if path_parts and path_parts[0]:
            # Check each part of the path for matching nav links
            for i, part in enumerate(path_parts):
                if part:
                    pattern = f'<li><a href="/{part}">'
                    replacement = f'<li><a class="active" href="/{part}">'
                    template_content = re.sub(pattern, replacement, 
                                            template_content)
        res = template_content.replace("{{ Title }}", title).replace(
            "{{ Content }}", html_string).replace('href="/', 
            f'href="{basepath}').replace('src="/', f'src="{basepath}')
        open(dest_path, "x").write(res)

    def generate_page_rec(dir_path_content, template_path, dest_dir_path, 
                         basepath):
        if not os.path.exists(dest_dir_path):
            os.makedirs(dest_dir_path)
        for thing in os.listdir(dir_path_content):
            source_path = os.path.join(dir_path_content, thing)
            if os.path.isfile(source_path) and thing.endswith(".md"):
                filename = thing[:-3] + ".html"
                dest_file_path = os.path.join(dest_dir_path, filename)
                generate_page(source_path, template_path, dest_file_path, 
                            basepath)
            elif os.path.isdir(source_path):
                dest_sub_dir = os.path.join(dest_dir_path, thing)
                generate_page_rec(source_path, template_path, dest_sub_dir, 
                                basepath)

    public("static/")
    generate_page_rec("content/", "template.html", "docs/", basepath)
    rss.generate_rss_feed("content/", "docs/index.xml", "https://xn--matthewmller-klb.com/", 
                 "Blog", "Articles")
main()
