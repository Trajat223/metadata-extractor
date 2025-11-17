# src/docx_utils.py

import zipfile
import datetime
from lxml import etree


def extract_docx_metadata(file_path):
    """Extract metadata from DOCX files using docProps XML."""

    metadata = {"core": {}, "app": {}}

    try:
        with zipfile.ZipFile(file_path, 'r') as docx:
            # ---- Extract core metadata ----
            if "docProps/core.xml" in docx.namelist():
                core_xml = docx.read("docProps/core.xml")
                core_tree = etree.fromstring(core_xml)
                ns = {
                    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
                    "dc": "http://purl.org/dc/elements/1.1/",
                    "dcterms": "http://purl.org/dc/terms/"
                }

                tags = {
                    "title": "dc:title",
                    "subject": "dc:subject",
                    "creator": "dc:creator",
                    "keywords": "cp:keywords",
                    "description": "dc:description",
                    "last_modified_by": "cp:lastModifiedBy",
                    "revision": "cp:revision",
                    "created": "dcterms:created",
                    "modified": "dcterms:modified",
                }

                for key, xml_tag in tags.items():
                    node = core_tree.find(xml_tag, ns)
                    if node is not None:
                        metadata["core"][key] = node.text

            # ---- Extract app metadata ----
            if "docProps/app.xml" in docx.namelist():
                app_xml = docx.read("docProps/app.xml")
                app_tree = etree.fromstring(app_xml)

                app_tags = [
                    "Application",
                    "Pages",
                    "Words",
                    "Characters",
                    "Lines",
                    "Paragraphs",
                ]

                for tag in app_tags:
                    node = app_tree.find(tag)
                    if node is not None:
                        metadata["app"][tag.lower()] = node.text

    except Exception as e:
        metadata["error"] = str(e)

    return metadata

