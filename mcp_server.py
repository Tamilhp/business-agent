from typing import Any, Dict, List, Optional, Tuple
from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi


# Initialize FastMCP Server
mcp = FastMCP("business-agent")


# Helper functions
def format_transcript_response(transcript_object: str) -> str:
    """
    Formats the youtube transcript response
    """
    transcripts: list[str] = []
    for snippet in transcript_object:
        transcripts.append(snippet.text)
    final_transcript = "".join(transcripts)
    return final_transcript


# tool execution handler
@mcp.tool()
def fetch_youtube_transcript(video_id: str) -> str:
    """
    Fetch the youtube transcipt give a video_id
    Args:
        video_id: For eg: https://www.youtube.com/watch?v=12345 the ID is 12345

    Returns:
        Transcript of the given video_id
    """
    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(video_id)
    final_transcript = format_transcript_response(fetched_transcript)
    return final_transcript


@mcp.prompt()
def business_agent(video_link: str) -> str:
    return f"""
        You're an expert in drawing the insights from an extract and distill the important points discussed in it and extract the main business idea of the context. You will be given a transcript of a youtube video mainly focused on business discussions.
        As an shrewd business expert, you shoud do the following:

        1) Given a context you should understand what is the business context that is being discussed and derive a title for your response.
        2) Once you understand the context and decide on a title, you have to summarize the content presented to you, extract the key insishts.
        3) If the given context doesn't discuss any businees or if it is totally unrelated, you can use the tools of your interest and suggest the user with ideas that he/she can explore.
        4) Once you are done with the title, summary, insights and the main idea that is being discussed, you have to search the internet to supplement your understanding by adding additional informatio about the business.
        5) You should also understand the competitors in the space using the search and the initial investment, operational cost involved.
        6) Finally, you have to give a comprehensive and an exhaustive report of the business idea covering every edge cases, risks and profit opportunities.

        Note: The context mainly comes from a youtube video and you will be given with a youtube video link.

        The link of the youtube video is: {video_link}
    """


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
