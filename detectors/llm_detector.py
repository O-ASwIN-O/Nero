import logging

try:
    import pygetwindow as gw
except ImportError:
    logging.warning("pygetwindow not installed. LLM website detection won't work.")
    gw = None

def detect_llm_sites() -> list[str]:
    """Detect if any LLM websites are currently open in the active windows."""
    llm_sites = []
    
    if gw is None:
        return llm_sites

    try:
        titles = gw.getAllTitles()
        
        for title in titles:
            if not title:
                continue
                
            if "ChatGPT" in title:
                if "ChatGPT" not in llm_sites:
                    llm_sites.append("ChatGPT")
                    
            if "Claude" in title:
                if "Claude" not in llm_sites:
                    llm_sites.append("Claude")
                    
            if "Gemini" in title:
                if "Gemini" not in llm_sites:
                    llm_sites.append("Gemini")
                    
            if "Grok" in title:
                if "Grok" not in llm_sites:
                    llm_sites.append("Grok")
                    
    except Exception as e:
        logging.error(f"Error checking window titles: {e}")
        
    return llm_sites
