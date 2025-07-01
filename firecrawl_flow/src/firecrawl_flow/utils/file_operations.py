"""
File operations utilities for FireCrawl Flow
"""

from typing import List
from ..models import SearchResult, Summary


def save_search_results_to_markdown(
    query: str,
    search_results: List[SearchResult],
    summaries: List[Summary],
    limit: int,
    filename: str = "search_results.md"
) -> None:
    """
    Save search results with AI summaries to a formatted markdown file.
    
    Args:
        query: The search query used
        search_results: List of search results
        summaries: List of AI-generated summaries
        limit: The search limit used
        filename: Output filename (default: "search_results.md")
    """
    print(f"Saving search results with summaries to formatted markdown file: {filename}")
    
    # Create a nicely formatted markdown report
    with open(filename, "w") as f:
        f.write(f"# 📊 Search Results & Analysis for: {query}\n\n")
        f.write(f"**🔍 Query:** {query}  \n")
        f.write(f"**📈 Results Found:** {len(search_results)}  \n")
        f.write(f"**⚙️ Search Limit:** {limit}  \n")
        f.write(f"**🤖 AI Summaries:** {len(summaries)}  \n\n")
        f.write("---\n\n")
        
        for i, (result, summary) in enumerate(zip(search_results, summaries), 1):
            f.write(f"## {i}. {result.title}\n\n")
            f.write(f"**🔗 URL:** [{result.url}]({result.url})  \n")
            f.write(f"**📝 Description:** {result.description}  \n\n")
            
            # Add AI-generated summary
            if summary:
                f.write(f"### 🤖 AI Summary\n\n")
                f.write(f"{summary.summary}\n\n")
                
                # Key Action Items
                if summary.key_action_items:
                    f.write(f"### 🎯 Key Action Items\n\n")
                    for item in summary.key_action_items:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                # Dramatic News Points
                if summary.dramatic_news_points:
                    f.write(f"### 🚨 Dramatic News Points\n\n")
                    for point in summary.dramatic_news_points:
                        f.write(f"- {point}\n")
                    f.write("\n")
                
                # Key Takeaways
                if summary.key_takeaways:
                    f.write(f"### 💡 Key Takeaways\n\n")
                    for takeaway in summary.key_takeaways:
                        f.write(f"- {takeaway}\n")
                    f.write("\n")
            
            # Add found links if any
            if result.links:
                f.write(f"### 🔗 Related Links ({len(result.links)})\n\n")
                for link in result.links[:10]:  # Show max 10 links
                    f.write(f"- {link}\n")
                if len(result.links) > 10:
                    f.write(f"- ... and {len(result.links) - 10} more links\n")
                f.write("\n")
            
            # Add content preview at the end for reference
            if result.markdown:
                f.write(f"<details>\n<summary>📄 Full Content Preview</summary>\n\n")
                f.write(f"```\n{result.markdown[:1000]}")
                if len(result.markdown) > 1000:
                    f.write("...")
                f.write(f"\n```\n\n</details>\n\n")
            
            f.write("---\n\n")
    
    print(f"✅ Search results with AI summaries saved to '{filename}' ({len(search_results)} results, {len(summaries)} summaries)") 