
import logging
import requests
import xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

# Configure logging
logging.basicConfig(filename='pubmed_search.log', level=logging.INFO, format='%(asctime)s - %(message)s')

mcp = FastMCP("PubmedSearch")

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

@mcp.tool()
async def search_pubmed(title_abstract_keywords: List[str] = [], authors: List[str] = [], num_results: int = 10) -> Dict[str, Any]:
    """
    Search the PubMed database using specified keywords and/or author names.

    This function allows users to search the PubMed database by providing keywords
    for titles or abstracts and/or author names. It returns a specified number of
    results in a formatted dictionary.

    Parameters:
    - title_abstract_keywords (List[str]): Keywords to search for in the title or abstract.
    - authors (List[str]): Author names to include in the search. Format: surname followed by initials, e.g., "Doe JP".
    - num_results (int): Maximum number of results to return. Default is 10.

    Returns:
    - Dict[str, Any]: A dictionary containing the success status, a list of results with PubMed IDs,
      links, abstracts, and the total number of results found.
    """
    try:
        query_parts = []
        
        if authors:
            author_query = " OR ".join([f"{author}[Author]" for author in authors])
            query_parts.append(f"({author_query})")
            
        if title_abstract_keywords:
            keyword_query = " OR ".join([f"{keyword}[Title/Abstract]" for keyword in title_abstract_keywords])
            query_parts.append(f"({keyword_query})")
        
        query = " AND ".join(query_parts) if query_parts else ""
        
        if not query:
            return {
                "success": False,
                "error": "No search parameters provided. Please specify authors or keywords.",
                "results": []
            }
        
        logging.info(f"Search query: {query}")
        
        search_url = f"{BASE_URL}/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": num_results,
            "retmode": "json"
        }
        search_response = requests.get(search_url, params=search_params)
        search_data = search_response.json()
        pmids = search_data.get("esearchresult", {}).get("idlist", [])
        
        formatted_results = await format_paper_details(pmids)
        
        return {
            "success": True,
            "results": formatted_results,
            "total_results": len(pmids)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

@mcp.tool()
async def format_paper_details(pubmed_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch and format details of multiple PubMed articles.

    This function retrieves details for a list of PubMed IDs and formats them
    into a list of dictionaries containing article information.

    Parameters:
    - pubmed_ids (List[str]): A list of PubMed IDs to fetch details for.

    Returns:
    - List[Dict[str, Any]]: A list of dictionaries, each containing details of a PubMed article.
    """
    fetch_url = f"{BASE_URL}/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    fetch_response = requests.get(fetch_url, params=fetch_params)
    return parse_article_details(fetch_response.content)

def parse_article_details(xml_content) -> List[Dict[str, Any]]:
    root = ET.fromstring(xml_content)
    articles = root.findall(".//PubmedArticle")
    results = []
    
    for article in articles:
        title = article.findtext(".//ArticleTitle", default="N/A")
        abstract = article.findtext(".//Abstract/AbstractText", default="N/A")
        journal = article.findtext(".//Journal/Title", default="N/A")
        volume = article.findtext(".//Journal/JournalIssue/Volume", default="N/A")
        issue = article.findtext(".//Journal/JournalIssue/Issue", default="N/A")
        pages = article.findtext(".//Pagination/MedlinePgn", default="N/A")
        doi = article.findtext(".//ELocationID[@EIdType='doi']", default="N/A")
        pubdate = article.findtext(".//PubDate/Year", default="N/A")
        
        authors = []
        for author in article.findall(".//Author"):
            lastname = author.findtext("LastName", default="")
            initials = author.findtext("Initials", default="")
            authors.append(f"{lastname} {initials}".strip())
        
        results.append({
            "pubmed_id": article.findtext(".//PMID", default="N/A"),
            "link": f"https://pubmed.ncbi.nlm.nih.gov/{article.findtext('.//PMID', default='N/A')}",
            "title": title,
            "authors": authors,
            "source": journal,
            "volume": volume,
            "issue": issue,
            "pages": pages,
            "doi": doi,
            "pubdate": pubdate,
            "abstract": abstract
        })
    
    return results

if __name__ == "__main__":
    mcp.run()
