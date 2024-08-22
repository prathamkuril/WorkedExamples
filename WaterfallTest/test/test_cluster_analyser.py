# Copyright (c) 2024 Braid Technologies Ltd

# Standard Library Imports
import pytest
import os
import shutil
import sys
import logging

# Set paths tp find the 'src' directory
test_root = os.path.dirname(__file__)
parent= os.path.abspath(os.path.join(test_root, '..'))
src_dir = os.path.join(parent, 'src')
sys.path.extend([parent, src_dir])

# Set up logging to display information about the execution of the script
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)

from src.workflow import PipelineItem
from src.cluster_analyser import ClusterAnalyser
from src.html_file_downloader import HtmlFileDownloader
from src.summariser import Summariser
from src.embedder import Embedder

# Fixture to create a temporary directory for test output
@pytest.fixture
def test_output_dir(tmpdir):
    dir_path = tmpdir.mkdir("test_output")
    logger.info(f"Created temporary test output directory: {dir_path}")
    yield str(dir_path)
    # Clean up after the test
    logger.info(f"Cleaning up test output directory: {dir_path}")
    shutil.rmtree(str(dir_path))

def test_basic (test_output_dir):
    test_path = 'test'
    test_output_location = test_output_dir

    items: list [PipelineItem] = []
    item: PipelineItem = PipelineItem()
    item.path = test_path
    item.embedding = "[1.0,2.0]"
    item.embedding_as_float = Embedder.textToFloat (item.embedding)    
    items.append (item)
        
    analyser = ClusterAnalyser (items, test_output_location)

    assert len(analyser.items) == 1  
    assert analyser.output_location == test_output_location
  

def test_with_output (test_output_dir):
    
    test_root = os.path.dirname(__file__)
    os.chdir (test_root)
    test_paths = ['cluster_test_1.html', 'cluster_test_2.html', 'cluster_test_3.html', 'cluster_test_4.html', 'cluster_test_5.html']
    test_output_location = 'test_output'

    items: list [PipelineItem] = []
    item: PipelineItem = PipelineItem()

    for test_path in test_paths:
       downloader = HtmlFileDownloader (test_path, test_output_location)
       text = downloader.download () 

       summariser = Summariser (test_path, test_output_location)   
       summary = summariser.summarise (text) 

       embedder = Embedder (test_path, test_output_location)
       embedding = embedder.embed (summary)   
       
       item.path = test_path
       item.embedding = embedding
       item.embedding_as_float = Embedder.textToFloat (item.embedding) 
       items.append (item)

    cluster_analyser = ClusterAnalyser (items, test_output_location) 
    clusters = cluster_analyser.analyse (2)

    assert len(clusters) == len(items)