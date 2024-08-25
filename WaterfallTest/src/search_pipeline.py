# Copyright (c) 2024 Braid Technologies Ltd

# Standard Library Imports
import logging
import os
import json
import plotly
import plotly.express as px
import umap.umap_ as umap

from workflow import PipelineItem, Theme, PipelineSpec, get_embeddings_as_float
from web_searcher import WebSearcher
from html_file_downloader import HtmlFileDownloader
from summariser import Summariser
from embedder import Embedder
from cluster_analyser import ClusterAnalyser
from theme_finder import ThemeFinder
from embedding_finder import EmbeddingFinder

# Set up logging to display information about the execution of the script
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)

def sort_array_by_another(arr1: list[Theme], arr2:list[int]) -> list[Theme]:
    
    # Combine the two arrays into a list of tuples
    combined = list(zip(arr2, arr1))
    
    # Sort the combined list by the first element of each tuple (values in arr2)
    combined.sort(reverse=True)
    
    # Extract the sorted arr1 from the combined list
    sorted_arr1 : list[Theme] = [x for _, x in combined]
    
    return sorted_arr1


class WaterfallDataPipeline:
   '''
   Searches for HTML content from a list of links.

   Returns:
      list[str]: A list of HTML content downloaded from the specified links.
   '''

   def __init__(self, output_location: str):
      self.output_location = output_location       
      return
       

   def search (self, spec: PipelineSpec) -> list[Theme]: 
      '''
      Searches for HTML content from a list of links.

      Returns:
          list[str]: A list of HTML content downloaded from the specified links.
      '''
      searcher = WebSearcher (self.output_location)

      input_items = searcher.search (spec)

      items : list [PipelineItem] = []
      themes : list[Theme] = []

      for item in input_items:

         downloader = HtmlFileDownloader (self.output_location)
         item = downloader.download (item)

         summariser = Summariser (self.output_location)
         item = summariser.summarise (item)

         embedder = Embedder (self.output_location)
         item = embedder.embed (item)      

         items.append (item)        

      cluster_analyser = ClusterAnalyser (items, self.output_location) 
      items = cluster_analyser.analyse(spec.clusters)
      
      accumulated_summaries : list [str] = [""] * spec.clusters
      accumulated_counts : list [int] = [0] * spec.clusters
      accumulated_members : list [list [PipelineItem ]] = [None] * spec.clusters
      for x in range(spec.clusters):
         accumulated_members[x] = []

      # Accumulate a set of summaries and counts of summaries according to classification
      for i, item in enumerate (items):
         cluster = items[i].cluster
         accumulated_summaries[cluster] = accumulated_summaries[cluster] + item.summary
         accumulated_counts[cluster] = accumulated_counts[cluster] + 1
         accumulated_members[cluster].append (item)
     
      # Ask the theme finder to find a theme, then store it
      for i, accumulated_summary in enumerate (accumulated_summaries):
         theme_finder = ThemeFinder ()
         short_description = theme_finder.find_theme (accumulated_summary, 15)
         long_description = theme_finder.find_theme (accumulated_summary, 50)
         theme = Theme()
         theme.member_pipeline_items = accumulated_members[i]
         theme.short_description = short_description
         theme.long_description = long_description
         themes.append (theme)         

      reducer = umap.UMAP()
      logger.debug("Reducing cluster")     
      embeddings_as_float = get_embeddings_as_float (items) 
      embeddings_2d = reducer.fit_transform(embeddings_as_float)

      logger.debug("Generating chart")
      #df = pd.DataFrame({'theme': themes})
      
      # Make a list of theme names which gets used as the legend in the chart
      theme_names : list [str] = []
      for item in items:
         theme_name = themes[item.cluster].short_description     
         theme_names.append(theme_name)
      
      fig = px.scatter(x=embeddings_2d[:, 0], y=embeddings_2d[:, 1], color=theme_names)

      # save an interactive HTML version
      html_path = os.path.join(self.output_location, spec.output_chart_name)      
      plotly.offline.plot(fig, filename=html_path)      

      logger.debug("Ordering themes")
      ordered_themes = sort_array_by_another(themes, accumulated_counts)

      logger.debug("Finding nearest embedding")
      # Now we are looking for articles that best match the themes
      embedding_finder = EmbeddingFinder (embeddings_as_float, self.output_location)

      # Ask the embedding finder to find nearest article for each theme
      for theme in ordered_themes:
         nearest_items : list [PipelineItem]= []         
         nearest_embedding = embedding_finder.find_nearest (theme.long_description)
         for item in items:
            # TODO - accumulate top 3 items per theme
            if item.embedding_as_float == nearest_embedding:
               nearest_items.append(item)  
               theme.example_pipeline_items = nearest_items
               break            

      logger.debug("writing output")
      output_results = []
      for i, item in enumerate(items):
         output_item = dict()
         output_item["summary"] = item.summary
         output_item["embedding"] = item.embedding
         output_item["path"] = item.path
         output_item["theme"] = theme_names[i]
         output_results.append (output_item)
      
      # save the test results to a json file
      output_file = os.path.join(self.output_location, "test_output.json")
      with open(output_file, "w+", encoding="utf-8") as f:
         json.dump(output_results, f)        
        
      return ordered_themes
      
        

