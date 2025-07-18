#!/usr/bin/env python
import os
from dotenv import load_dotenv

load_dotenv()

from crewai.flow import Flow, listen, start
from firecrawl import FirecrawlApp, ScrapeOptions
from .crews.summary_crew.summary_crew import SummaryCrew
from .models import SearchResult, FireCrawlState
from .utils.file_operations import save_search_results_to_markdown

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

class FireCrawlFlow(Flow[FireCrawlState]):

    @start()
    def get_query(self):
        print("Query: ", self.state.query)
        print("Limit: ", self.state.limit)

    @listen(get_query)
    def perform_search(self):
        print("Performing search on", self.state.query)
        search_result = app.search(
            query=self.state.query,
            limit=self.state.limit,
            scrape_options=ScrapeOptions(formats=["markdown", "links"]),
            tbs="qdr:w"
        )
        
        search_results = []
        
        for result in search_result.data:
            search_results.append(SearchResult(
                title=result['title'],
                url=result['url'],
                description=result['description'],
                markdown=result['markdown'],
                links=result['links']
            ))
        
        self.state.search_result = search_results
        print("Search results: ", len(self.state.search_result), "results found")
        print(self.state.search_result)
        
    @listen(perform_search)
    def create_summary(self):
        print("Creating summary of search results")
        
        for result in self.state.search_result:
            result = (
                SummaryCrew()
                .crew()
                .kickoff(inputs={"results": result.markdown})
            )
            print("Summary created", result.pydantic)
            self.state.summaries.append(result.pydantic)
        
        print("Summaries created", self.state.summaries)
        
    @listen(create_summary)
    def save_search_result(self):
        save_search_results_to_markdown(
            query=self.state.query,
            search_results=self.state.search_result,
            summaries=self.state.summaries,
            limit=self.state.limit
        )

def kickoff(query: str, limit: int):
    firecrawl_flow = FireCrawlFlow()
    firecrawl_flow.kickoff(inputs={"query": query, "limit": limit})

if __name__ == "__main__":
    user_input_query = input("Enter a query: ")
    user_input_limit = input("Enter a limit on search results (default is 3): ")
    if user_input_limit == "":
        user_input_limit = 3
    else:
        user_input_limit = int(user_input_limit)
        
    kickoff(user_input_query, user_input_limit)
