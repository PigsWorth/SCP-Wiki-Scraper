# SCP-Wiki Web-Scraping & Narrative Analysis
A web scraping program designed to scrape the SCP Wikipedia writing forum and discover relationships between disparate articles across the site via embedded links and redirects. Once discovered this data is formatted into objects representing the integer number of the article (ex. SCP-2481 --> 2481), the text from the article, links present in the article, and other articles that link to the current one.

The data representing the inbound and outbound links from a given article is then formatted into a JSON file and will be fed into a force-directed diagram, giving a visual representation of the connections between articles and their various weights.
