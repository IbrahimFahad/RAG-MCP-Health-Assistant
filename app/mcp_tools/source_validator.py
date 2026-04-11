from urllib.parse import urlparse

# Whitelisted trusted health domains
TRUSTED_DOMAINS = {
    # International Organizations
    "who.int",
    "paho.org",
    "unicef.org",

    # US Government & Institutions
    "cdc.gov",
    "nih.gov",
    "nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "medlineplus.gov",
    "fda.gov",
    "nhlbi.nih.gov",
    "cancer.gov",
    "diabetes.org",

    # UK Health
    "nhs.uk",
    "nice.org.uk",

    # Top Medical Centers
    "mayoclinic.org",
    "clevelandclinic.org",
    "hopkinsmedicine.org",
    "mountsinai.org",
    "ucsf.edu",
    "harvard.edu",
    "stanford.edu",
    "yale.edu",
    "yalemedicine.org",

    # Medical Journals & Publishers
    "pubmed.ncbi.nlm.nih.gov",
    "nejm.org",
    "thelancet.com",
    "jamanetwork.com",
    "bmj.com",
    "nature.com",
    "sciencedirect.com",
    "springer.com",
    "wiley.com",

    # Arabic Health Sources
    "moh.gov.sa",        # Saudi Ministry of Health
    "moh.gov.ae",        # UAE Ministry of Health
    "moh.gov.eg",        # Egypt Ministry of Health
    "hakeem.gov.sa",     # Saudi health platform
    "seha.ae",           # Abu Dhabi health
    "webteb.com",        # Arabic medical info site
    "altibbi.com",       # Arabic health platform

    # General Trusted Health Sites
    "webmd.com",
    "healthline.com",
    "medicalnewstoday.com",
    "everydayhealth.com",
    "drugs.com",
    "rxlist.com",
}

# Domain suffixes that are generally trustworthy
TRUSTED_SUFFIXES = {".gov", ".edu"}


def validate_source(url: str) -> dict:
    """
    Check if a URL is from a trusted health source.

    Returns:
        {
            "url":       str,
            "domain":    str,
            "trusted":   bool,
            "reason":    str   # why it's trusted or not
        }
    """
    if not url or not url.startswith("http"):
        return {"url": url, "domain": "", "trusted": False, "reason": "Invalid URL"}

    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        domain = netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return {"url": url, "domain": "", "trusted": False, "reason": "Could not parse URL"}

    # Check exact domain match
    if domain in TRUSTED_DOMAINS:
        return {"url": url, "domain": domain, "trusted": True, "reason": "Whitelisted domain"}

    # Check if domain ends with a trusted suffix (.gov, .edu)
    for suffix in TRUSTED_SUFFIXES:
        if domain.endswith(suffix):
            return {"url": url, "domain": domain, "trusted": True, "reason": f"Trusted suffix: {suffix}"}

    # Check if domain is a subdomain of a trusted domain
    for trusted in TRUSTED_DOMAINS:
        if domain.endswith("." + trusted):
            return {"url": url, "domain": domain, "trusted": True, "reason": f"Subdomain of {trusted}"}

    return {"url": url, "domain": domain, "trusted": False, "reason": "Domain not in trusted list"}


def filter_trusted_results(results: list[dict]) -> list[dict]:
    """
    Filter a list of search results to keep only trusted sources.
    Each result dict must have a 'url' key.
    """
    trusted = []
    for r in results:
        validation = validate_source(r.get("url", ""))
        if validation["trusted"]:
            r["source_trusted"] = True
            r["trust_reason"] = validation["reason"]
            trusted.append(r)
    return trusted
